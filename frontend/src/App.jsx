import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import UploadPage from './pages/UploadPage'
import ContentViewerPage from './pages/ContentViewerPage'
import OfflineContentPage from './pages/OfflineContentPage'
import AccessibilitySettings from './components/AccessibilitySettings'

function App() {
  const [isDyslexicFont, setIsDyslexicFont] = useState(false)

  useEffect(() => {
    const savedPreference = localStorage.getItem('dyslexicFont')
    if (savedPreference === 'true') {
      setIsDyslexicFont(true)
      document.body.classList.add('dyslexic-font')
    }
  }, [])

  const toggleDyslexicFont = () => {
    const newValue = !isDyslexicFont
    setIsDyslexicFont(newValue)
    localStorage.setItem('dyslexicFont', newValue.toString())
    
    if (newValue) {
      document.body.classList.add('dyslexic-font')
    } else {
      document.body.classList.remove('dyslexic-font')
    }
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <a href="#main-content" className="skip-link">
          Skip to main content
        </a>
        
        <nav className="bg-blue-600 text-white shadow-lg" role="navigation" aria-label="Main navigation">
          <div className="container mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold">
                <Link to="/" aria-label="Home - Multilingual Education Platform">
                  Multilingual Education
                </Link>
              </h1>
              
              <nav role="navigation" aria-label="Main menu">
                <ul className="flex space-x-6" role="menubar">
                  <li role="none">
                    <Link 
                      to="/upload" 
                      className="hover:text-blue-200 transition-colors focus:outline-none focus:ring-2 focus:ring-white rounded px-2 py-1"
                      role="menuitem"
                      aria-label="Upload content"
                    >
                      Upload
                    </Link>
                  </li>
                  <li role="none">
                    <Link 
                      to="/content" 
                      className="hover:text-blue-200 transition-colors focus:outline-none focus:ring-2 focus:ring-white rounded px-2 py-1"
                      role="menuitem"
                      aria-label="View content"
                    >
                      Content
                    </Link>
                  </li>
                  <li role="none">
                    <Link 
                      to="/offline" 
                      className="hover:text-blue-200 transition-colors focus:outline-none focus:ring-2 focus:ring-white rounded px-2 py-1"
                      role="menuitem"
                      aria-label="Offline content"
                    >
                      Offline
                    </Link>
                  </li>
                </ul>
              </nav>
            </div>
          </div>
        </nav>

        <main id="main-content" className="container mx-auto px-4 py-8" role="main">
          <AccessibilitySettings 
            isDyslexicFont={isDyslexicFont}
            onToggleDyslexicFont={toggleDyslexicFont}
          />
          
          <Routes>
            <Route path="/" element={<UploadPage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/content" element={<ContentViewerPage />} />
            <Route path="/content/:id" element={<ContentViewerPage />} />
            <Route path="/offline" element={<OfflineContentPage />} />
          </Routes>
        </main>

        <footer className="bg-gray-800 text-white py-6 mt-12" role="contentinfo">
          <div className="container mx-auto px-4 text-center">
            <p>&copy; 2024 Multilingual Education Platform. Democratizing learning for all.</p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
