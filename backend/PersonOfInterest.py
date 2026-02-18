from deepface import DeepFace
import torch
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, ScoredPoint
from sentence_transformers import SentenceTransformer
from PIL import Image
import glob
import os
from nicegui import ui

VECTOR_SIZE = 512
BATCH_SIZE = 256

class PersonOfInterest:
    def __init__(self) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer("clip-ViT-B-32", device=self.device)
        self.qdrant_client = QdrantClient(host="localhost", port=6333)

    def semantic_search(self, query: str, sim_score, results) -> list[ScoredPoint]:
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
        query_embedding = self.model.encode(query, convert_to_numpy = True, show_progress_bar = True)
        print(f"DEBUG: query_embedding: {len(query_embedding)} vectors ")
        search_results = self.qdrant_client.query_points(
            collection_name= "CelebA",
            query = query_embedding,
            limit = results,
            score_threshold = sim_score
        )
        
        return search_results.points
    
    def crop_image(self, image_path: str) -> Image.Image:
        """
        Crops the image to the face
        
        Args:
            - image_path: str - path to the image to crop
            
        Returns:
            - Object of cropped image (PIL.Image.Image)
        """
        image = Image.open(image_path)
        face = DeepFace.extract_faces(img_path=image_path,
            detector_backend="yunet",
            enforce_detection=False
        )[0]


        if not face:
            return image
        area = face['facial_area']
        x, y, w, h = area['x'], area['y'], area['w'], area['h']
        # left, top, right, bottom
        box = (x, y, x + w, y + h)
        cropped_image = image.crop(box)
        return cropped_image
            
    def get_embeddings(self, collection_name: str = "CelebA"):
        """
            Gets embeddings from the cropped images and uploads them to Qdrant database

            Args:
                - collection_name: str - name of the collection to upload the embeddings to
        """

        if not self.qdrant_client.collection_exists(collection_name):
            # create collection if it doesn't exist yet
            spinner = ui.spinner(size='lg')
            label = ui.label('Loading embeddings into Qdrant (may take 10–15 min)...')
            spinner.visible = label.visible = True
            print("Collection not found, creating collection...")
            with ui.row().classes("items-center gap-2"):
                self.qdrant_client.create_collection(collection_name, 
                    vectors_config = VectorParams(
                        size = VECTOR_SIZE, 
                        distance=Distance.COSINE
                ))
                folder_path = os.getenv("FOLDER_PATH") or os.getcwd()
                pattern = os.path.join(folder_path, "cropped_images", "*.jpg")
                image_paths = glob.glob(pattern)
                points = []
                count = 0
                for i in range(0, len(image_paths), BATCH_SIZE):
                    batch = image_paths[i:i+BATCH_SIZE]
                    cropped_images = [self.crop_image(image_path) for image_path in batch]
                    count += BATCH_SIZE
                    print(f"Processing batch {i//BATCH_SIZE + 1}/{(len(image_paths) + BATCH_SIZE - 1)//BATCH_SIZE}")
                    image_embedding = self.model.encode(cropped_images,
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
                    self.qdrant_client.upsert(collection_name, points)

                spinner.visible = label.visible = False
                print("Successfully uploaded Database to Qdrant!")
            
            ui.notify(f'Successfully Uploading {count} images to Qdrant!', type='positive')
        else:
            ui.notify('Collection already exists!', type='positive')
        

