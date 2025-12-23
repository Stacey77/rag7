# StyleFit AI - Virtual Try-On Platform

## Overview

StyleFit AI is an innovative AI-powered virtual try-on platform that revolutionizes online fashion shopping. Using advanced computer vision and machine learning, users can upload their photos and virtually try on clothing items to see how they look before making a purchase.

## Features

### Core Features (MVP)

- **AI-Powered Body Mapping**: Upload a photo and our AI creates a body model with measurements
- **Virtual Try-On**: See how garments look on you in real-time with realistic rendering
- **Fit Analysis**: Get personalized fit recommendations and size suggestions
- **Garment Catalog**: Browse and try on various clothing items from different categories
- **User-Friendly Interface**: Intuitive React-based UI with smooth interactions

### Technology Stack

**Frontend:**
- React 18
- Vite (build tool)
- Axios (API calls)
- Modern CSS with responsive design

**Backend:**
- Python/Flask
- OpenCV for image processing
- TensorFlow/PyTorch (for AI models)
- Pillow for image manipulation

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Stacey77/rag7.git
cd rag7
```

2. **Install Frontend Dependencies**
```bash
npm install
```

3. **Install Backend Dependencies**
```bash
pip install -r requirements.txt
```

### Running the Application

1. **Start the Backend Server**
```bash
cd backend
python app.py
```
The backend will run on `http://localhost:5000`

2. **Start the Frontend Development Server**
```bash
npm run dev
```
The frontend will run on `http://localhost:3000`

3. **Access the Application**
Open your browser and navigate to `http://localhost:3000`

## Usage

1. **Upload Your Photo**: Click on the upload area and select a full-body photo
2. **Browse Garments**: Once your photo is uploaded, browse available garments by category
3. **Try On**: Click on any garment to see it virtually applied to your photo
4. **View Fit Analysis**: Check the fit score and size recommendations
5. **Take Action**: Add to cart, save to lookbook, or share with friends

## Project Structure

```
rag7/
├── backend/
│   ├── api/
│   │   ├── body_mapping.py      # Body mapping AI module
│   │   ├── garment_processor.py # Garment catalog management
│   │   └── virtual_tryon.py     # Virtual try-on engine
│   └── app.py                   # Flask application
├── src/
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── PhotoUpload.jsx
│   │   ├── GarmentSelector.jsx
│   │   └── TryOnDisplay.jsx
│   ├── services/
│   │   └── api.js              # API service layer
│   ├── styles/
│   │   └── *.css               # Component styles
│   ├── App.jsx                 # Main application component
│   └── main.jsx                # Application entry point
├── public/                     # Static assets
├── uploads/                    # User uploaded photos
├── package.json
├── requirements.txt
└── README.md
```

## API Endpoints

### Backend API

- `GET /api/health` - Health check endpoint
- `POST /api/upload-photo` - Upload user photo for body mapping
- `GET /api/garments` - Get available garments
- `POST /api/try-on` - Perform virtual try-on

## Future Enhancements

- **AI Stylist**: Personalized outfit recommendations
- **Outfit Builder**: Mix and match items to create complete outfits
- **Social Sharing**: Share virtual try-ons with friends
- **Brand Integration**: Direct purchase links to e-commerce sites
- **AR Overlay**: Mobile AR experience using phone cameras
- **Advanced Body Modeling**: More accurate 3D body reconstruction
- **Material Simulation**: Realistic fabric draping and movement
- **User Accounts**: Save preferences and lookbooks

## Development

### Build for Production

```bash
npm run build
```

### Lint Code

```bash
npm run lint
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Mission

To empower users to confidently explore and experiment with fashion virtually, reducing returns and enhancing the shopping experience through advanced AI technology.

---

**Note**: This is an MVP implementation. The AI models are currently using placeholder logic. In production, these would be replaced with trained deep learning models for accurate body mapping, garment digitization, and virtual try-on rendering.