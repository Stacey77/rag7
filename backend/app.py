from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import json

from api.body_mapping import BodyMapper
from api.garment_processor import GarmentProcessor
from api.virtual_tryon import VirtualTryOn

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize services
body_mapper = BodyMapper()
garment_processor = GarmentProcessor()
virtual_tryon = VirtualTryOn()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'StyleFit AI'})

@app.route('/api/upload-photo', methods=['POST'])
def upload_photo():
    """Upload user photo for body mapping"""
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo provided'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process body mapping
        body_model = body_mapper.map_body(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'body_model': body_model
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/garments', methods=['GET'])
def get_garments():
    """Get available garments for try-on"""
    garments = garment_processor.get_available_garments()
    return jsonify({'garments': garments})

@app.route('/api/try-on', methods=['POST'])
def try_on():
    """Perform virtual try-on"""
    data = request.json
    user_photo = data.get('user_photo')
    garment_id = data.get('garment_id')
    
    if not user_photo or not garment_id:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    # Perform virtual try-on
    result = virtual_tryon.apply_garment(user_photo, garment_id)
    
    return jsonify({
        'success': True,
        'result_image': result['image'],
        'fit_analysis': result['fit_analysis']
    })

@app.route('/api/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Debug mode should only be enabled in development
    # For production, use a production WSGI server like gunicorn
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
