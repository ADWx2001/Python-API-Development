from fastapi import FastAPI,Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange #imported for gennerate random numbers
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True

#connecting to databse locally
try:
    conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='ASAnka119@', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Database connection successfull!")
except Exception as error:
    print(f"Connecting to databse Unsuccessfull, caused this {error}")



my_posts = [{"title":"Post 1 title", "content":"Post 1 content", "id":"1"},{"title":"Post 1 title", "content":"Post 1 content", "id":"2"}]

@app.get("/")
async def read_root():
    return {"Hello": "World"}

#retrieve all the posts
@app.get("/getposts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts = cursor.fetchall()
    return {"data": posts}

#create a new post
@app.post("/createpost", status_code=status.HTTP_201_CREATED) #this status code is the suitable for creating records 
def create_post(post : Post):
    # print(payLoad.model_dump())
    # post_dict = payLoad.model_dump()  #convert the incoming reqest data to dictionary type
    # post_dict['id'] = randrange(0,100000) #add randomm number as id to the post_dict dictionary type variable.
    # my_posts.append(post_dict) #save the data to my_posts dictinary type

    cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
                     (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"Data": new_post}

#function to find the post
def find_post(id):
    for post in my_posts:
        if post["id"] == id:
            return post

def find_post_dic_id(id):
    for i, post in enumerate(my_posts): #use enumerate for grab the id of the post
        if post['id'] == id:
            return i

#an example for the order matter
@app.get("/getpost/latest")
def get_latest_post():
    return {"post_details": my_posts[len(my_posts)-1]} 
#Fast api is not going to come to this function because in top of there a url pattern similar to this "/getpost/some variable" 
# and it going to that function anw server run in to error ti fix that we can push this function to up |^

#get only one post
@app.get("/getpost/{id}")
def get_post(id : int, respose : Response): #validating the id is integer or not
    post = find_post(id)
    if not post:
        # respose.status_code = status.HTTP_404_NOT_FOUND
        # return {"message":"post with this id is not found"}
        #without hardcoding everything we can do throw an httpexception
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} was not found ")
    return {"Post detail": post}

#delete a post from dictionary
#need the id od the post in dictionary then pop the id
@app.delete("/deletepost/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id):
    index = find_post_dic_id(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} was not found ")
    my_posts.pop(index)
    return {"message": "post was deleted"}


@app.put("/update/{id}")
def update_post(id : int, post :Post):
    index = find_post_dic_id(id)
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id}")
    post_dict = post.dict()
    post_dict['id'] = id
    my_posts[index] = post_dict
    return {"message": "post was updated"}
