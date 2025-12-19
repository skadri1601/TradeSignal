import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { aiApi } from '../../api/ai';
import { ThinkingDots } from '../common/AISkeleton';
import { Send, Sparkles } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: {
    provider?: string;
    response_length?: number;
    tokens_used?: number;
    max_tokens?: number;
    truncated?: boolean;
    safety_blocked?: boolean;
    finish_reason?: string;
    block_reason?: string;
    error?: boolean;
    errors?: string[];
  };
}

export default function AIChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: "Hello! I'm your AI-powered insider trading analyst. I have access to comprehensive insider trading data and can help you understand patterns, trends, and specific company activity. What would you like to know?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const [showScrollIndicator, setShowScrollIndicator] = useState(false);
  const [isNearBottom, setIsNearBottom] = useState(true);

  // Auto-scroll to bottom when new messages arrive (only if user is near bottom)
  useEffect(() => {
    if (isNearBottom && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [messages, isNearBottom]);

  // Detect scroll position and show/hide fade indicator
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight;

      setIsNearBottom(distanceFromBottom < 100);
      setShowScrollIndicator(distanceFromBottom > 20);
    };

    container.addEventListener('scroll', handleScroll);
    handleScroll();

    return () => container.removeEventListener('scroll', handleScroll);
  }, []);

  // Check if content is scrollable
  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container) return;

    const isScrollable = container.scrollHeight > container.clientHeight;
    setShowScrollIndicator(isScrollable && !isNearBottom);
  }, [messages, isNearBottom]);

  const askMutation = useMutation({
    mutationFn: (question: string) => aiApi.askQuestion(question),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer,
          timestamp: new Date(data.timestamp),
          metadata: data.response_metadata,
        },
      ]);
    },
    onError: (error: any) => {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      const isUnavailable = errorMessage.includes('503') || errorMessage.includes('unavailable') || errorMessage.includes('AI service');
      
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: isUnavailable 
            ? "I'm sorry, the AI service is currently unavailable. Please ensure GEMINI_API_KEY is configured in the backend and ENABLE_AI_INSIGHTS is set to true."
            : `I'm sorry, I encountered an error: ${errorMessage}. Please try again.`,
          timestamp: new Date(),
        },
      ]);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || askMutation.isPending) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    askMutation.mutate(input.trim());
    setInput('');
  };

  const suggestedQuestions = [
    "Which companies have the most insider buying this month?",
    "What are the biggest trades this week?",
    "Explain NVDA's recent insider activity",
    "Show me recent CEO purchases over $1M",
  ];

  return (
    <div className="bg-gray-900/50 backdrop-blur-sm rounded-2xl shadow-lg border border-white/10 max-w-4xl mx-auto overflow-hidden">
      <div className="flex flex-col min-h-[400px] max-h-[80vh] h-[600px]">
        {/* Header */}
        <div className="p-6 border-b border-white/10 bg-black/20">
          <div className="flex items-center space-x-2 mb-1">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <h2 className="text-xl font-bold text-white">AI Chat Assistant</h2>
          </div>
          <p className="text-sm text-gray-400">
            Ask questions about insider trading data and get AI-powered answers
          </p>
        </div>

        {/* Messages */}
        <div
          ref={messagesContainerRef}
          className="flex-1 overflow-y-auto space-y-6 p-6 relative"
        >
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-5 py-4 shadow-md ${
                  message.role === 'user'
                    ? 'bg-purple-600 text-white rounded-br-none'
                    : 'bg-white/10 text-gray-200 rounded-bl-none border border-white/5'
                }`}
              >
                <p className="whitespace-pre-wrap leading-relaxed text-sm md:text-base">{message.content}</p>
                
                {/* Response Quality Warnings */}
                {message.role === 'assistant' && message.metadata && (
                  <div className="mt-3 space-y-1">
                    {message.metadata.truncated && (
                      <div className="flex items-start space-x-2 p-2 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                        <span className="text-yellow-400 text-xs">⚠️</span>
                        <p className="text-xs text-yellow-300">
                          Response may be incomplete. LUNA's answer was cut off due to length limits.
                          {message.metadata.tokens_used && ` (${message.metadata.tokens_used}/${message.metadata.max_tokens} tokens used)`}
                        </p>
                      </div>
                    )}
                    {message.metadata.safety_blocked && (
                      <div className="flex items-start space-x-2 p-2 bg-red-500/10 border border-red-500/20 rounded-lg">
                        <span className="text-red-400 text-xs">🚫</span>
                        <p className="text-xs text-red-300">
                          Response was restricted by safety filters.
                          {message.metadata.block_reason && ` Reason: ${message.metadata.block_reason}`}
                        </p>
                      </div>
                    )}
                    {message.metadata.error && (
                      <div className="flex items-start space-x-2 p-2 bg-red-500/10 border border-red-500/20 rounded-lg">
                        <span className="text-red-400 text-xs">❌</span>
                        <p className="text-xs text-red-300">
                          Error generating response.
                          {message.metadata.errors && message.metadata.errors.length > 0 && (
                            <span> Details: {message.metadata.errors.join(', ')}</span>
                          )}
                        </p>
                      </div>
                    )}
                  </div>
                )}
                
                <p className={`text-[10px] mt-2 opacity-70 ${message.role === 'user' ? 'text-purple-200' : 'text-gray-400'}`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}
          {askMutation.isPending && (
            <div className="flex justify-start">
              <div className="bg-white/10 text-gray-200 rounded-2xl rounded-bl-none px-5 py-4 max-w-[85%] border border-white/5">
                <div className="space-y-2 mb-2 w-64">
                  <div className="h-2 bg-white/20 rounded animate-pulse w-full"></div>
                  <div className="h-2 bg-white/20 rounded animate-pulse w-[80%]"></div>
                  <div className="h-2 bg-white/20 rounded animate-pulse w-[60%]"></div>
                </div>
                <div className="flex items-center space-x-2 mt-3">
                  <span className="text-xs text-purple-300 font-medium">LUNA is thinking</span>
                  <ThinkingDots />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Fade gradient overlay when scrollable */}
        {showScrollIndicator && (
          <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-gray-900 to-transparent pointer-events-none" />
        )}

        {/* Suggested Questions */}
        {messages.length === 1 && (
          <div className="px-6 pb-2">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Suggested questions:</p>
            <div className="flex flex-wrap gap-2">
              {suggestedQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => setInput(question)}
                  className="text-sm bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white px-4 py-2 rounded-xl transition-all border border-white/5 hover:border-purple-500/30"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="p-4 bg-black/20 border-t border-white/10">
          <form onSubmit={handleSubmit} className="flex space-x-3 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about insider trades..."
              className="flex-1 px-5 py-3 bg-black/50 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all pr-12"
              disabled={askMutation.isPending}
            />
            <button
              type="submit"
              disabled={!input.trim() || askMutation.isPending}
              className="absolute right-2 top-1.5 p-1.5 bg-purple-600 text-white rounded-lg hover:bg-purple-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-500/20"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}