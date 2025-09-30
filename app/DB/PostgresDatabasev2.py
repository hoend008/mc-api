import psycopg2
import numpy as np
import pandas as pd
import os
from typing import List, Dict, Set
psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)
from psycopg2.extras import RealDictCursor
from datetime import date
from dataclasses import dataclass
from DFdiffChecker import ColumnChecker, ValueDifferences, ValueChecker

@dataclass
class DbColumns:
    missing_columns: Set
    db_columns: List
  
@dataclass
class ProcessedFK:
    mistakes: bool
    data: pd.DataFrame

    
"""
example usecase

with PostgresDatabase('owfsr', DB_USER, DB_PASSWORD) as db:
    sqlquery = "SELECT * FROM ontologies.country;"
    df_country = db.querydf(sqlquery)
    
"""

class PostgresDatabase:
    def __init__(self, db_name, db_user, db_password, host="opostgres16.cdbe.wurnet.nl", realdictcursor=False):
        
        if not realdictcursor:
            self.connection = psycopg2.connect(user = db_user,
                                            password = db_password,
                                            host = host,
                                            port = "5432",
                                            database = db_name)
            self.cursor = self.connection.cursor()
        else:
            self.connection = psycopg2.connect(user = db_user,
                                            password = db_password,
                                            host = host,
                                            port = "5432",
                                            database = db_name,
                                            cursor_factory=RealDictCursor)
            self.cursor = self.connection.cursor()            

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def commit(self):
        self.connection.commit()
    
    def rollback(self):
        self.connection.rollback()
            
    def close(self, commit=True):
        if commit:
            self.commit()
        self.cursor.close()
        self.connection.close()

    def execute(self, sql: str, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql: str, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()

    def querydf(self, sql: str) -> pd.DataFrame:
        return pd.read_sql_query(sql, self.connection)
    
    def dumpdf(self, df, tablename):
        df.to_sql(tablename, self.connection)
    
    def columnnames_identical(self, schema: str, tbl: str, df_columns: List[str]) -> DbColumns:
        
        # get columnnames from table with essential columns
        db_columns = self.query(f"SELECT column_name FROM information_schema.columns WHERE table_schema = '{schema}' AND table_name = '{tbl}' AND column_name NOT IN ('id', 'created_at');")
        # convert to list
        db_columns = [x[0] for x in db_columns]
        
        # check if the columns in the dataframe are all present in the database
        column_info = ColumnChecker(df_columns, db_columns)
        missing_cols = column_info.rightcols
        
        return DbColumns(missing_cols, db_columns)
   
    def export_excel(self, query: str, filename: str, dir_name: str=None):
        
        # get data
        df = self.querydf(query)
        
        # create filename and create fullpath
        base_filename = f"{filename}_{date.today()}.xlsx"
        if dir_name:
            fullpath = os.path.join(dir_name, base_filename)
        else:
            fullpath = os.path.join(os.getcwd(), base_filename)
        
        # export and print some output
        df.to_excel(fullpath, index=False)
        
        print(f"Destination: {fullpath}")
        print(f"Exported {df.shape[0]} rows and {df.shape[1]} columns")
        
    def check_foreign_keys(self, df_series: pd.Series, tbl_name: str, colname: str) -> List:
        
        # get values
        db_values = self.query(f"SELECT {colname} FROM {tbl_name} GROUP BY {colname};")
        db_values = [x[0] for x in db_values]
        
        # search for values in df_series that are not in list_values
        return list(set(set(df_series) - set(db_values)))
    
    def get_foreign_keys(self, df: pd.DataFrame, refs: Dict) -> ProcessedFK:
        # convert labels to id's
        # ref has the column and table name(s)
        mistakes = False
        for tblname, colnames in refs.items():
            reftbl = tblname
            colname_df = colnames['df']
            colname_tblref = colnames['tblref']
            
            # check if all values in colname_df are also in the database. Remove nan's
            invalid_values = self.check_foreign_keys(df[colname_df], reftbl, colname_tblref)
            invalid_values = [x for x in invalid_values if x == x and x != None]
            if len(invalid_values) > 0:
                print("Foreign key value error")
                print(f"In df[{colname_df}] are values that are not in the database")
                for x in set(invalid_values):
                    print(x)
                mistakes = True
            else:            
                # get id's from db
                tbl_labels_id = dict(self.query(f"SELECT {colname_tblref}, id FROM {reftbl};"))
                # create list of values to be replaced, create dictionary from db for lookup, replace (ignore nan)
                df = df.replace({colname_df: tbl_labels_id})

        return ProcessedFK(mistakes, df)
  
    #def explore_diffs(self, df: pd.DataFrame, tbl_name: str, identifiers: List[str], refs: Dict = None, ignore_column_updates: List[str] = None) -> ValueDifferences:
    def explore_diffs(self, df: pd.DataFrame, tbl_name: str, identifiers: List[str], refs: Dict = None) -> ValueDifferences:   
        """
        Explore differences between a dataframe and the corresponding table in the database
        """

        # check datatypes of empty columns and if nessecary convert them from objects to floats
        df = self.check_datatypes_empty_columns(df, tbl_name)
        
        # get data from DB
        tbl_in_db = self.querydf(f"SELECT * FROM {tbl_name};")        
        # check datatypes of empty columns and if nessecary convert them from objects to floats
        tbl_in_db = self.check_datatypes_empty_columns(tbl_in_db, tbl_name)
        
        # remove id column
        if 'id' in tbl_in_db.columns:
            tbl_in_db = tbl_in_db.drop(['id'], axis=1)
      
        # get foreign key values
        if refs:
            processed_foreignkeys = self.get_foreign_keys(df, refs)
            if processed_foreignkeys.mistakes:
                print("Incorrect data, see FK error messages above")
                return
            else:
                df = processed_foreignkeys.data
        
        # find differences
        diffs = ValueChecker(df, tbl_in_db, identifiers)
        return diffs.find_differences()
      
    def insert_update(self, 
                      i_df: pd.DataFrame, 
                      tbl_name: str, 
                      skip_existing: List[str] = None, 
                      update_existing: List[str] = None, 
                      logfunction: str = None, 
                      refs: Dict = None, 
                      auto_commit: bool = True, 
                      text_output: bool = True):
    
        """
        This function imports data in the db. New rows are inserted, if foreign keys are used, use the refs input
        In case you want to update rows that already exist, use the update_existing. If you do not want to update
        the values in the existing row but are using dates instead, add a date_var.
        If you only want to add new rows, use skip_existing.
        
        Inputs:
            i_df = dataframe to import. MAKE SURE ALL COLUN NAMES ARE IDENTICAL TO THOSE IN DB
            tbl_name = name of table in DB
            skip_exising = list of columns that makes a row unique. Do this when you want to skip inserting rows 
                            that already exist in DB (based on columns that make a row unique)
            update_existing = list of columns that makes a row unique. Do this when you want to update the rows that already exist in DB
            log_updates = If True, this calls the function ontologies.fnc_logchanges which stores the updated values (old + new) 
                          in the table ontologies.logchanges
            refs = dictionary used to get foreign key information. Input is column_name to be update, table with primary key
                e.g. refs = {'feed.stof_naam_engels' : {'df':'stof_naam_engels', 'tblref':'stof_naam_engels_id'}}
        """
        
        """
        CHECKS and FOREIGN KEY PROCESSING
        """
        # some checks on the input
        if skip_existing and update_existing:
            print("Faulty input. skip_existing and update_existing cant both have values. Import aborted.")
            return
  
        # check datatypes of empty columns and if nessecary convert them from objects to floats
        i_df = self.check_datatypes_empty_columns(i_df, tbl_name)
        
        # split schema and tbl name
        schema, tbl = tbl_name.split('.')
        
        # check if columnnames in i_df and the DB table are identical
        columns_info = self.columnnames_identical(schema, tbl, i_df.columns)
        if len(columns_info.missing_columns) > 0:
            print("Columns in dataframe and in DB table are not identical. Insert aborted. These columns are missing in the dataframe:")
            for x in columns_info.missing_columns:
                print(x)
            return
        
        # get only the columns from i_df that are also in the database
        # create a list (db_columns) and a comma-separated string (db_columnnames)
        db_columns = columns_info.db_columns
        db_columnnames = ', '.join(["{}".format(value) for value in db_columns])
        
        # convert values into foreign keys
        if refs:
            processed_foreignkeys = self.get_foreign_keys(i_df, refs)
            if processed_foreignkeys.mistakes:
                print("Incorrect data, see FK error messages above")
                return
            else:
                i_df = processed_foreignkeys.data
        
        """
        LOOP OVER DATAFRAME AND INSERT/UPDATE
        """
        # make count variables for output
        count_insert = 0
        count_update = 0
        count_skipped = 0
        
        # when existing rows are going to be updated or when existing rows have to be skipped, 
        # get the existing data from the DB
        if update_existing or skip_existing:
            df_existing = self.querydf(f"SELECT * FROM {tbl_name};") 
            
            # check datatypes of empty columns and if nessecary convert them from objects to floats 
            df_existing = self.check_datatypes_empty_columns(df_existing, tbl_name)

            # make a dataframe with only the new rows (skip_existing)
            # or (update_existing)
            # make a dataframe with the values to be updated and a dataframe with only the new rows
            if skip_existing:
                i_df = self.get_leftrows(i_df, df_existing, skip_existing)
            elif update_existing:
                df_differences = ValueChecker(i_df, df_existing, update_existing, pgdb=True)
                df_differences = df_differences.find_differences()
                df_update_values = df_differences.diffs
                i_df = self.get_leftrows(i_df, df_existing, update_existing)
        
        # get all values
        try:
            for index, row in i_df.iterrows():
                insert_values = dict(row[db_columns])
                insert_values = {key : value if pd.notnull(value) else None for key, value in insert_values.items()}
                # insert values
                self.execute(f"INSERT INTO {tbl_name}(" + db_columnnames + ") VALUES (" + "%s," * (len(insert_values)-1) + "%s)" , list(insert_values.values()))
                count_insert += 1
            
            if update_existing:
                count_update = self.update_differences_by_rowid(df_update_values, tbl_name, logfunction)                           
                
        except (Exception, psycopg2.DatabaseError) as dberror:
            print('DB error: Rollback executed')
            print(dberror)
            self.rollback()
            
        except:
            print('other error')
            pass
            
        else:
            # if auto_commit = False, ask user what to do (commit or rollback). Else just commit.
            if not auto_commit:
                while True:
                    self.insert_update_output(i_df.shape[0], count_insert, count_update, count_skipped)
                    i_commit = input('Do you want to autocommit? [y/n]:')
                    if i_commit.lower() == 'y':
                        print('Committed to DB')
                        self.commit()
                        break
                    elif i_commit.lower() == 'n':
                        print('Rollback executed')
                        self.rollback()
                        break
            else:            
                if text_output:
                    print('Committed to DB')
                self.commit()
            
        finally:
            if text_output:
                print('Closed DB connection')
                self.insert_update_output(i_df.shape[0], count_insert, count_update, count_skipped)
                # self.close(commit=False)
    

    def update_differences_by_rowid(self, df_update_values: pd.DataFrame, tbl_name: str, logfunction: str = None) -> int:
        
        # split schema and tbl_name
        schema, tbl = tbl_name.split('.')
        # get datatypes from the columns
        db_datatypes = self.querydf(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '{schema}' AND table_name = '{tbl}';")
        
        update_columns = ['id', 'variable', 'value_x', 'value_y']
        
        # get original row data for insert query              
        count_update = 0
        
        list_ids = list(set(df_update_values['id']))

        for ID in list_ids:

            tmp_updated_values = df_update_values.query("id == @ID")
                        
            update_query = f"UPDATE {tbl_name} SET "

            for index, row in tmp_updated_values.iterrows():
                # make a dict with values to update
                update_values = dict(row[update_columns])
            
                # get datatype belonging to variable
                datatype = db_datatypes.loc[db_datatypes['column_name'] == update_values['variable'], 'data_type'].item()
                                    
                # create and execute queries
                # if date_var, then only create an update query for the date.
                # else, create an update query to update the value in the existing row
                
                if pd.isnull(update_values['value_x']):
                    #update_query = f"UPDATE {tbl_name} SET {update_values['variable']} = NULL WHERE id = {update_values['id']};"
                    update_query = update_query + f"{update_values['variable']} = NULL,"
                else:
                    if datatype in ['integer', 'numeric', 'decimal', 'boolean']:
                        #update_query = f"UPDATE {tbl_name} SET {update_values['variable']} = {update_values['value_x']} WHERE id = {update_values['id']};"
                        update_query = update_query + f"{update_values['variable']} = {update_values['value_x']},"
                    else:
                        # add quote in case of single quote
                        if datatype not in ['date']:
                            update_values['value_x'] = update_values['value_x'].replace("'", "''")
                        #update_query = f"UPDATE {tbl_name} SET {update_values['variable']} = '{update_values['value_x']}' WHERE id = {update_values['id']};"
                        update_query = update_query + f"{update_values['variable']} = '{update_values['value_x']}',"
            
            update_query = update_query[:-1]
            update_query = update_query + f" WHERE id = {ID};"
        
            #print(update_query)
            
            # update
            if '%' in update_query:
                update_query = update_query.replace('%', '%%')
                            
            self.execute(update_query)
            count_update += 1
            
            # log changes
            if logfunction:
                log_query = f"SELECT * FROM {logfunction}('{tbl_name}', '{update_values['variable']}',{update_values['id']}, '{update_values['value_y']}', '{update_values['value_x']}');"
                self.execute(log_query)

        return count_update          
    
    def check_datatypes_empty_columns(self, df: pd.DataFrame, tbl_name: str) -> pd.DataFrame:
        
        # check if there are empty columns in df
        empty_columns = []
        nr_rows = df.shape[0]
        for col in df.columns:
            if sum(df[col].isna()) == nr_rows:
                empty_columns.append(col)
        
        # check the datatypes of those empty columns
        if len(empty_columns) > 0:            
            # split schema and tbl_name
            schema, tbl = tbl_name.split('.')
            # get datatypes from the columns
            db_datatypes = self.querydf(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '{schema}' AND table_name = '{tbl.lower()}';")
            
            # compare datatypes
            for col in empty_columns:
                datatype_db = db_datatypes.query("column_name == @col")["data_type"].item()
                datatype_df = str(df[col].dtypes)
                if datatype_df == 'object' and datatype_db in ['integer', 'numeric', 'decimal']:
                    df[col] = df[col].astype(float)
                    
        return df
        
    @staticmethod
    def get_leftrows(df1, df2, identifiers):
        df = df1.merge(df2[identifiers], on=identifiers, how='left', indicator='Exist')
        return df[df[ 'Exist' ] == 'left_only']        
        
        
    @staticmethod
    def insert_update_output(i_rows, count_insert, count_update, count_skipped):
        print('Closed DB connection')
        print(f"Dataframe nr rows:  {i_rows}")
        print(f"Nr rows inserted:   {count_insert}")
        print(f"Nr rows updated:    {count_update}")
        print(f"Nr rows skipped:    {count_skipped}")
        
    @staticmethod
    def hello():
        print("Hello")

