import React, { useState, useEffect } from 'react'
import apiService from '../services/api'
import '../styles/GarmentSelector.css'

function GarmentSelector({ onGarmentSelect, userPhoto, onTryOnResult }) {
  const [garments, setGarments] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedGarment, setSelectedGarment] = useState(null)
  const [tryingOn, setTryingOn] = useState(false)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    loadGarments()
  }, [])

  const loadGarments = async () => {
    try {
      const data = await apiService.getGarments()
      setGarments(data.garments)
    } catch (error) {
      console.error('Failed to load garments:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGarmentClick = async (garment) => {
    setSelectedGarment(garment)
    onGarmentSelect(garment)

    // Automatically trigger try-on
    setTryingOn(true)
    try {
      const result = await apiService.tryOn(userPhoto, garment.id)
      onTryOnResult(result)
    } catch (error) {
      console.error('Try-on failed:', error)
    } finally {
      setTryingOn(false)
    }
  }

  const filteredGarments = filter === 'all' 
    ? garments 
    : garments.filter(g => g.category === filter)

  const categories = ['all', 'dress', 'shirt', 'pants', 'outerwear', 'skirt']

  return (
    <div className="garment-selector">
      <h2>Step 2: Select a Garment</h2>
      
      <div className="filter-bar">
        {categories.map(cat => (
          <button
            key={cat}
            className={`filter-btn ${filter === cat ? 'active' : ''}`}
            onClick={() => setFilter(cat)}
          >
            {cat.charAt(0).toUpperCase() + cat.slice(1)}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="loading-state">Loading garments...</div>
      ) : (
        <div className="garments-grid">
          {filteredGarments.map(garment => (
            <div
              key={garment.id}
              className={`garment-card ${selectedGarment?.id === garment.id ? 'selected' : ''}`}
              onClick={() => handleGarmentClick(garment)}
            >
              <div className="garment-image-placeholder">
                <div className="garment-icon">👕</div>
              </div>
              <div className="garment-info">
                <h3>{garment.name}</h3>
                <p className="garment-brand">{garment.brand}</p>
                <p className="garment-price">${garment.price}</p>
                <div className="garment-colors">
                  {garment.colors.map(color => (
                    <span key={color} className="color-dot" title={color}></span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {tryingOn && (
        <div className="trying-on-overlay">
          <div className="spinner"></div>
          <p>Applying garment to your photo...</p>
        </div>
      )}
    </div>
  )
}

export default GarmentSelector
