import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { processContent, formatApiError } from '../utils/api'

function UploadPage() {
  const navigate = useNavigate()
  const [inputType, setInputType] = useState('text')
  const [textContent, setTextContent] = useState('')
  const [pdfFile, setPdfFile] = useState(null)
  const [targetLanguage, setTargetLanguage] = useState('Hindi')
  const [gradeLevel, setGradeLevel] = useState(8)
  const [subject, setSubject] = useState('Mathematics')
  const [outputFormat, setOutputFormat] = useState('both')
  const [isProcessing, setIsProcessing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const languages = ['Hindi', 'Tamil', 'Telugu', 'Bengali', 'Marathi']
  const subjects = ['Mathematics', 'Science', 'Social Studies', 'English', 'History']
  const grades = Array.from({ length: 8 }, (_, i) => i + 5)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file && file.type === 'application/pdf') {
      setPdfFile(file)
      setError(null)
    } else {
      setError('Please select a valid PDF file')
      setPdfFile(null)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsProcessing(true)
    setError(null)
    setResult(null)

    try {
      // Validate input
      if (inputType === 'text') {
        if (!textContent.trim()) {
          throw new Error('Please enter some text content')
        }
      } else {
        if (!pdfFile) {
          throw new Error('Please select a PDF file')
        }
      }

      // Prepare request data
      const requestData = {
        input_data: inputType === 'text' ? textContent : pdfFile.name, // For now, use filename for PDF
        target_language: targetLanguage,
        grade_level: gradeLevel,
        subject: subject,
        output_format: outputFormat,
      }

      // Process content through API
      const response = await processContent(requestData)
      
      setResult(response)
      
      // Automatically navigate to content viewer after 2 seconds
      setTimeout(() => {
        navigate(`/content/${response.id}`)
      }, 2000)
      
    } catch (err) {
      setError(formatApiError(err))
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Upload Educational Content</h1>
      
      <form 
        onSubmit={handleSubmit} 
        className="bg-white rounded-lg shadow-md p-6"
        aria-label="Content upload form"
      >
        <fieldset className="mb-6">
          <legend className="text-lg font-semibold mb-3">Input Type</legend>
          
          <div className="flex space-x-4">
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="inputType"
                value="text"
                checked={inputType === 'text'}
                onChange={(e) => setInputType(e.target.value)}
                className="mr-2"
                aria-label="Text input"
              />
              <span>Text Input</span>
            </label>
            
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="inputType"
                value="pdf"
                checked={inputType === 'pdf'}
                onChange={(e) => setInputType(e.target.value)}
                className="mr-2"
                aria-label="PDF upload"
              />
              <span>PDF Upload</span>
            </label>
          </div>
        </fieldset>

        {inputType === 'text' ? (
          <div className="mb-6">
            <label htmlFor="text-content" className="block text-sm font-medium mb-2">
              Content Text
            </label>
            <textarea
              id="text-content"
              value={textContent}
              onChange={(e) => setTextContent(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="8"
              placeholder="Enter educational content here..."
              aria-required="true"
              aria-describedby="text-content-help"
            />
            <p id="text-content-help" className="text-sm text-gray-600 mt-1">
              Enter the educational content you want to process
            </p>
          </div>
        ) : (
          <div className="mb-6">
            <label htmlFor="pdf-file" className="block text-sm font-medium mb-2">
              PDF File
            </label>
            <input
              type="file"
              id="pdf-file"
              accept=".pdf"
              onChange={handleFileChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              aria-required="true"
              aria-describedby="pdf-file-help"
            />
            <p id="pdf-file-help" className="text-sm text-gray-600 mt-1">
              Upload a PDF file containing educational content
            </p>
            {pdfFile && (
              <p className="text-sm text-green-600 mt-2" role="status">
                Selected: {pdfFile.name}
              </p>
            )}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label htmlFor="target-language" className="block text-sm font-medium mb-2">
              Target Language
            </label>
            <select
              id="target-language"
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              aria-required="true"
            >
              {languages.map(lang => (
                <option key={lang} value={lang}>{lang}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="grade-level" className="block text-sm font-medium mb-2">
              Grade Level
            </label>
            <select
              id="grade-level"
              value={gradeLevel}
              onChange={(e) => setGradeLevel(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              aria-required="true"
            >
              {grades.map(grade => (
                <option key={grade} value={grade}>Grade {grade}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="subject" className="block text-sm font-medium mb-2">
              Subject
            </label>
            <select
              id="subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              aria-required="true"
            >
              {subjects.map(subj => (
                <option key={subj} value={subj}>{subj}</option>
              ))}
            </select>
          </div>

          <div>
            <label htmlFor="output-format" className="block text-sm font-medium mb-2">
              Output Format
            </label>
            <select
              id="output-format"
              value={outputFormat}
              onChange={(e) => setOutputFormat(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              aria-required="true"
            >
              <option value="text">Text Only</option>
              <option value="audio">Audio Only</option>
              <option value="both">Text + Audio</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={isProcessing}
          className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-semibold"
          aria-label={isProcessing ? 'Processing content' : 'Process content'}
        >
          {isProcessing ? 'Processing...' : 'Process Content'}
        </button>
      </form>

      {error && (
        <div 
          className="mt-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg"
          role="alert"
          aria-live="polite"
        >
          <strong className="font-semibold">Error: </strong>
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div 
          className="mt-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg"
          role="status"
          aria-live="polite"
        >
          <strong className="font-semibold">Success! </strong>
          <span>Content processed successfully. ID: {result.id}</span>
          <a 
            href={`/content/${result.id}`}
            className="block mt-2 text-blue-600 hover:underline"
            aria-label={`View processed content ${result.id}`}
          >
            View Content →
          </a>
        </div>
      )}
    </div>
  )
}

export default UploadPage
