import React, { useState, useEffect } from 'react'
import { handleKeyboardActivation } from '../utils/keyboardNavigation'

function AccessibilitySettings({ isDyslexicFont, onToggleDyslexicFont }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [fontSize, setFontSize] = useState('medium')
  const [highContrast, setHighContrast] = useState(false)

  useEffect(() => {
    const savedFontSize = localStorage.getItem('fontSize')
    const savedHighContrast = localStorage.getItem('highContrast')
    
    if (savedFontSize) {
      setFontSize(savedFontSize)
      applyFontSize(savedFontSize)
    }
    
    if (savedHighContrast === 'true') {
      setHighContrast(true)
      document.body.classList.add('high-contrast')
    }
  }, [])

  const applyFontSize = (size) => {
    document.documentElement.classList.remove('text-sm', 'text-base', 'text-lg', 'text-xl')
    
    switch(size) {
      case 'small':
        document.documentElement.classList.add('text-sm')
        break
      case 'large':
        document.documentElement.classList.add('text-lg')
        break
      case 'extra-large':
        document.documentElement.classList.add('text-xl')
        break
      default:
        document.documentElement.classList.add('text-base')
    }
  }

  const handleFontSizeChange = (size) => {
    setFontSize(size)
    localStorage.setItem('fontSize', size)
    applyFontSize(size)
  }

  const handleHighContrastToggle = () => {
    const newValue = !highContrast
    setHighContrast(newValue)
    localStorage.setItem('highContrast', newValue.toString())
    
    if (newValue) {
      document.body.classList.add('high-contrast')
    } else {
      document.body.classList.remove('high-contrast')
    }
  }

  return (
    <div 
      className="bg-white rounded-lg shadow-md p-4 mb-6"
      role="region"
      aria-label="Accessibility settings"
    >
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        onKeyDown={(e) => handleKeyboardActivation(e, () => setIsExpanded(!isExpanded))}
        className="w-full flex justify-between items-center text-lg font-semibold mb-3 focus:outline-none"
        aria-expanded={isExpanded}
        aria-controls="accessibility-options"
      >
        <span>Accessibility Options</span>
        <span aria-hidden="true">{isExpanded ? '▼' : '▶'}</span>
      </button>
      
      {isExpanded && (
        <div id="accessibility-options" className="space-y-4">
          <div className="border-t pt-4">
            <label 
              htmlFor="dyslexic-font-toggle"
              className="flex items-center cursor-pointer"
            >
              <input
                type="checkbox"
                id="dyslexic-font-toggle"
                checked={isDyslexicFont}
                onChange={onToggleDyslexicFont}
                className="w-5 h-5 mr-3 cursor-pointer focus:ring-2 focus:ring-blue-500"
                aria-describedby="dyslexic-font-description"
              />
              <span className="text-gray-700 font-medium">
                Use OpenDyslexic Font
              </span>
            </label>
            
            <p 
              id="dyslexic-font-description"
              className="text-sm text-gray-600 mt-2 ml-8"
            >
              A font designed to improve readability for people with dyslexia
            </p>
          </div>

          <div className="border-t pt-4">
            <fieldset>
              <legend className="text-gray-700 font-medium mb-2">Text Size</legend>
              <div className="flex flex-wrap gap-2">
                {['small', 'medium', 'large', 'extra-large'].map((size) => (
                  <label key={size} className="flex items-center cursor-pointer">
                    <input
                      type="radio"
                      name="fontSize"
                      value={size}
                      checked={fontSize === size}
                      onChange={() => handleFontSizeChange(size)}
                      className="mr-2 focus:ring-2 focus:ring-blue-500"
                      aria-label={`${size} text size`}
                    />
                    <span className="text-sm capitalize">{size.replace('-', ' ')}</span>
                  </label>
                ))}
              </div>
            </fieldset>
          </div>

          <div className="border-t pt-4">
            <label 
              htmlFor="high-contrast-toggle"
              className="flex items-center cursor-pointer"
            >
              <input
                type="checkbox"
                id="high-contrast-toggle"
                checked={highContrast}
                onChange={handleHighContrastToggle}
                className="w-5 h-5 mr-3 cursor-pointer focus:ring-2 focus:ring-blue-500"
                aria-describedby="high-contrast-description"
              />
              <span className="text-gray-700 font-medium">
                High Contrast Mode
              </span>
            </label>
            
            <p 
              id="high-contrast-description"
              className="text-sm text-gray-600 mt-2 ml-8"
            >
              Increases contrast for better visibility
            </p>
          </div>

          <div className="border-t pt-4">
            <h3 className="text-gray-700 font-medium mb-2">Keyboard Shortcuts</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li><kbd className="px-2 py-1 bg-gray-100 rounded">Tab</kbd> - Navigate between elements</li>
              <li><kbd className="px-2 py-1 bg-gray-100 rounded">Enter</kbd> or <kbd className="px-2 py-1 bg-gray-100 rounded">Space</kbd> - Activate buttons</li>
              <li><kbd className="px-2 py-1 bg-gray-100 rounded">Esc</kbd> - Close dialogs</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}

export default AccessibilitySettings
