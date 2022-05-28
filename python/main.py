import os
import logging
import pathlib
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

# Assign database path
db_path = pathlib.Path('../db/mercari.sqlite3')

# On startup, initialize database if it does not exist
@app.on_event("startup")
def startup_event():
    if not db_path.is_file():
        db_schema = open(pathlib.Path('../db/items.db'), "r")
        schema = db_schema.read()
        db_schema.close()
        con = sqlite3.connect(db_path)
        cur = con.cursor()
        cur.executescript(schema)
        con.commit()
        con.close()

@app.get('/')
def root():
    return {"message": "Simple Mercari API Root Directory"}

# GET Items endpoint - Retreive list of items from SQLite3 database
@app.get('/items')
def get_items_list():

    # Connect to database and fetch all items
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute("""
                    SELECT item_id AS id,
                            item_name AS name,
                            category_name AS category,
                            item_image_filename AS image
                    FROM Items
                    LEFT JOIN Categories
                    USING (category_id)
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
    cur.execute("INSERT OR IGNORE INTO Categories VALUES (null, ?)", (category,))
    cat_id = cur.execute("SELECT category_id FROM Categories WHERE category_name = ?", (category,)).fetchone()
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
                    SELECT item_name AS name, category_name AS category, item_image_filename AS image
                    FROM Items
                    LEFT JOIN Categories
                    USING (category_id)
                    WHERE item_id = ?
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
                        SELECT item_name AS name, category_name AS category, item_image_filename AS image
                        FROM Items
                        LEFT JOIN Categories
                        USING (category_id)
                        WHERE name LIKE ?
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
        logger.info(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)

@app.get('/drafts')
def get_items_list():
    # Connect to database and fetch all items
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = cur.execute("""
                    SELECT Drafts.draft_id AS id,
                            Drafts.sort_index,
                            Drafts.item_name AS name,
                            Drafts.item_image_filename AS image,
                            Categories.category_name AS category,
                            Item_State.state AS state,
                            Drafts.description AS description,
                            Delivery.delivery_method AS delivery,
                            Drafts.price AS price
                    FROM Drafts
                    LEFT JOIN Categories USING (category_id)
                    LEFT JOIN Item_State USING (item_state_id)
                    LEFT JOIN Delivery USING (delivery_method_id)
                    """).fetchall()
    con.close()

    # Create a dictionary for each item
    list = []
    for row in rows:
        columns = row.keys()
        list.append({key: row[key] for key in columns})

    # Return all items
    return {"draft items": list}

# POST request to post a single item to the drafts table in SQLite3 database
@app.post('/drafts')
async def add_draft(item_name: str = Form(...), image: UploadFile = File(...),
category: str = Form(...), item_state_id: int = Form(...), description: str = Form(...),
delivery_id: int = Form(...), price: int = Form(...)):
    try:
        image_binary = image.file.read()
        db_image = open(f'draft_images/{image.filename}', "xb")
        db_image.write(image_binary)
        db_image.close()
    except:
        logger.info("New image could not be created:", sys.exc_info()[0])

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    # Use null for id value to allow persistent primary key to automatically generate
    cur.execute("INSERT OR IGNORE INTO Categories VALUES (null, ?)", (category,))
    cat_id = cur.execute("SELECT category_id FROM Categories WHERE category_name = ?", (category,)).fetchone()[0]
    params = (item_name, image.filename, cat_id, item_state_id, description, delivery_id, price,)
    cur.execute("""INSERT INTO Drafts (item_name, item_image_filename, category_id, item_state_id,
     description, delivery_method_id, price)
     VALUES (?, ?, ?, ?, ?, ?, ?)
     """, params)
    con.commit()
    con.close()

    # Return accepted item message
    return {"message": f"item received in drafts: {item_name}, category: {category}, image_filename: {image.filename}"}

# GET request to obtain the info a single item in the drafts table by inputting draft_id
@app.get('/drafts/{draft_id}')
def get_draft(draft_id: int):
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    # Use * to allow for schema changes (Not safe to add sensitive data to schema)
    item = cur.execute("""
                    SELECT Drafts.draft_id AS id,
                            Drafts.sort_index,
                            Drafts.item_name AS name,
                            Drafts.item_image_filename AS image,
                            Categories.category_name AS category,
                            Item_State.state AS state,
                            Drafts.description AS description,
                            Delivery.delivery_method AS delivery,
                            Drafts.price AS price
                    FROM Drafts
                    LEFT JOIN Categories USING (category_id)
                    LEFT JOIN Item_State USING (item_state_id)
                    LEFT JOIN Delivery USING (delivery_method_id)
                    WHERE id = ?
                    """, (draft_id,)).fetchone()
    con.close()

    # Throw exception if item not found
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Return item
    return {key: item[key] for key in item.keys()}

# DELETE request which deletes a single item from the drafts table by inputting draft_id
@app.delete("/drafts/{draft_id}")
def delete_draft_item(draft_id: int):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("DELETE FROM Drafts WHERE draft_id = (?)", (draft_id,))
    con.commit()
    con.close()
