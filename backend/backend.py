from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from PersonOfInterest import PersonOfInterest
import os
app = FastAPI()
POI = PersonOfInterest()

IMAGES_DIR = os.path.join(os.getenv("FOLDER_PATH") or os.getcwd(), "cropped_images")
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

@app.get("/search")
async def search(query: str, sim_score: float, results: int):
    res = POI.semantic_search(
        query=query, 
        sim_score=sim_score,
        results=results
    )
    # json format
    return [{"score": r.score, 'image_url': "/images/" + os.path.basename(r.payload['image_path'])} for r in res]

