from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel

app = FastAPI()

class Post(BaseModel):
    title: str
    description: str

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/createpost")
def create_post(payLoad : Post):
    print(payLoad.model_dump())
    return {"message": payLoad.model_dump()}