from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from PersonOfInterest import PersonOfInterest

app = FastAPI()
POI = PersonOfInterest()

app.get("/search")
async def search(query: str, sim_score: float, results: int):
    res = POI.semantic_search(
        query=query, 
        sim_score=sim_score,
        results=results
    )
    # json format
    return [{"score": r.score, 'image_url': r.payload['image_path']} for r in res]

