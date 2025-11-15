/**
 * API utility for connecting frontend to backend endpoints.
 * 
 * This module provides a centralized interface for all API calls,
 * handling request formatting, error handling, and response parsing.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

/**
 * Process educational content through the pipeline.
 * 
 * @param {Object} data - Content processing request
 * @param {string} data.input_data - Text content to process
 * @param {string} data.target_language - Target language (Hindi, Tamil, etc.)
 * @param {number} data.grade_level - Grade level (5-12)
 * @param {string} data.subject - Subject area
 * @param {string} data.output_format - Output format (text, audio, both)
 * @returns {Promise<Object>} Processed content result
 */
export async function processContent(data) {
  const response = await fetch(`${API_BASE_URL}/api/process-content`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.details || error.error || 'Failed to process content')
  }

  return response.json()
}

/**
 * Retrieve processed content by ID.
 * 
 * @param {string} contentId - UUID of the content
 * @param {boolean} compress - Whether to request compressed content
 * @returns {Promise<Object>} Content data
 */
export async function getContent(contentId, compress = false) {
  const url = new URL(`${API_BASE_URL}/api/content/${contentId}`)
  if (compress) {
    url.searchParams.append('compress', 'true')
  }

  const response = await fetch(url)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.details || error.error || 'Failed to retrieve content')
  }

  return response.json()
}

/**
 * Get audio URL for content.
 * 
 * @param {string} contentId - UUID of the content
 * @returns {string} Audio URL
 */
export function getAudioUrl(contentId) {
  return `${API_BASE_URL}/api/content/${contentId}/audio`
}

/**
 * Search for content with filters.
 * 
 * @param {Object} filters - Search filters
 * @param {string} filters.language - Filter by language
 * @param {number} filters.grade - Filter by grade level
 * @param {string} filters.subject - Filter by subject
 * @param {number} filters.limit - Maximum results
 * @param {number} filters.offset - Pagination offset
 * @returns {Promise<Object>} Search results
 */
export async function searchContent(filters = {}) {
  const url = new URL(`${API_BASE_URL}/api/content/search`)
  
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== null && value !== undefined && value !== '') {
      url.searchParams.append(key, value)
    }
  })

  const response = await fetch(url)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.details || error.error || 'Failed to search content')
  }

  return response.json()
}

/**
 * Create batch download package for offline access.
 * 
 * @param {Array<string>} contentIds - List of content IDs (max 50)
 * @param {boolean} includeAudio - Whether to include audio files
 * @returns {Promise<Object>} Batch package information
 */
export async function createBatchDownload(contentIds, includeAudio = true) {
  const response = await fetch(`${API_BASE_URL}/api/batch-download`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      content_ids: contentIds,
      include_audio: includeAudio,
    }),
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.details || error.error || 'Failed to create batch download')
  }

  return response.json()
}

/**
 * Check API health status.
 * 
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new Error('Health check failed')
  }

  return response.json()
}

/**
 * Handle API errors with user-friendly messages.
 * 
 * @param {Error} error - Error object
 * @returns {string} User-friendly error message
 */
export function formatApiError(error) {
  if (error.message.includes('Failed to fetch')) {
    return 'Unable to connect to server. Please check your internet connection.'
  }
  
  if (error.message.includes('Validation failed')) {
    return 'Invalid input. Please check your form data and try again.'
  }
  
  if (error.message.includes('Processing failed')) {
    return 'Content processing failed. Please try again or contact support.'
  }
  
  return error.message || 'An unexpected error occurred. Please try again.'
}

export default {
  processContent,
  getContent,
  getAudioUrl,
  searchContent,
  createBatchDownload,
  checkHealth,
  formatApiError,
}
