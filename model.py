from flask import Flask, render_template, request, url_for
import numpy as np
from ultralytics import YOLO
import cv2
import os
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing.image import load_img, img_to_array
# from tensorflow.keras.applications.vgg16 import preprocess_input

# os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# from tensorflow.keras.preprocessing import image


app = Flask(__name__)
# model = load_model('CADx_Model.h5')  # Load your trained model
model = YOLO('best.pt')
target_img = os.path.join(os.getcwd(), 'Images')

@app.route('/')
def home_view():
    return render_template('home.html')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/index')
def index():
    return render_template('index.html')



# Allow files with extension png, jpg and jpeg
ALLOWED_EXT = set(['jpg', 'jpeg', 'png', 'pgm'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

# # Function to load and prepare the image in the right shape
# def read_image(filename):
#     img = load_img(filename, target_size=(32, 32))  # Adjust target size as needed
#     x = image.img_to_array(img)
#     x = np.expand_dims(x, axis=0)
#     x = preprocess_input(x)
#     print(f'Image shape: {x.shape}')
#     return x


# @app.route('/predict', methods=['GET', 'POST'])
# def predict():
#     if request.method == 'POST':
#         file = request.files['file']
#         if file and allowed_file(file.filename):
#             filename = file.filename
#             file_path = os.path.join('static/Images', filename)
#             print(file_path)
#             file.save(file_path)
#             img = read_image(file_path)
#             class_prediction = model.predict(img)
#             classes_x = np.argmax(class_prediction, axis=1)

#             # Map the class indices to your labels
#             if classes_x == 0:
#                 label = "Benign"
#             elif classes_x == 1:
#                 label = "Malignant"
#             else:
#                 label = "Unknown"


#             return render_template('predict.html', label=label, user_image=url_for('static', filename='Images/' + filename))
#         else:
#             return "Unable to read the file. Please check file extension"


# Function to load and prepare the image in the right shape for YOLO
def read_image(filename):
    # Open the image using OpenCV
    img = cv2.imread(filename)
    img = cv2.resize(img, (640, 640))  # YOLO expects 640x640 input
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB (for YOLO)
    return img_rgb

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            file_path = os.path.join('static/Images', filename)
            file.save(file_path)
            
            # Read and process the image for YOLO
            img = read_image(file_path)
            
            # Run inference using YOLO
            results = model(img)

            # Access bounding boxes and labels
            detected_objects = results[0].boxes  # Bounding box information
            labels = results[0].names  # Class label mapping

            # Prepare the response
            if detected_objects is not None and len(detected_objects) > 0:
                first_box = detected_objects[0]  # First detected object
                label_index = int(first_box.cls)  # Class ID
                label = labels[label_index]  # Class name
                confidence = first_box.conf.item()  # Convert tensor to float
                response_message = f"Detected: {label} with confidence {confidence:.2f}"
            else:
                response_message = "Normal"

            # Annotate and save the image (optional)
            annotated_image = results[0].plot()
            annotated_image_path = os.path.join('static/Images/annotated_' + filename)
            cv2.imwrite(annotated_image_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

            return render_template('predict.html', label=response_message, user_image=url_for('static', filename='Images/annotated_' + filename))
        else:
            return "Unable to read the file. Please check file extension."



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=8000)
