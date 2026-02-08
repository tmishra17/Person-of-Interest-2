# Person-of-Interest-2

This project takes in user description of a person (tall man with glasses and long blond hair) and returns images matching the semantic meaning of the query. Images are stored in Qdrant Vector Databases

## Instructions
- User types descriptive query, selects similarity threshold, and number of results
- Application returns search results semantically similar to the user's query


## Powered by
- QdrantDB 
- SIGLIB2 for text image understanding
- Streamlit UI

## Future Features
- Removing Toxic queries (insults, cussing, keyboard smashing) using LLM 
- Accessible on Android Devices
- Allow image import to find images semantically similar to import image