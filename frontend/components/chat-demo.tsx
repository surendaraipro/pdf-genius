"use client";

import { useState } from "react";
import { Send, Bot, User, Sparkles, Download } from "lucide-react";

type Message = {
  id: number;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
};

const sampleQuestions = [
  "Summarize this document in 3 bullet points",
  "What are the key recommendations?",
  "Extract all dates mentioned",
  "Find contradictions in this contract",
  "Convert the table on page 3 to CSV"
];

export function ChatDemo() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your PDF assistant. Upload a PDF or try one of the sample questions below.",
      sender: "bot",
      timestamp: new Date(Date.now() - 300000)
    }
  ]);
  const [input, setInput] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || isProcessing) return;

    const userMessage: Message = {
      id: messages.length + 1,
      text: input,
      sender: "user",
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsProcessing(true);

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        "Based on the document, the main findings suggest a 20% increase in productivity when using AI tools.",
        "The key recommendations are: 1) Implement automation, 2) Train staff on new tools, 3) Monitor results quarterly.",
        "I found dates: January 15, 2024; March 30, 2024; and December 1, 2024.",
        "There's a contradiction on page 5 regarding the payment terms. Section 3.2 conflicts with Appendix A.",
        "I've extracted the table and converted it to CSV. You can download it below."
      ];

      const botMessage: Message = {
        id: messages.length + 2,
        text: responses[Math.floor(Math.random() * responses.length)],
        sender: "bot",
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
      setIsProcessing(false);
    }, 1500);
  };

  const handleSampleQuestion = (question: string) => {
    setInput(question);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Chat Interface */}
        <div className="lg:col-span-2">
          <div className="bg-gray-50 rounded-2xl p-6 h-[400px] flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto mb-4 space-y-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl p-4 ${
                      message.sender === "user"
                        ? "bg-blue-600 text-white rounded-br-none"
                        : "bg-white border border-gray-200 rounded-bl-none"
                    }`}
                  >
                    <div className="flex items-center mb-2">
                      {message.sender === "bot" ? (
                        <Bot className="w-4 h-4 mr-2 text-purple-600" />
                      ) : (
                        <User className="w-4 h-4 mr-2 text-blue-400" />
                      )}
                      <span className="text-xs opacity-75">
                        {message.sender === "bot" ? "PDF Assistant" : "You"}
                      </span>
                      <span className="text-xs opacity-50 ml-2">
                        {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <p className="whitespace-pre-wrap">{message.text}</p>
                    
                    {message.sender === "bot" && message.id > 1 && (
                      <div className="mt-3 pt-3 border-t border-gray-200 border-opacity-20">
                        <button className="text-sm flex items-center text-blue-400 hover:text-blue-300">
                          <Download className="w-3 h-3 mr-1" />
                          Download as CSV
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {isProcessing && (
                <div className="flex justify-start">
                  <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-none p-4">
                    <div className="flex items-center">
                      <Bot className="w-4 h-4 mr-2 text-purple-600" />
                      <span className="text-xs opacity-75">PDF Assistant</span>
                    </div>
                    <div className="flex space-x-1 mt-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="flex space-x-2">
              <div className="flex-1 relative">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask a question about your PDF..."
                  className="w-full p-4 pr-12 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={2}
                />
                <button
                  onClick={handleSend}
                  disabled={isProcessing || !input.trim()}
                  className="absolute right-3 bottom-3 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Sample Questions & Info */}
        <div className="space-y-6">
          <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl p-6">
            <div className="flex items-center mb-4">
              <Sparkles className="w-5 h-5 text-purple-600 mr-2" />
              <h3 className="font-semibold text-gray-900">Try These Questions</h3>
            </div>
            
            <div className="space-y-3">
              {sampleQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleSampleQuestion(question)}
                  className="w-full text-left p-3 bg-white rounded-xl border border-gray-200 hover:border-purple-300 hover:shadow-sm transition-all text-sm"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-gray-50 rounded-2xl p-6">
            <h3 className="font-semibold text-gray-900 mb-4">How It Works</h3>
            <ol className="space-y-4 text-sm text-gray-600">
              <li className="flex items-start">
                <span className="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-600 rounded-full text-xs font-semibold mr-3 flex-shrink-0">1</span>
                Upload your PDF document
              </li>
              <li className="flex items-start">
                <span className="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-600 rounded-full text-xs font-semibold mr-3 flex-shrink-0">2</span>
                Ask questions in natural language
              </li>
              <li className="flex items-start">
                <span className="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-600 rounded-full text-xs font-semibold mr-3 flex-shrink-0">3</span>
                Get instant answers with citations
              </li>
              <li className="flex items-start">
                <span className="flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-600 rounded-full text-xs font-semibold mr-3 flex-shrink-0">4</span>
                Download results in multiple formats
              </li>
            </ol>
          </div>

          <div className="text-center text-sm text-gray-500">
            <p>No PDF uploaded? Try with our sample document</p>
            <button className="mt-2 text-blue-600 font-medium hover:text-blue-700">
              Use Sample PDF →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}