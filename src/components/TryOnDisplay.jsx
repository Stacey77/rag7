import React from 'react'
import '../styles/TryOnDisplay.css'

function TryOnDisplay({ result }) {
  if (!result) return null

  const { result_image, fit_analysis } = result

  return (
    <div className="tryon-display">
      <h2>Step 3: View Your Virtual Try-On</h2>
      
      <div className="tryon-content">
        <div className="tryon-image-container">
          {result_image ? (
            <img 
              src={result_image} 
              alt="Virtual Try-On Result" 
              className="tryon-image"
            />
          ) : (
            <div className="no-image">Try-on result not available</div>
          )}
        </div>

        {fit_analysis && (
          <div className="fit-analysis">
            <h3>Fit Analysis</h3>
            
            <div className="fit-score">
              <div className="score-label">Fit Score</div>
              <div className="score-value">
                {Math.round(fit_analysis.fit_score * 100)}%
              </div>
              <div className="score-bar">
                <div 
                  className="score-fill"
                  style={{ width: `${fit_analysis.fit_score * 100}%` }}
                ></div>
              </div>
            </div>

            <div className="size-recommendation">
              <strong>Recommended Size:</strong> {fit_analysis.recommended_size}
            </div>

            <div className="fit-notes">
              <h4>Fit Notes:</h4>
              <ul>
                {fit_analysis.notes.map((note, index) => (
                  <li key={index}>{note}</li>
                ))}
              </ul>
            </div>

            <div className="action-buttons">
              <button className="btn-primary">Add to Cart</button>
              <button className="btn-secondary">Save to Lookbook</button>
              <button className="btn-secondary">Share</button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default TryOnDisplay
