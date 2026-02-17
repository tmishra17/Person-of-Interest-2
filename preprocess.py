from deepface import DeepFace
from PIL import Image, ImageDraw
import streamlit as st
import glob
import os
import numpy as np

pattern = f"./img_align_dataset/img_align_celeba/img_align_celeba/*.jpg"
output_dir = f"./cropped_images"
os.makedirs(output_dir, exist_ok=True)
image_paths = glob.glob(pattern)
print(f"Found {len(image_paths)} images to process")

for image_path in image_paths:
    image = Image.open(image_path)
    face = DeepFace.extract_faces(img_path=image_path, 
    enforce_detection=False,
    detector_backend="yunet",
    # recognition_model="ArcFace"   
    )[0]
    if not face:
        cropped_image = image
    else:
        area = face['facial_area']
        x, y, w, h = area['x'], area['y'], area['w'], area['h']
        box = (x, y, x + w, y + h)
        cropped_image = image.crop(box)
    filename = os.path.basename(image_path)
    filename = os.path.join(output_dir, filename)
    # save cropped image to specified output file
    cropped_image.save(filename)
    print(f"Saved cropped image to {filename}")