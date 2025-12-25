import React from 'react'
import '../styles/Header.css'

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <span className="logo-icon">✨</span>
          <span className="logo-text">StyleFit AI</span>
        </div>
        <nav className="nav">
          <a href="#home">Home</a>
          <a href="#try-on">Try On</a>
          <a href="#about">About</a>
          <a href="#contact">Contact</a>
        </nav>
      </div>
    </header>
  )
}

export default Header
