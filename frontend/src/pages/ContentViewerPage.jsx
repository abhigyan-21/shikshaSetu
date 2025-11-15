import React, { useState, useEffect, useRef } from 'react'
import { useParams, useSearchParams } from 'react-router-dom'
import { getContent, getAudioUrl, searchContent, formatApiError } from '../utils/api'

function ContentViewerPage() {
  const { id } = useParams()
  const [searchParams] = useSearchParams()
  const [content, setContent] = useState(null)
  const [searchResults, setSearchResults] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const audioRef = useRef(null)

  const [filters, setFilters] = useState({
    language: searchParams.get('language') || '',
    grade: searchParams.get('grade') || '',
    subject: searchParams.get('subject') || ''
  })

  useEffect(() => {
    if (id) {
      fetchContent(id)
    }
  }, [id])

  const fetchContent = async (contentId) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const data = await getContent(contentId)
      setContent(data)
    } catch (err) {
      setError(formatApiError(err))
    } finally {
      setIsLoading(false)
    }
  }

  const handleSearch = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await searchContent({
        language: filters.language || undefined,
        grade: filters.grade || undefined,
        subject: filters.subject || undefined,
        limit: 20,
        offset: 0
      })
      
      setSearchResults(response.results || [])
    } catch (err) {
      setError(formatApiError(err))
    } finally {
      setIsLoading(false)
    }
  }

  const toggleAudio = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Content Viewer</h1>

      {!id && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Search Content</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label htmlFor="search-language" className="block text-sm font-medium mb-2">
                Language
              </label>
              <select
                id="search-language"
                value={filters.language}
                onChange={(e) => setFilters({ ...filters, language: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                aria-label="Filter by language"
              >
                <option value="">All Languages</option>
                <option value="Hindi">Hindi</option>
                <option value="Tamil">Tamil</option>
                <option value="Telugu">Telugu</option>
                <option value="Bengali">Bengali</option>
                <option value="Marathi">Marathi</option>
              </select>
            </div>

            <div>
              <label htmlFor="search-grade" className="block text-sm font-medium mb-2">
                Grade
              </label>
              <select
                id="search-grade"
                value={filters.grade}
                onChange={(e) => setFilters({ ...filters, grade: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                aria-label="Filter by grade"
              >
                <option value="">All Grades</option>
                {Array.from({ length: 8 }, (_, i) => i + 5).map(grade => (
                  <option key={grade} value={grade}>Grade {grade}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="search-subject" className="block text-sm font-medium mb-2">
                Subject
              </label>
              <select
                id="search-subject"
                value={filters.subject}
                onChange={(e) => setFilters({ ...filters, subject: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                aria-label="Filter by subject"
              >
                <option value="">All Subjects</option>
                <option value="Mathematics">Mathematics</option>
                <option value="Science">Science</option>
                <option value="Social Studies">Social Studies</option>
                <option value="English">English</option>
                <option value="History">History</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleSearch}
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-2 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
            aria-label="Search content"
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>
      )}

      {error && (
        <div 
          className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6"
          role="alert"
          aria-live="polite"
        >
          <strong className="font-semibold">Error: </strong>
          <span>{error}</span>
        </div>
      )}

      {isLoading && (
        <div 
          className="text-center py-12"
          role="status"
          aria-live="polite"
        >
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading content...</p>
        </div>
      )}

      {content && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="mb-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold mb-2">Content Details</h2>
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    {content.language}
                  </span>
                  <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                    Grade {content.grade_level}
                  </span>
                  <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                    {content.subject}
                  </span>
                </div>
              </div>
              
              {content.audio_url && (
                <button
                  onClick={toggleAudio}
                  className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors"
                  aria-label={isPlaying ? 'Pause audio' : 'Play audio'}
                  aria-pressed={isPlaying}
                >
                  {isPlaying ? '⏸ Pause' : '▶ Play Audio'}
                </button>
              )}
            </div>

            {content.audio_url && (
              <audio
                ref={audioRef}
                src={getAudioUrl(content.id)}
                onEnded={() => setIsPlaying(false)}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                className="hidden"
                aria-label="Content audio"
              />
            )}
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Simplified Text</h3>
            <div 
              className="prose max-w-none p-4 bg-gray-50 rounded-lg"
              role="article"
              aria-label="Simplified content"
            >
              <p className="whitespace-pre-wrap">{content.simplified_text}</p>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Translated Text ({content.language})</h3>
            <div 
              className="prose max-w-none p-4 bg-gray-50 rounded-lg"
              role="article"
              aria-label={`Translated content in ${content.language}`}
              lang={content.language.toLowerCase()}
            >
              <p className="whitespace-pre-wrap">{content.translated_text}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-blue-50 rounded-lg">
            <div>
              <p className="text-sm text-gray-600">NCERT Alignment Score</p>
              <p className="text-2xl font-bold text-blue-600">
                {(content.ncert_alignment_score * 100).toFixed(1)}%
              </p>
            </div>
            {content.audio_accuracy_score && (
              <div>
                <p className="text-sm text-gray-600">Audio Accuracy Score</p>
                <p className="text-2xl font-bold text-green-600">
                  {(content.audio_accuracy_score * 100).toFixed(1)}%
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {searchResults.length > 0 && (
        <div className="mt-6">
          <h2 className="text-2xl font-bold mb-4">Search Results</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {searchResults.map((item) => (
              <a
                key={item.id}
                href={`/content/${item.id}`}
                className="block bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow"
                aria-label={`View content: ${item.subject} for Grade ${item.grade_level} in ${item.language}`}
              >
                <h3 className="font-semibold mb-2">{item.subject}</h3>
                <div className="flex flex-wrap gap-2 mb-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                    {item.language}
                  </span>
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                    Grade {item.grade_level}
                  </span>
                </div>
                <p className="text-sm text-gray-600 line-clamp-3">
                  {item.simplified_text?.substring(0, 100)}...
                </p>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ContentViewerPage
