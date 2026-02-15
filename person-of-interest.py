import streamlit as st
# from deepface import DeepFace
import math
import numpy as np
import torch
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from PIL import Image, ImageDraw
import glob
import os
from folder_path import FOLDER_PATH, HF_TOKEN

st.title("Person of Interest")

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_NUM_INTEROP_THREADS"] = "1"
os.environ["TF_NUM_INTRAOP_THREADS"] = "1"
os.environ["HF_TOKEN"] = HF_TOKEN

qdrant_client = QdrantClient(host="localhost", port=6333)


VECTOR_SIZE=512

 

# model that turns images and texts into vector embeddings
device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer("clip-ViT-B-32", device=device)
# designed for images
BATCH_SIZE = 256

@st.cache_data
def get_embeddings(collection_name: str = "CelebA"):
    """
        If the qdrantdb is empty, pull from the original celebA dataset add add the cluster to the database. Return if the database is already there
        
        Args:
            collection_name: str = CelebA

    """
    if not qdrant_client.collection_exists(collection_name):
        # create collection if it doesn't exist yet
        print("Collection not found, creating collection...")
        with st.spinner("Loading Embeddings in to qdrant database may take 10-15 minutes..."):
            qdrant_client.create_collection(collection_name, 
                vectors_config = VectorParams(
                    size = VECTOR_SIZE, 
                    distance=Distance.COSINE
            ))
            batch_size = 256
            pattern = f"{FOLDER_PATH}/img_align_dataset/img_align_celeba/img_align_celeba/*.jpg"
            image_paths = glob.glob(pattern)
            points = []
            for i in range(0, len(image_paths), BATCH_SIZE):
                batch = image_paths[i:i+BATCH_SIZE]
                print(f"Processing batch {i//BATCH_SIZE + 1}/{(len(image_paths) + BATCH_SIZE - 1)//BATCH_SIZE}")
                image_embedding = model.encode([Image.open(image_path) for image_path in batch],
                                        convert_to_numpy = True,
                                        show_progress_bar = True,
                                    )
                points = []
                # zip pairs embeddings with its corresponding image paths
                for j, (emb, path) in enumerate(zip(image_embedding, batch)):
                    points.append(PointStruct(
                        id=i + j + 1,
                        vector=emb.tolist(),
                        payload={"image_path": path},
                    )) 
                print(f"DEBUG: points: {len(points)} points")              
                qdrant_client.upsert(collection_name, points)
            print("Successfully uploaded Database to Qdrant!")
        
        st.success(f"Successfully uploaded {len(points)} points to Qdrant DB!")
    else:
        st.success("Collection already exists!")
        


def semantic_search(query: str, sim_score, results):
    """
        Returns results related to the query's semantic meaning pulling and searching from qdrant database 
    
    Args:
        - query: str - query user inputted
        - sim_score: float - similarity score user inputed
        - results: int - number of results user desires
        
    Returns:
        - list of images close to query description
    """
    # convert query to latent vector and compare semantic meaning to vectorDB
    query_embedding = model.encode(query, convert_to_numpy = True, show_progress_bar = True)
    print(f"DEBUG: query_embedding: {len(query_embedding)} vectors ")
    search_results = qdrant_client.query_points(
        collection_name= "CelebA",
        query = query_embedding,
        limit = results,
        # score_threshold = sim_score
    )
    print(f"DEBUG: search_results type: {type(search_results)}")
    print(f"DEBUG: search_results length: {search_results}")
    print(f"DEBUG: search_results content: {search_results.points}")
    return search_results.points
# store celebA dataset in Qdrant db

def main():
    get_embeddings()
    st.sidebar.title("Parameters")
    results = st.sidebar.slider(
            "Number of results",
            min_value=1,
            max_value=50,
            value=10,
            step=1
        )
    sim_score = st.sidebar.slider(
            "Similarity Score",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.05
    )
    query = st.text_input("Enter Description here", placeholder="e.g. beautiful blonde girl with glasses, handsome guy in a suit")

    if st.button("Search") and query:
        with st.spinner("Searching for similar images..."):
            search_results = semantic_search(query, sim_score, results) # semantic search on database
        print(f"search_results: {search_results}")
        cols = st.columns(3)
        for idx, result in enumerate(search_results):
            image_path = result.payload["image_path"]
            image = Image.open(image_path)
            # res = DeepFace.extract_faces(img_path=image_path)
            # draw = ImageDraw.Draw(image)
            # for face in res:
            #     area = face['facial_area']
            #     x,y,w,h = area['x'], area['y'], area['w'], area['h']
            #     draw.rectangle([x, y, x + w, y + h], outline='green', width=3)
            col = cols[idx % 3]
            with col:
                st.image(image, caption=f"Score: {result.score:.2f}")
    else:
        st.warning("Please enter a description to search for similar images")
        st.stop()

if __name__ == "__main__":
    main()