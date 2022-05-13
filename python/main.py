import os
import logging
import pathlib
import json
import sqlite3
import hashlib
import sys
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.get('/')
def root():
    return {"message": "Hello, world!"}

# GET Items endpoint - Retreive list of items from SQLite3 database
@app.get('/items')
def get_items_list():

    # Connect to database and fetch all items
    con = sqlite3.connect('../db/mercari.sqlite3')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # Use * to allow for schema changes (Not safe to add sensitive data to schema)
    rows = cur.execute("SELECT * FROM Items").fetchall()
    con.close()
    
    # Create a dictionary for each item, omitting ID
    list = []
    for row in rows:
        columns = row.keys()
        columns.remove("id")
        list.append({key: row[key] for key in columns})
    
    # Return all items
    return {"items": list}
    
    # JSON implementation (deprecated)
    #    with open("items.json", "r") as file:
    #        file_data = json.load(file)
    #        return file_data

# POST Items endpoint - Add single item to SQLite3 database
@app.post('/items')
def add_item(name: str = Form(...), category: str = Form(...), image: str = Form(...)):
    logger.info(f"Receive item: {name}, category: {category}")
    
    # Raise exception if image file extension is not .jpg
    if not image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")
    
    # Hash image at provided path using SHA-256
    with open(image, "rb") as image_file:
        bytes = image_file.read()
        image_hash = hashlib.sha256(bytes).hexdigest()
        image_file.close()
        
    # Save image with hash as filename in ../db/images
    # Use creation mode to avoid overwriting existing copies of same image
    try:
        db_image = open(f'../db/images/{image_hash}.jpg', "xb")
        db_image.write(bytes)
        db_image.close()
    except:
        logger.info("New image creation failure:", sys.exc_info()[0])
    
    # Connect to database, insert new item, commit
    con = sqlite3.connect('../db/mercari.sqlite3')
    cur = con.cursor()
    # Use null for id value to allow persistent primary key to automatically generate
    cur.execute(f"INSERT INTO Items VALUES(null, \"{name}\", \"{category}\", \"{image_hash}.jpg\")")
    con.commit()
    con.close()
    
    # Return accepted item message
    return {"message": f"item received: {name}, category: {category}"}
    
    # JSON implementation (deprecated)
    #    dictionary = {
    #        "name": name,
    #        "category": category
    #    }
    #
    #    with open("items.json", "r+") as file:
    #        file_data = json.load(file)
    #        file_data["items"].append(dictionary)
    #        file.seek(0)
    #        json.dump(file_data, file, indent = 4)
    
    
# GET Item by ID endpoint - Retrieve item by id number
@app.get('/items/{item_id}')
def get_item(item_id: int):

    # Connect to database and fetch items containing keyword in name or category
    con = sqlite3.connect('../db/mercari.sqlite3')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # Use * to allow for schema changes (Not safe to add sensitive data to schema)
    item = cur.execute(f"""
                    SELECT * FROM Items
                    WHERE id = {item_id}
                    """).fetchone()
    con.close()
    
    # Throw exception if item not found
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Omit ID
    columns = item.keys()
    columns.remove("id")
    
    # Return all items
    return {key: item[key] for key in columns}

# GET Search Items endpoint - Retrieve list of items matching keyword in SQLite3 database
@app.get('/search')
def search_items(keyword: str = Form(...)):
    
    # Connect to database and fetch items containing keyword in name or category
    con = sqlite3.connect('../db/mercari.sqlite3')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # Use * to allow for schema changes (Not safe to add sensitive data to schema)
    rows = cur.execute(f"""
                        SELECT * FROM Items
                        WHERE name LIKE \"%{keyword}%\"
                        OR category LIKE \"%{keyword}%\"
                        """).fetchall()
    con.close()
    
    # Create a dictionary for each item, omitting ID
    list = []
    for row in rows:
        columns = row.keys()
        columns.remove("id")
        list.append({key: row[key] for key in columns})
    
    # Return all items
    return {"items": list}


@app.get('/image/{items_image}')
async def get_image(items_image):
    # Create image path
    image = images / items_image

    if not items_image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
