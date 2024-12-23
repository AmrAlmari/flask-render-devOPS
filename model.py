from flask import Flask, render_template, request, url_for
import os
import cv2
from ultralytics import YOLO

app = Flask(__name__, static_folder='static', template_folder='templates')

# YOLO model
model = YOLO('best.pt')

# Ensure upload folder exists
upload_folder = os.path.join(app.static_folder, 'Images')
os.makedirs(upload_folder, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pgm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_image(filename):
    img = cv2.imread(filename)
    img = cv2.resize(img, (640, 640))
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img_rgb

@app.route('/')
def home_view():
    return render_template('home.html')
@app.route('/home')
def home():
    return render_template('home.html')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        img = read_image(file_path)
        results = model(img)
        
        detected_objects = results[0].boxes
        labels = results[0].names

        if detected_objects is not None and len(detected_objects) > 0:
            first_box = detected_objects[0]
            label_index = int(first_box.cls)
            label = labels[label_index]
            confidence = first_box.conf.item()
            response_message = f"Detected: {label} with confidence {confidence:.2f}"
        else:
            response_message = "Normal"

        annotated_image = results[0].plot()
        annotated_image_path = os.path.join(upload_folder, f'annotated_{filename}')
        cv2.imwrite(annotated_image_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

        return render_template('predict.html', label=response_message, user_image=url_for('static', filename=f'Images/annotated_{filename}'))
    else:
        return "Invalid file format. Please upload a valid image."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)
