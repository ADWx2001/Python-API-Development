from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange #imported for gennerate random numbers

app = FastAPI()

class Post(BaseModel):
    title: str
    description: str

my_posts = [{"title":"Post 1 title", "content":"Post 1 content", "id":"1"}]

@app.get("/")
async def read_root():
    return {"Hello": "World"}

#retrieve all the posts
@app.get("/getposts")
def get_posts():
    return {"data": my_posts}

#create a new post
@app.post("/createpost")
def create_post(payLoad : Post):
    print(payLoad.model_dump())
    post_dict = payLoad.model_dump()  #convert the incoming reqest data to dictionary type
    post_dict['id'] = randrange(0,100000) #add randomm number as id to the post_dict dictionary type variable.
    my_posts.append(post_dict) #save the data to my_posts dictinary type
    return {"Data": post_dict}

#get only one post
@app.get("/getpost/{id}")
def get_post(id):
    for post in my_posts:
        if post["id"] == id:
            return {"post_details": post}
