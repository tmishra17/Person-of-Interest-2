import streamlit as st
from PIL import Image
import os
from dotenv import load_dotenv
from backend import search
from PersonOfInterest import PersonOfInterest

load_dotenv()  # reads .env file into os.environ
st.title("Person of Interest")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_NUM_INTEROP_THREADS"] = "1"
os.environ["TF_NUM_INTRAOP_THREADS"] = "1"


@st.cache_resource
def get_poi():
    return PersonOfInterest()

def main():
    POI = get_poi()
    POI.get_embeddings()
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
            search_results = POI.semantic_search(
                query=query, 
                sim_score=sim_score,
                results=results
            ) # semantic search on database
        
        print(f"search_results: {search_results}")
        cols = st.columns(3)
        for idx, result in enumerate(search_results):
            image_path = result.payload['image_path']
            image = Image.open(image_path)
            col = cols[idx % 3]
            with col:
                st.image(image, caption=f"Score: {result.score:.2f}")

if __name__ == "__main__":
    main()