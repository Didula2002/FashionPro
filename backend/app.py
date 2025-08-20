from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import pickle as pkl
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.layers import GlobalMaxPool2D
from sklearn.neighbors import NearestNeighbors
from numpy.linalg import norm
import os
import json

app = Flask(__name__)
CORS(app)

# Load features and filenames
Image_features = pkl.load(open('Images_features.pkl', 'rb'))
# Load filenames and remove the 'images/' prefix if present
filenames = pkl.load(open('filenames.pkl', 'rb'))
filenames = [os.path.basename(f) for f in filenames]  # Remove directory prefix

# Load product details
with open('products.json', 'r') as f:
    products = json.load(f)

# Load ResNet50 model
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
base_model.trainable = False
model = tf.keras.models.Sequential([base_model, GlobalMaxPool2D()])

# Fit NearestNeighbors
neighbors = NearestNeighbors(n_neighbors=6, algorithm='brute', metric='euclidean')
neighbors.fit(Image_features)

def extract_features_from_images(image_path, model):
    img = image.load_img(image_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_expand_dim = np.expand_dims(img_array, axis=0)
    img_preprocess = preprocess_input(img_expand_dim)
    result = model.predict(img_preprocess).flatten()
    return result / norm(result)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save uploaded file
    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    # Get recommendations
    input_img_features = extract_features_from_images(file_path, model)
    distances, indices = neighbors.kneighbors([input_img_features])

    # Return recommended image filenames and product details
    recommended_images = []
    for idx in indices[0][1:6]:  # Skip the first result (it's the input image itself)
        image_name = filenames[idx]
        product_info = next((product for product in products if product['image_name'] == image_name), None)
        if product_info:
            recommended_images.append({
                'image_name': image_name,
                'product_name': product_info['product_name'],
                'product_link': product_info['product_link']
            })
        else:
            # If no product info is found, still return the image name
            recommended_images.append({
                'image_name': image_name,
                'product_name': 'Product Name Not Found',
                'product_link': '#'
            })

    # Debug: Print the recommended images
    print("Recommended Images:", recommended_images)

    return jsonify({'recommended_images': recommended_images})

# Serve images from the "images" folde r
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

if __name__ == '__main__':
    app.run(debug=True)