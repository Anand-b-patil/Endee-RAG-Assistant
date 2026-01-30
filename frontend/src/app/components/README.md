# Endee RAG Assistant - Frontend Components

## Overview

This is a modern, production-ready frontend for a Retrieval-Augmented Generation (RAG) system powered by the Endee vector database.

## Components

### 1. DocumentUpload (`document-upload.tsx`)
- **Features:**
  - Drag-and-drop file upload
  - File type validation (PDF, TXT)
  - Upload progress with loading spinner
  - Success/error notifications
  - File preview before upload

### 2. QuestionAnswer (`question-answer.tsx`)
- **Features:**
  - Chat-style interface
  - Real-time conversation history
  - User and assistant message bubbles
  - Auto-scroll to latest messages
  - Loading indicators
  - Error handling

### 3. SourcesPanel (`sources-panel.tsx`)
- **Features:**
  - Collapsible source items
  - Display retrieved document chunks
  - Metadata display for each source
  - Clean, organized layout

## API Integration

The frontend integrates with a REST API backend through the `api.ts` service:

### API Endpoints:

**1. Upload Document**
- **Endpoint:** `POST /upload`
- **Content-Type:** `multipart/form-data`
- **Request:** File (PDF or TXT)
- **Response:**
  ```json
  {
    "message": "Document uploaded successfully",
    "filename": "example.pdf"
  }
  ```

**2. Ask Question**
- **Endpoint:** `POST /ask`
- **Content-Type:** `application/json`
- **Request:**
  ```json
  {
    "question": "What is the main topic?"
  }
  ```
- **Response:**
  ```json
  {
    "answer": "The main topic is...",
    "sources": [
      {
        "text": "Retrieved text chunk...",
        "metadata": {
          "page": 1,
          "source": "document.pdf"
        }
      }
    ]
  }
  ```

## Configuration

Set your backend API URL in `.env`:

```env
VITE_API_BASE_URL=http://localhost:5000
```

## Tech Stack

- **React 18** - UI Framework
- **TypeScript** - Type Safety
- **Axios** - HTTP Client
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Vite** - Build Tool

## Usage

```tsx
import { DocumentUpload } from '@/app/components/document-upload';
import { QuestionAnswer } from '@/app/components/question-answer';
import { SourcesPanel } from '@/app/components/sources-panel';

function App() {
  const [sources, setSources] = useState([]);

  return (
    <div>
      <DocumentUpload onUploadSuccess={(filename) => console.log(filename)} />
      <QuestionAnswer onSourcesUpdate={setSources} />
      <SourcesPanel sources={sources} />
    </div>
  );
}
```

## Error Handling

All components include comprehensive error handling:
- Network errors
- File validation errors
- API response errors
- User-friendly error messages

## Accessibility

- Keyboard navigation support
- ARIA labels for screen readers
- Focus management
- Semantic HTML elements

## Responsive Design

All components are fully responsive and work seamlessly across:
- Desktop (1280px+)
- Tablet (768px - 1279px)
- Mobile (< 768px)
