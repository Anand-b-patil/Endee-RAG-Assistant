import { useState, useRef, ChangeEvent, DragEvent } from 'react';
import { Upload, File, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { uploadDocument } from '@/services/api';

interface DocumentUploadProps {
  onUploadSuccess?: (filename: string) => void;
}

export function DocumentUpload({ onUploadSuccess }: DocumentUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (file: File) => {
    // Validate file type
    const validTypes = ['application/pdf', 'text/plain'];
    if (!validTypes.includes(file.type)) {
      setErrorMessage('Please upload a PDF or TXT file');
      setUploadStatus('error');
      return;
    }

    setSelectedFile(file);
    setUploadStatus('idle');
    setErrorMessage('');
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadStatus('idle');
    setErrorMessage('');

    try {
      const response = await uploadDocument(selectedFile);
      setSuccessMessage(response.message || 'Document uploaded successfully');
      setUploadStatus('success');
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      if (onUploadSuccess) {
        onUploadSuccess(response.filename);
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Upload failed');
      setUploadStatus('error');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl mb-4">Upload Documents</h2>
        
        {/* File Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
            transition-colors duration-200
            ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}
            ${uploading ? 'opacity-50 pointer-events-none' : ''}
          `}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt"
            onChange={handleFileChange}
            className="hidden"
            disabled={uploading}
          />
          
          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          
          <p className="text-gray-700 mb-2">
            {selectedFile ? selectedFile.name : 'Drag and drop your file here'}
          </p>
          <p className="text-sm text-gray-500">
            or click to browse (PDF, TXT)
          </p>
        </div>

        {/* Selected File Info */}
        {selectedFile && uploadStatus === 'idle' && (
          <div className="mt-4 flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2">
              <File className="w-5 h-5 text-blue-500" />
              <span className="text-sm text-gray-700">{selectedFile.name}</span>
            </div>
            <button
              onClick={() => setSelectedFile(null)}
              className="text-sm text-red-500 hover:text-red-700"
            >
              Remove
            </button>
          </div>
        )}

        {/* Upload Button */}
        {selectedFile && uploadStatus === 'idle' && (
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="
              w-full mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg
              hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed
              flex items-center justify-center gap-2 transition-colors
            "
          >
            {uploading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Uploading...
              </>
            ) : (
              'Upload Document'
            )}
          </button>
        )}

        {/* Success Message */}
        {uploadStatus === 'success' && (
          <div className="mt-4 flex items-center gap-2 p-4 bg-green-50 border border-green-200 rounded-lg">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            <span className="text-sm text-green-700">{successMessage}</span>
          </div>
        )}

        {/* Error Message */}
        {uploadStatus === 'error' && (
          <div className="mt-4 flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
            <XCircle className="w-5 h-5 text-red-600" />
            <span className="text-sm text-red-700">{errorMessage}</span>
          </div>
        )}
      </div>
    </div>
  );
}
