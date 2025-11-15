import React, { useState, useEffect } from 'react'
import { createBatchDownload, formatApiError } from '../utils/api'

function OfflineContentPage() {
  const [offlineContent, setOfflineContent] = useState([])
  const [selectedItems, setSelectedItems] = useState([])
  const [isDownloading, setIsDownloading] = useState(false)
  const [message, setMessage] = useState(null)
  const [isOnline, setIsOnline] = useState(navigator.onLine)

  useEffect(() => {
    loadOfflineContent()
    
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  const loadOfflineContent = () => {
    const cached = localStorage.getItem('offlineContent')
    if (cached) {
      setOfflineContent(JSON.parse(cached))
    }
  }

  const toggleSelection = (id) => {
    setSelectedItems(prev => 
      prev.includes(id) 
        ? prev.filter(item => item !== id)
        : [...prev, id]
    )
  }

  const handleBatchDownload = async () => {
    if (selectedItems.length === 0) {
      setMessage({ type: 'error', text: 'Please select at least one item' })
      return
    }

    if (selectedItems.length > 50) {
      setMessage({ type: 'error', text: 'Maximum 50 items can be downloaded at once' })
      return
    }

    setIsDownloading(true)
    setMessage(null)

    try {
      const response = await createBatchDownload(selectedItems, true)

      // Store the batch package information
      const downloadedContent = response.contents || []
      const existing = JSON.parse(localStorage.getItem('offlineContent') || '[]')
      
      // Merge and deduplicate
      const existingIds = new Set(existing.map(item => item.id))
      const newContent = downloadedContent.filter(item => !existingIds.has(item.id))
      const updated = [...existing, ...newContent]
      
      localStorage.setItem('offlineContent', JSON.stringify(updated))
      setOfflineContent(updated)
      setSelectedItems([])
      
      setMessage({ 
        type: 'success', 
        text: `Successfully downloaded ${newContent.length} items (${response.total_size_mb}MB) for offline access` 
      })
    } catch (err) {
      setMessage({ 
        type: 'error', 
        text: formatApiError(err)
      })
    } finally {
      setIsDownloading(false)
    }
  }

  const removeOfflineContent = (id) => {
    const updated = offlineContent.filter(item => item.id !== id)
    localStorage.setItem('offlineContent', JSON.stringify(updated))
    setOfflineContent(updated)
    setMessage({ type: 'success', text: 'Content removed from offline storage' })
  }

  const clearAllOffline = () => {
    if (window.confirm('Are you sure you want to clear all offline content?')) {
      localStorage.removeItem('offlineContent')
      setOfflineContent([])
      setMessage({ type: 'success', text: 'All offline content cleared' })
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Offline Content</h1>
        
        <div 
          className={`px-4 py-2 rounded-lg ${isOnline ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}
          role="status"
          aria-live="polite"
        >
          {isOnline ? '🟢 Online' : '🔴 Offline'}
        </div>
      </div>

      {message && (
        <div 
          className={`mb-6 px-4 py-3 rounded-lg ${
            message.type === 'success' 
              ? 'bg-green-50 border border-green-200 text-green-700' 
              : 'bg-red-50 border border-red-200 text-red-700'
          }`}
          role="alert"
          aria-live="polite"
        >
          {message.text}
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Download for Offline Access</h2>
        
        <p className="text-gray-600 mb-4">
          Select up to 50 content items to download for offline access. 
          Downloaded content will be available even without internet connection.
        </p>

        <div className="flex gap-4">
          <button
            onClick={handleBatchDownload}
            disabled={isDownloading || selectedItems.length === 0 || !isOnline}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            aria-label={`Download ${selectedItems.length} selected items`}
          >
            {isDownloading 
              ? 'Downloading...' 
              : `Download Selected (${selectedItems.length})`}
          </button>

          {selectedItems.length > 0 && (
            <button
              onClick={() => setSelectedItems([])}
              className="bg-gray-200 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-300 transition-colors"
              aria-label="Clear selection"
            >
              Clear Selection
            </button>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">
            Offline Content ({offlineContent.length} items)
          </h2>
          
          {offlineContent.length > 0 && (
            <button
              onClick={clearAllOffline}
              className="text-red-600 hover:text-red-700 text-sm font-medium"
              aria-label="Clear all offline content"
            >
              Clear All
            </button>
          )}
        </div>

        {offlineContent.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg mb-2">No offline content available</p>
            <p className="text-sm">Download content to access it offline</p>
          </div>
        ) : (
          <div className="space-y-4">
            {offlineContent.map((item) => (
              <div 
                key={item.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg mb-2">{item.subject}</h3>
                    
                    <div className="flex flex-wrap gap-2 mb-3">
                      <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                        {item.language}
                      </span>
                      <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                        Grade {item.grade_level}
                      </span>
                      {item.audio_file_path && (
                        <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                          🔊 Audio Available
                        </span>
                      )}
                    </div>

                    <p className="text-sm text-gray-600 line-clamp-2">
                      {item.simplified_text?.substring(0, 150)}...
                    </p>
                  </div>

                  <div className="flex gap-2 ml-4">
                    <a
                      href={`/content/${item.id}`}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                      aria-label={`View ${item.subject} content`}
                    >
                      View
                    </a>
                    
                    <button
                      onClick={() => removeOfflineContent(item.id)}
                      className="bg-red-100 text-red-700 px-4 py-2 rounded-lg hover:bg-red-200 transition-colors text-sm"
                      aria-label={`Remove ${item.subject} from offline storage`}
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold mb-2">💡 Offline Mode Tips</h3>
        <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
          <li>Downloaded content is stored locally on your device</li>
          <li>You can access downloaded content even without internet</li>
          <li>Maximum 50 items can be downloaded in a single batch</li>
          <li>Content will sync automatically when you're back online</li>
        </ul>
      </div>
    </div>
  )
}

export default OfflineContentPage
