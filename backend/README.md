# StyleFit AI Backend

Flask-based backend for the StyleFit AI virtual try-on platform.

## API Documentation

### Health Check
```
GET /api/health
```

### Upload Photo
```
POST /api/upload-photo
Content-Type: multipart/form-data

Body:
  photo: File (image file)

Response:
{
  "success": true,
  "filename": "photo.jpg",
  "body_model": {
    "status": "success",
    "measurements": {...},
    "key_points": {...}
  }
}
```

### Get Garments
```
GET /api/garments

Response:
{
  "garments": [...]
}
```

### Virtual Try-On
```
POST /api/try-on
Content-Type: application/json

Body:
{
  "user_photo": "filename.jpg",
  "garment_id": "dress_001"
}

Response:
{
  "success": true,
  "result_image": "data:image/jpeg;base64,...",
  "fit_analysis": {
    "fit_score": 0.85,
    "recommended_size": "M",
    "notes": [...]
  }
}
```

## Running the Server

```bash
python app.py
```

The server will run on http://localhost:5000
