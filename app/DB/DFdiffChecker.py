# -*- coding: utf-8 -*-
"""
Created on Mon May 16 11:54:59 2022

@author: hoend008
"""

from typing import List, Set
import pandas as pd


class ColumnChecker:
    
    def __init__(self, df1_columns: List[str], df2_columns: List[str]):
        self.df1_columns = df1_columns
        self.df2_columns = df2_columns
        self.leftcols = set(self.df1_columns) - set(self.df2_columns)
        self.rightcols = set(self.df2_columns) - set(self.df1_columns)
        
    def __str__(self):
        return f"""
        cols in left and not in right {'' if len(self.leftcols) == 0 else self.leftcols}
        cols in right and not in left {'' if len(self.rightcols) == 0 else self.rightcols}
        """
        
class ValueDifferences:
    
    def __init__(self, 
                 leftrows: pd.DataFrame,
                 rightrows: pd.DataFrame,
                 diffs: pd.DataFrame,
                 leftcols: Set[str] = None,
                 rightcols: Set[str] = None):
        
        self.leftcols = leftcols
        self.rightcols = rightcols
        self.leftrows = leftrows
        self.rightrows = rightrows
        self.diffs = diffs

    def __str__(self):
        
        return f"""
        cols in left and not in right {'' if len(self.leftcols) == 0 else self.leftcols}
        cols in right and not in left {'' if len(self.rightcols) == 0 else self.rightcols}
        number of rows in left and not in right... {self.leftrows.shape[0]}
        number of rows in right and not in left... {self.rightrows.shape[0]}
        number of rows with differences........... {self.diffs.shape[0]}
        """
    
class ValueChecker:
    
    """
    This class takes two dataframes and returns the differences as a DataframeDifferences
    """
    
    def __init__(self, df1: pd.DataFrame, df2: pd.DataFrame, identifiers: List[str], pgdb: bool = False, ignore_column_updates: List[str] = None):
        self.df1 = df1
        self.df2 = df2
        self.pgdb = pgdb
        self.ignore_column_updates = ignore_column_updates
        # convert identifiers to list if nessecary
        if not isinstance(identifiers, list):
            self.identifiers = [identifiers]
        else:
            self.identifiers = identifiers
    
    @staticmethod        
    def diff_values(df1: pd.DataFrame, df2: pd.DataFrame, identifiers: List[str], pgdb: bool = None, ignore_column_updates: List[str] = None) -> pd.DataFrame:
        
        # convert both dataframes to long format based on identifiers
        # pgdb refers to usage in database class, for which 'id' column is needed for updating values
        df1_l = pd.melt(df1, id_vars=identifiers)
        if pgdb:
            df2_l = pd.melt(df2, id_vars=identifiers + ['id'])
        else:
            df2_l = pd.melt(df2, id_vars=identifiers)
            
        # merge both long format df's based on identifiers + new column 'variable'
        df1_2 = df1_l.merge(df2_l, on = identifiers + ['variable'])
        
        # create filter to only select rows that are different and return result
        filt = ((df1_2['value_x'] != df1_2['value_y']) & (pd.notnull(df1_2['value_x']) | pd.notnull(df1_2['value_y'])))
        df1_2 = df1_2.loc[filt]
        
        # remove rows from variables that can be ignored
        if ignore_column_updates:
            df1_2 = df1_2.query("variable != @ignore_column_updates")
        return df1_2

    def find_differences(self) -> ValueDifferences:

        """
        a function that takes in 2 dataframes
        0) checks if columns are identical
        1) returns the rows in the left that are not in the right
        2) returns the rows in the right that are not in the left
        3) the differences in rows that are both in left and right
        """        
        
        ### check columns
        column_info = ColumnChecker(self.df1.columns, self.df2.columns)
        leftcols = column_info.leftcols
        rightcols = column_info.rightcols
        
        ### rows in left that are not in right
        df_leftrows = self.df1.merge(self.df2[self.identifiers], on=self.identifiers, how='left', indicator='left_exist')
        filt_left = (df_leftrows['left_exist'] != 'both')
        df_leftrows = df_leftrows.loc[filt_left]
 
        ### rows in left that are not in right
        df_rightrows = self.df2.merge(self.df1[self.identifiers], on=self.identifiers, how='left', indicator='right_exist')
        filt_left = (df_rightrows['right_exist'] != 'both')
        df_rightrows = df_rightrows.loc[filt_left]
    
        ### rows that are in left and right but have different values in the same columns
        df_differences = self.diff_values(self.df1, self.df2, self.identifiers, self.pgdb, self.ignore_column_updates)
        return ValueDifferences(df_leftrows, 
                                df_rightrows, 
                                df_differences, 
                                leftcols, 
                                rightcols)
    
