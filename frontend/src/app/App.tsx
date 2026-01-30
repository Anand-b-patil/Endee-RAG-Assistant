import { useState } from 'react';
import { Database } from 'lucide-react';
import { DocumentUpload } from '@/app/components/document-upload';
import { QuestionAnswer } from '@/app/components/question-answer';
import { SourcesPanel } from '@/app/components/sources-panel';
import { AskResponse } from '@/services/api';

export default function App() {
  const [currentSources, setCurrentSources] = useState<AskResponse['sources']>([]);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);

  const handleUploadSuccess = (filename: string) => {
    setUploadedFiles((prev) => [...prev, filename]);
  };

  const handleSourcesUpdate = (sources: AskResponse['sources']) => {
    setCurrentSources(sources);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Database className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl text-gray-900">Endee RAG Assistant</h1>
              <p className="text-gray-600">
                Ask questions over your documents using high-performance vector search powered by Endee.
              </p>
            </div>
          </div>
          
          {/* Uploaded Files Counter */}
          {uploadedFiles.length > 0 && (
            <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
              <span className="text-sm text-blue-700">
                {uploadedFiles.length} document{uploadedFiles.length !== 1 ? 's' : ''} uploaded
              </span>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Document Upload Section */}
          <section>
            <DocumentUpload onUploadSuccess={handleUploadSuccess} />
          </section>

          {/* Question Answering Section */}
          <section>
            <QuestionAnswer onSourcesUpdate={handleSourcesUpdate} />
          </section>

          {/* Sources Panel */}
          {currentSources.length > 0 && (
            <section>
              <SourcesPanel sources={currentSources} />
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-600">
            Powered by Endee Vector Database | Built with React & Tailwind CSS
          </p>
        </div>
      </footer>
    </div>
  );
}
