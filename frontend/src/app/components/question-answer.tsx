import { useState, useRef, useEffect, FormEvent } from 'react';
import { Send, Loader2, User, Bot } from 'lucide-react';
import { askQuestion, AskResponse } from '@/services/api';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  sources?: AskResponse['sources'];
  timestamp: Date;
}

interface QuestionAnswerProps {
  onSourcesUpdate?: (sources: AskResponse['sources']) => void;
}

export function QuestionAnswer({ onSourcesUpdate }: QuestionAnswerProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await askQuestion(inputValue);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      
      // Update sources in parent component if callback provided
      if (onSourcesUpdate && response.sources) {
        onSourcesUpdate(response.sources);
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: error instanceof Error ? error.message : 'Failed to get answer. Please try again.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-md overflow-hidden flex flex-col h-[600px]">
        {/* Header */}
        <div className="p-4 border-b bg-gray-50">
          <h2 className="text-xl">Ask Questions</h2>
          <p className="text-sm text-gray-600">Ask anything about your uploaded documents</p>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-gray-500">
                <Bot className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p className="text-lg">Start a conversation</p>
                <p className="text-sm">Ask questions about your documents</p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.type === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.type === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-blue-600" />
                  </div>
                )}
                
                <div
                  className={`
                    max-w-[70%] rounded-lg p-4
                    ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }
                  `}
                >
                  <p className="whitespace-pre-wrap break-words">{message.content}</p>
                  
                  {message.sources && message.sources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-300">
                      <p className="text-xs text-gray-600 mb-1">Sources: {message.sources.length}</p>
                    </div>
                  )}
                </div>

                {message.type === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
                    <User className="w-5 h-5 text-white" />
                  </div>
                )}
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                <Bot className="w-5 h-5 text-blue-600" />
              </div>
              <div className="bg-gray-100 rounded-lg p-4">
                <Loader2 className="w-5 h-5 animate-spin text-gray-600" />
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t bg-gray-50">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask a question..."
              disabled={isLoading}
              className="
                flex-1 px-4 py-3 rounded-lg border border-gray-300
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                disabled:opacity-50 disabled:cursor-not-allowed
              "
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="
                px-6 py-3 bg-blue-600 text-white rounded-lg
                hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed
                transition-colors flex items-center gap-2
              "
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
