import React, { useState } from 'react'
import Header from './components/Header'
import PhotoUpload from './components/PhotoUpload'
import GarmentSelector from './components/GarmentSelector'
import TryOnDisplay from './components/TryOnDisplay'
import './styles/App.css'

function App() {
  const [userPhoto, setUserPhoto] = useState(null)
  const [bodyModel, setBodyModel] = useState(null)
  const [selectedGarment, setSelectedGarment] = useState(null)
  const [tryOnResult, setTryOnResult] = useState(null)

  const handlePhotoUpload = (photo, model) => {
    setUserPhoto(photo)
    setBodyModel(model)
  }

  const handleGarmentSelect = (garment) => {
    setSelectedGarment(garment)
  }

  const handleTryOnResult = (result) => {
    setTryOnResult(result)
  }

  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <div className="content-wrapper">
          <section className="hero-section">
            <h1>Welcome to StyleFit AI</h1>
            <p className="hero-subtitle">
              Experience the future of fashion with AI-powered virtual try-on technology
            </p>
          </section>

          <div className="platform-container">
            <div className="upload-section">
              <PhotoUpload 
                onPhotoUpload={handlePhotoUpload}
                userPhoto={userPhoto}
              />
            </div>

            {userPhoto && (
              <div className="garment-section">
                <GarmentSelector 
                  onGarmentSelect={handleGarmentSelect}
                  userPhoto={userPhoto}
                  onTryOnResult={handleTryOnResult}
                />
              </div>
            )}

            {tryOnResult && (
              <div className="result-section">
                <TryOnDisplay result={tryOnResult} />
              </div>
            )}
          </div>

          <section className="features-section">
            <h2>Platform Features</h2>
            <div className="features-grid">
              <div className="feature-card">
                <h3>🎯 AI Body Mapping</h3>
                <p>Advanced AI creates a precise 3D model of your body from a single photo</p>
              </div>
              <div className="feature-card">
                <h3>👗 Virtual Try-On</h3>
                <p>See how clothes look on you in real-time with realistic rendering</p>
              </div>
              <div className="feature-card">
                <h3>📊 Fit Analysis</h3>
                <p>Get personalized fit recommendations and size suggestions</p>
              </div>
              <div className="feature-card">
                <h3>🛍️ Shop Smart</h3>
                <p>Reduce returns and shop with confidence knowing how items will fit</p>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}

export default App
