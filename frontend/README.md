# Multilingual Education Platform - Frontend

React-based frontend application for the Multilingual Education Content Platform with comprehensive accessibility features.

## Features

- **Content Upload**: Text input and PDF upload interface
- **Content Customization**: Language, grade level, subject, and format selection
- **Content Viewer**: Display processed content with text and audio playback
- **Offline Support**: Download and manage content for offline access
- **Accessibility**: WCAG 2.0 AA compliant with multiple accessibility features

## Accessibility Features

### OpenDyslexic Font
- Toggle option for dyslexia-friendly font
- Preference saved in local storage

### ARIA Support
- Comprehensive ARIA labels on all interactive elements
- Proper semantic HTML structure
- Screen reader compatible

### Keyboard Navigation
- Full keyboard navigation support
- Focus indicators on all interactive elements
- Skip to main content link
- Keyboard shortcuts documented in accessibility settings

### Additional Features
- Adjustable text size (small, medium, large, extra-large)
- High contrast mode
- Reduced motion support for users with vestibular disorders
- Responsive design for mobile and desktop

## Setup

### Prerequisites
- Node.js 18+ and npm

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

### Accessibility Testing

Run Pa11y accessibility validation:

```bash
npm run a11y
```

Note: The development server must be running for Pa11y tests to work.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── AccessibilitySettings.jsx
│   ├── pages/
│   │   ├── UploadPage.jsx
│   │   ├── ContentViewerPage.jsx
│   │   └── OfflineContentPage.jsx
│   ├── utils/
│   │   └── keyboardNavigation.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── public/
│   └── fonts/
├── index.html
├── package.json
├── vite.config.js
├── tailwind.config.js
└── .pa11yci.json
```

## API Integration

The frontend connects to the backend API at `http://localhost:5000` (configurable in `vite.config.js`).

### Endpoints Used

- `POST /api/process-content` - Process educational content
- `GET /api/content/:id` - Retrieve specific content
- `GET /api/content/search` - Search content with filters
- `POST /api/batch-download` - Download content for offline access

## Keyboard Shortcuts

- **Tab** - Navigate between interactive elements
- **Enter** or **Space** - Activate buttons and links
- **Escape** - Close modals and dialogs
- **Arrow Keys** - Navigate within components

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Accessibility Standards

This application follows WCAG 2.0 Level AA guidelines:

- Perceivable: Text alternatives, adaptable content, distinguishable elements
- Operable: Keyboard accessible, sufficient time, navigable
- Understandable: Readable, predictable, input assistance
- Robust: Compatible with assistive technologies

## License

Part of the Multilingual Education Content Platform project.
