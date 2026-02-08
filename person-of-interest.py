import streamlit as st
import deepface
import torch
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from transformers import AutoProcessor, AutoModel
from sentence_transformers import SentenceTransformers
st.title("Person of Interest")
qdrant_client = QdrantClient(host="localhost", port=6333)

IMG_DB_PATH = "/imgdb/imgdb"

VECTOR_SIZE=768
# no classification needed, turning images and text into vector embeddings and points
# in a vector space, where the semantic meanings of the text will be directly compared to the 
# semantic meanings of the images


# tokens are numeric representation of texts, words, images, Neural Networks only understand numbers, 
# thus the tokens coverts the word/image in to a numerical representation
# Attention mechanism assigns meaning by comparing tokens in data
# embeddings are tokens converted into vector types

# text = st.search_box("enter a description", placeholder="Enter a name")
# device = ""

# sentence transformers vs transformers with mean pooling
 

# model that turns images and texts into vector embeddings
device = "cuda" if torch.cuda.is_available() else "cpu"
processor = AutoProcessor.from_pretrained("google/siglip-base-patch16-224")
model = AutoModel.from_pretrained("google/siglip-base-patch16-224").to(device)

def get_text_embedding(text: str)->List[float]:
    """
    Convert text to embedding vector
    
    Args: 
        text-> str - text query
   
    Returns:
        - Query Embedding (vector List)
    """
    inputs = processor(text=text, return_tensors="pt").to(device)
    with torch.no_grad():
        embedding = model.get_text_features(**inputs)
    return embedding[0].cpu().numpy().tolist()

def get_embeddings(collection_name: str = "CelebA"):
    """
        if the qdrantdb is empty, pull from the original celebA dataset add add the cluster to the database
        Args:
            collection_name: str = CelebA
    """
    try:
        qdrant_client.get_collection(collection_name)
        return
    except:
        qdrant_client.create_collection(collection_name, {
            VectorParams(size = VECTOR_SIZE, distance=Distance.COSINE)
        })
        
        # open celebA dataset -> open image -> tokenize -> create image_embedding -> upload to Qdrant
        
        points = []
        
        

        
        
    pass

def semantic_search(query: str, sim_score: float, results: int):
    """
        Returns results related to the query's semantic meaning pulling and searching from qdrant database 
    
    Args:
        - query: str - query user inputted
        - sim_score: float - similarity score user inputed
        - results: int - number of results user desires
        
    Returns:
        - list of images close to query description
    """
    query_embedding = get_text_embedding(query)
    search_results = qdrant_client.search(
        collection_name= "CelebA",
        query_vector = query_embedding,
        limit=results,
        score_threshold = sim_score
    )
    return search_results
# store celebA dataset in Qdrant db

def main():
    st.sidebar.title("Parameters")
    results = st.sidebar.slider("Number of results", 1, 50, 10, 1)
    sim_score = st.sidebar.slider("Similarity Score", 0.0, 5.0, 0.2, .2)
    query = st.text_input("Enter Description here", placeholder="e.g. beautiful blonde girl with glasses, handsome guy in a suit")

    if st.button("Search"):
        semantic_search(query, results, sim_score) # semantic search on database

    
if __name__ == "__main__":
    main()