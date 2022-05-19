import os
import logging
import pathlib
from pathlib import Path
import json
import sqlite3
import hashlib
import sys
from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

## WIP
## Check if database file exists - if not, create file based on schema.
db_path = Path('../db/mercari.sqlite3')
#if not db_path.is_file():
#    db_schema = Path('../db/items.db')
#    conn = sqlite3.connect(db_schema)
#    with open('../db/mercari.sqlite3', "w") as new_db:
#        for line in conn.iterdump():
#            new_db.write("%s\n" % line)
#    conn.close()

@app.get('/')
def root():
    return {"message": "Hello, world!"}

# GET Items endpoint - Retreive list of items from SQLite3 database
@app.get('/items')
def get_items_list():

    # Connect to database and fetch all items
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute("""
                    SELECT Items.name, Categories.name AS category, image_filename AS image
                    FROM Items
                    LEFT JOIN Categories
                    ON Items.category_id = Categories.id
                    """).fetchall()
    con.close()
    
    # Create a dictionary for each item
    list = []
    for row in rows:
        columns = row.keys()
        list.append({key: row[key] for key in columns})
    
    # Return all items
    return {"items": list}
    
    # JSON implementation (deprecated)
    #    with open("items.json", "r") as file:
    #        file_data = json.load(file)
    #        return file_data

# POST Items endpoint - Add single item to SQLite3 database
@app.post('/items')

async def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    logger.info(f"Receive item: {name}, category: {category}")
    
    # Raise exception if image file extension is not .jpg
    if not image.filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image filename does not end with .jpg")
    
    image_title = image.filename.split(".")[0].encode()
    filename_hash = hashlib.sha256(image_title).hexdigest()
    
    ### Deprecated - Filename should be hashed, not image binary.
    #   # Hash image at provided path using SHA-256
    #    with open(image.filename, "rb") as image_binary:
    #        bytes = image_binary.read()
    #        image_hash = hashlib.sha256(bytes).hexdigest()
    #        image_binary.close()
    # Save image with hashed filename in ../db/images
    # Use creation mode to avoid overwriting existing copies of same image
    
    try:
        image_binary = image.file.read()
        db_image = open(f'images/{filename_hash}.jpg', "xb")
        db_image.write(image_binary)
        db_image.close()
    except:
        logger.info("New image could not be created:", sys.exc_info()[0])
    
    # Connect to database, find category_id, insert new item, commit
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    # Use null for id value to allow persistent primary key to automatically generate
    cat_id = cur.execute("SELECT id FROM Categories WHERE name = ?", (category,)).fetchone()
    if cat_id is None:
        cur.execute("INSERT INTO Categories VALUES (null, ?)", (category,))
        cat_id = cur.execute("SELECT id FROM Categories WHERE name = ?", (category,)).fetchone()
    cur.execute("INSERT INTO Items VALUES(null, ?, ?, ?)", (name, cat_id[0], filename_hash + ".jpg"))
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
def get_item(item_id: str):

    # Connect to database and fetch items containing keyword in name or category
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # Use * to allow for schema changes (Not safe to add sensitive data to schema)
    item = cur.execute("""
                    SELECT Items.name, Categories.name AS category, image_filename AS image
                    FROM Items
                    LEFT JOIN Categories
                    ON Items.category_id = Categories.id
                    WHERE Items.id = ?
                    """, (item_id,)).fetchone()
    con.close()
    
    # Throw exception if item not found
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Return item
    return {key: item[key] for key in item.keys()}

# GET Search Items endpoint - Retrieve list of items matching keyword in SQLite3 database
@app.get('/search')
def search_items(keyword: str = Form(...)):
    
    # Connect to database and fetch items containing keyword in name or category
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute("""
                        SELECT Items.name, Categories.name AS category, image_filename AS image
                        FROM Items
                        LEFT JOIN Categories
                        ON Items.category_id = Categories.id
                        WHERE Items.name LIKE ?
                        OR category LIKE ?
                        """, ("%" + keyword + "%", "%" + keyword + "%")).fetchall()
    con.close()
    
    # Create a dictionary for each item
    list = []
    for row in rows:
        columns = row.keys()
        list.append({key: row[key] for key in columns})
    
    # Return all items
    return {"items": list}

@app.get("/image/{image_filename}")
async def get_image(image_filename):
  
    # Create image path
    image = images / image_filename

    if not image_filename.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)