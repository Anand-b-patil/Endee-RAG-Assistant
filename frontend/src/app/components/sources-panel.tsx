import { FileText, ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';
import { AskResponse } from '@/services/api';

interface SourcesPanelProps {
  sources: AskResponse['sources'];
}

interface SourceItemProps {
  source: AskResponse['sources'][0];
  index: number;
}

function SourceItem({ source, index }: SourceItemProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors"
      >
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-blue-600" />
          <span className="text-sm">Source {index + 1}</span>
        </div>
        {isExpanded ? (
          <ChevronDown className="w-5 h-5 text-gray-600" />
        ) : (
          <ChevronRight className="w-5 h-5 text-gray-600" />
        )}
      </button>
      
      {isExpanded && (
        <div className="p-4 bg-white border-t border-gray-200">
          <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
            {source.text}
          </p>
          
          {source.metadata && Object.keys(source.metadata).length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <p className="text-xs text-gray-500 mb-2">Metadata:</p>
              <div className="space-y-1">
                {Object.entries(source.metadata).map(([key, value]) => (
                  <div key={key} className="flex gap-2 text-xs">
                    <span className="text-gray-600">{key}:</span>
                    <span className="text-gray-900">{String(value)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export function SourcesPanel({ sources }: SourcesPanelProps) {
  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="mb-4">
          <h2 className="text-xl">Retrieved Sources</h2>
          <p className="text-sm text-gray-600">
            {sources.length > 0
              ? `${sources.length} relevant document ${sources.length === 1 ? 'chunk' : 'chunks'} found`
              : 'No sources available'}
          </p>
        </div>

        {sources.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-3 text-gray-400" />
            <p>Ask a question to see relevant sources</p>
          </div>
        ) : (
          <div className="space-y-3">
            {sources.map((source, index) => (
              <SourceItem key={index} source={source} index={index} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
