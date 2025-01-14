from flask import Flask, render_template, request, jsonify, send_from_directory
import cv2
import face_recognition
import os

app = Flask(__name__)

# Paths to folders containing celebrity images
celebrity_images_path = "celebrity_images"
celebrity_dataset_path = "celebrity_dataset"

celebrity_face_encodings = []
celebrity_names = []

# Load celebrity images and their face encodings for matching
for filename in os.listdir(celebrity_images_path):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        img_path = os.path.join(celebrity_images_path, filename)
        image = face_recognition.load_image_file(img_path)
        encoding = face_recognition.face_encodings(image)
        if len(encoding) > 0:
            celebrity_face_encodings.append(encoding[0])
            celebrity_names.append(os.path.splitext(filename)[0])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/match')
def match():
    return render_template('match.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Handle file upload from user
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"})

    # Save the uploaded image temporarily
    file_path = os.path.join('static', 'uploads', file.filename)
    file.save(file_path)
    
    # Load the uploaded image and recognize the face
    user_image = face_recognition.load_image_file(file_path)
    user_face_encodings = face_recognition.face_encodings(user_image)

    if len(user_face_encodings) == 0:
        return jsonify({"error": "No face found in the image"})
    
    user_encoding = user_face_encodings[0]

    # Compare with celebrity encodings
    matches = face_recognition.compare_faces(celebrity_face_encodings, user_encoding, tolerance=0.65)
    face_distances = face_recognition.face_distance(celebrity_face_encodings, user_encoding)

    if len(face_distances) > 0:
        best_match_index = face_distances.argmin()
        if matches[best_match_index]:
            match_name = celebrity_names[best_match_index]
            
            # Extract base celebrity name (without numbers)
            celebrity_base_name = ''.join([char for char in match_name if not char.isdigit()]).strip().lower()

            # DEBUGGING: Print the base celebrity name being searched for
            print(f"Base celebrity name: {celebrity_base_name}")

            # Find additional images of the matched celebrity in celebrity_dataset
            additional_images = []
            for image_name in os.listdir(celebrity_dataset_path):
                # Check if the image file starts with the celebrity's base name (case-insensitive)
                if image_name.lower().startswith(celebrity_base_name):
                    additional_images.append(image_name)

            # DEBUGGING: Print out additional images found
            print(f"Additional images found: {additional_images}")

            # If no additional images are found, return a message
            if not additional_images:
                return jsonify({"match": match_name, "additional_images": [], "message": "No additional images found."})

            return jsonify({
                "match": match_name, 
                "additional_images": additional_images
            })
        else:
            return jsonify({"match": "Unknown"})
    else:
        return jsonify({"match": "Unknown"})

# Route to serve additional images from the dataset
@app.route('/celebrity_dataset/<filename>')
def serve_celebrity_image(filename):
    return send_from_directory(celebrity_dataset_path, filename)

if __name__ == '__main__':
    app.run(debug=True)
