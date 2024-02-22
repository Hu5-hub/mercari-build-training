import os
import logging
import pathlib
import json
import hashlib
from fastapi import FastAPI, Form, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [os.environ.get("FRONT_URL", "http://localhost:3000")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Hello, world!"}

# STEP 3-3
@app.get("/items")
def get_items():
    # read the json file as dictionary
    with open("items.json", "r") as file:
        item_data = json.load(file)
    logger.info(f"Receive items: {item_data}")
    return item_data

# STEP 3-2
@app.post("/items")
async def add_item(name: str = Form(...), category: str = Form(...), image: UploadFile = File(...)):
    image_filename = await get_image_filename(image)
    item = {"name": name, "category": category, "image": image_filename}

    # read the json file as dictionary
    with open("items.json", "r") as file:
        item_data = json.load(file)

    # retrieve and append the list of items
    item_list = []
    if "items" in item_data.keys():
        item_list.append(item)
    else: 
        # inittilize an empty list if it doesn't exist
        item_list.append([])
    
    # write the json file
    with open("items.json", "w") as file:
        json.dump({"items": item_list}, file)
        
    logger.info(f"Receive item: {name}, {category}, {image_filename}")
    return {"message": f"item received: {name}, {category}, {image_filename}"}

# STEP 3-5
@app.get("/items/{item_id}")
def get_item_id(item_id: int):
    with open("items.json", "r") as file:
        item_data = json.load(file)

    # check if item_id is a valid index
    if 1 <= item_id < len(item_data[("items")]) + 1:
        item = item_data["items"][item_id - 1]
        logger.info(f"Receive item: {item}")
        return item
    else:
        raise HTTPException(status_code=404, detail="Item not found")

# STEP 3-4
async def get_image_filename(image):
    image_hash = hashlib.sha256(await image.read()).hexdigest()
    image_filename = f"{image_hash}.jpg"

    logger.info(f"Received image: {image_filename}")
    return image_filename


@app.get("/image/{image_name}")
async def get_image(image_name):
    # Create image path
    image = images / image_name

    if not image_name.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
