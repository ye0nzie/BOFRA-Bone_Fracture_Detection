from flask import Flask, render_template, request, jsonify, send_from_directory
from ultralytics import YOLO
from PIL import Image
# from tensorflow.keras.models import load_model
# from tensorflow.keras import backend as K
import os
import cv2
import numpy as np
from datetime import datetime
import io





# =========================
# INIT APP
# =========================
app = Flask(__name__)

# =========================
# FOLDER CONFIG
# =========================
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
MODEL_FOLDER = 'model'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# =========================
# LOAD MODELS
# =========================
print("Loading YOLO model...")
yolo_model = YOLO(os.path.join(MODEL_FOLDER, 'best.pt'))

print("Loading CNN model...")
try:
    cnn_model = load_model(os.path.join(MODEL_FOLDER, 'cnn_best.h5'))
except Exception as e:
    cnn_model = None
    print("WARNING: CNN model failed to load:", e)

# =========================
# CNN HELPER FUNCTION
# =========================
def run_cnn_on_crop(crop_bgr):
    """
    Run CNN on cropped image
    Returns dict or None
    """
    if cnn_model is None:
        return None

    try:
        # BGR -> RGB
        crop_rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)

        # Get model input shape
        input_shape = cnn_model.input_shape
        target_h, target_w = 224, 224

        if len(input_shape) == 4:
            _, h, w, c = input_shape
            if h and w:
                target_h, target_w = int(h), int(w)

        # Resize & normalize
        resized = cv2.resize(crop_rgb, (target_w, target_h))
        x = resized.astype('float32') / 255.0

        if K.image_data_format() == 'channels_first':
            x = np.transpose(x, (2, 0, 1))

        x = np.expand_dims(x, axis=0)

        preds = cnn_model.predict(x)

        # Binary / softmax handling
        if preds.shape[1] == 1:
            prob = float(preds[0][0])
            label = "fractured" if prob >= 0.5 else "not fractured"
            confidence = prob if label == "fractured" else (1 - prob)
        else:
            idx = int(np.argmax(preds[0]))
            prob = float(preds[0][idx])
            labels = ["not fractured", "fractured"]
            label = labels[idx]

        return {
            "cnn_prediction": label,
            "cnn_confidence": round(prob * 100, 2)
        }

    except Exception as e:
        print("CNN inference error:", e)
        return None

# =========================
# ROUTES
# =========================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save upload
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # YOLO detection
        results = yolo_model.predict(source=filepath, conf=0.5, save=False)
        result = results[0]

        img = cv2.imread(filepath)
        h_img, w_img = img.shape[:2]

        detections = []
        fracture_detected = False

        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            yolo_conf = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = yolo_model.names[class_id]

            # Draw YOLO box
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                img,
                f"{class_name} {yolo_conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

            # Crop
            x1c, y1c = max(0, x1), max(0, y1)
            x2c, y2c = min(w_img, x2), min(h_img, y2)
            crop = img[y1c:y2c, x1c:x2c]

            cnn_info = run_cnn_on_crop(crop) if crop.size > 0 else None

            detection = {
                "class": class_name,
                "confidence": round(yolo_conf * 100, 2),
                "bbox": [x1, y1, x2, y2],
                "cnn_prediction": cnn_info["cnn_prediction"] if cnn_info else None,
                "cnn_confidence": cnn_info["cnn_confidence"] if cnn_info else None
            }

            detections.append(detection)
            fracture_detected = True

        # Save result image
        result_filename = f"result_{filename}"
        result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
        cv2.imwrite(result_path, img)

        main_detection = max(detections, key=lambda x: x['confidence']) if detections else None

        return jsonify({
            "success": True,
            "fracture_detected": fracture_detected,
            "total_detections": len(detections),
            "detections": detections,
            "main_detection": main_detection,
            "original_image": f"/static/uploads/{filename}",
            "result_image": f"/static/results/{result_filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# =========================
# RUN
# =========================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
