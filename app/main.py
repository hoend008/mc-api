from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import country, sample, user, auth

app = FastAPI(
  title="title API",
  description="A beautiful API",
  summary="API doing stuff",
  version="0.0.1",
  contact={
        "name": "Wouter Hoenderdaal",
        "email": "wouter.hoenderdaal@wur.nl",
  },
)

origins = [
    "*",
    #"http://localhost",
    #"http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(country.router)
app.include_router(sample.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}