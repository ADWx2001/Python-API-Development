from fastapi import FastAPI,Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange #imported for gennerate random numbers
import psycopg2
from psycopg2.extras import RealDictCursor
from .import models
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
import time

models.Base.metadata.create_all(bind=engine) #this create all the models when start run the main file, sqlalchemy

app = FastAPI()

# this is used for sqlalchemy
def get_db():
    db = SessionLocal() #session object is the thing that call with databses
    try:
        yield db
    finally:
        db.close()

@app.get("/sqlalchemy")
def test_post(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"status":posts}


class Post(BaseModel):
    title: str
    content: str
    published: bool = True

#connecting to databse locally
# try:
#     conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='ASAnka119@', cursor_factory=RealDictCursor)
#     cursor = conn.cursor()
#     print("Database connection successfull!")
# except Exception as error:
#     print(f"Connecting to databse Unsuccessfull, caused this {error}")



my_posts = [{"title":"Post 1 title", "content":"Post 1 content", "id":"1"},{"title":"Post 1 title", "content":"Post 1 content", "id":"2"}]

@app.get("/")
async def read_root():
    return {"Hello": "World"}

#retrieve all the posts
@app.get("/getposts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}

#create a new post
@app.post("/createpost", status_code=status.HTTP_201_CREATED) #this status code is the suitable for creating records 
def create_post(post : Post, db: Session = Depends(get_db)):
    # print(payLoad.model_dump())
    # post_dict = payLoad.model_dump()  #convert the incoming reqest data to dictionary type
    # post_dict['id'] = randrange(0,100000) #add randomm number as id to the post_dict dictionary type variable.
    # my_posts.append(post_dict) #save the data to my_posts dictinary type

    #this down below is sql query using the psycog2 library 
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #                  (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()

    # this below code is using sqlalchemy library
    # new_post = models.Post(title=post.title, content=post.content, published=post.published) 
    # if we have 50 entriens in the coming request  we have to seperate all it line in above code and it not efficient we use this instead of
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit() # every changes need to be commit to the database otherwise it's not gonna save to the database
    db.refresh(new_post) #use for get the result of newly created post earlier we use RETURNING * keyword this method is used for that
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
def get_post(id : int, db: Session = Depends(get_db)): #validating the id is integer or not
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s""", (str(id)))
    # post = cursor.fetchone()
    # print(post)
    #post = find_post(id)

    # top code is used by psycog2 and below code sqlalchmey
    post = db.query(models.Post).filter(models.Post.id == id).first() # used first for send back fist record that postgre found otherwise use .all() can waste the resource because after found a record it going to be find all the records that matched that id  
    if not post:
        # respose.status_code = status.HTTP_404_NOT_FOUND
        # return {"message":"post with this id is not found"}

        #without hardcoding everything we can do throw an httpexception
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} was not found ")
    return {"Post detail": post}

#delete a post from dictionary
#need the id od the post in dictionary then pop the id
@app.delete("/deletepost/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id,db: Session = Depends(get_db)):
    # #index = find_post_dic_id(id)
    # cursor.execute("""delete from posts where id = %s returning *""", (str(id),))
    # delete_post = cursor.fetchone()
    # conn.commit()

    # top code is using psycog2 and below code is sqlalchemy
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id} was not found ")
    #my_posts.pop(index)

    post.delete(synchronize_session=False)
    db.commit()
    return {"message": "post was deleted"}



@app.put("/update/{id}")
def update_post(id : int, post_updated :Post,db: Session = Depends(get_db)):
    # cursor.execute(""" UPDATE posts set title=%s, content=%s, published=%s WHERE id =%s RETURNING *""",
    # (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    # index = find_post_dic_id(id)

    #this below is sql alchemy code
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id:{id}")
    # post_dict = post.dict()
    # post_dict['id'] = id
    # my_posts[index] = post_dict

    post_query.update(post_updated.model_dump(), synchronize_session=False)
    db.commit()
    return {"message": post_query.first()}
