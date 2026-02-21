"use client";

import { useState, useEffect } from 'react';
import { 
  Upload, 
  FileText, 
  MessageSquare, 
  BarChart, 
  Settings,
  Download,
  Trash2,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { useAuth, ProtectedRoute } from '@/contexts/auth-context';
import { api, formatFileSize, formatDate } from '@/lib/api';
import { UploadArea } from '@/components/upload-area';
import { UsageStats } from '@/components/usage-stats';

interface PDFFile {
  id: string;
  filename: string;
  size: number;
  pages: number;
  uploaded_at: string;
  processed: boolean;
}

interface UsageData {
  conversions_used: number;
  conversions_limit: number;
  ai_questions_used: number;
  ai_questions_limit: number;
  subscription_tier: string;
  reset_date: string;
}

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const [files, setFiles] = useState<PDFFile[]>([]);
  const [usage, setUsage] = useState<UsageData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'files' | 'chat' | 'usage'>('files');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [filesResponse, usageResponse] = await Promise.all([
        api.listFiles(),
        api.getUsage()
      ]);

      if (filesResponse.data) {
        setFiles(filesResponse.data);
      }

      if (usageResponse.data) {
        setUsage(usageResponse.data);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    try {
      const response = await api.uploadPdf(file);
      if (response.data) {
        await loadData(); // Refresh file list
      }
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleDeleteFile = async (fileId: string) => {
    if (!confirm('Are you sure you want to delete this file?')) return;

    try {
      await api.deleteFile(fileId);
      setFiles(files.filter(file => file.id !== fileId));
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };

  const handleConvert = async (fileId: string, format: string) => {
    try {
      const response = await api.convertPdf(fileId, format);
      if (response.data?.content) {
        // Convert base64 to blob and download
        const byteCharacters = atob(response.data.content);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: 'application/octet-stream' });
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = response.data.filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Conversion failed:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-600 rounded-xl">
                  <FileText className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">PDF Genius</h1>
                  <p className="text-sm text-gray-500">Welcome back, {user?.username}</p>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                <div className="text-right">
                  <p className="font-medium text-gray-900">{user?.subscription_tier} Plan</p>
                  <p className="text-sm text-gray-500">
                    {usage && `${usage.conversions_remaining} conversions remaining`}
                  </p>
                </div>
                <button
                  onClick={() => logout()}
                  className="px-4 py-2 text-gray-700 hover:text-blue-600 font-medium"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Sidebar */}
            <div className="lg:col-span-1">
              <nav className="bg-white rounded-2xl shadow-sm p-4">
                <div className="space-y-2">
                  <button
                    onClick={() => setActiveTab('files')}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-colors ${
                      activeTab === 'files'
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <FileText className="w-5 h-5" />
                    <span className="font-medium">My Files</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('chat')}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-colors ${
                      activeTab === 'chat'
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <MessageSquare className="w-5 h-5" />
                    <span className="font-medium">Chat Sessions</span>
                  </button>

                  <button
                    onClick={() => setActiveTab('usage')}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-colors ${
                      activeTab === 'usage'
                        ? 'bg-blue-50 text-blue-600'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <BarChart className="w-5 h-5" />
                    <span className="font-medium">Usage</span>
                  </button>

                  <button className="w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-gray-700 hover:bg-gray-50 transition-colors">
                    <Settings className="w-5 h-5" />
                    <span className="font-medium">Settings</span>
                  </button>
                </div>

                {/* Upload Area */}
                <div className="mt-8">
                  <div className="border-2 border-dashed border-gray-300 rounded-2xl p-6 text-center hover:border-blue-400 transition-colors cursor-pointer">
                    <Upload className="w-8 h-8 text-gray-400 mx-auto mb-3" />
                    <p className="text-sm font-medium text-gray-700">Upload PDF</p>
                    <p className="text-xs text-gray-500 mt-1">Drag & drop or click</p>
                  </div>
                </div>

                {/* Usage Stats */}
                {usage && (
                  <div className="mt-8">
                    <UsageStats usage={usage} />
                  </div>
                )}
              </nav>
            </div>

            {/* Main Content */}
            <div className="lg:col-span-3">
              {activeTab === 'files' && (
                <div className="space-y-6">
                  <div className="bg-white rounded-2xl shadow-sm p-6">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload New PDF</h2>
                    <UploadArea onUpload={handleFileUpload} />
                  </div>

                  <div className="bg-white rounded-2xl shadow-sm p-6">
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-2xl font-bold text-gray-900">My Files</h2>
                      <span className="text-gray-500">{files.length} files</span>
                    </div>

                    {files.length === 0 ? (
                      <div className="text-center py-12">
                        <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No files yet</h3>
                        <p className="text-gray-500">Upload your first PDF to get started</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {files.map((file) => (
                          <div
                            key={file.id}
                            className="flex items-center justify-between p-4 border border-gray-200 rounded-xl hover:border-blue-300 transition-colors"
                          >
                            <div className="flex items-center space-x-4">
                              <div className="p-3 bg-blue-50 rounded-xl">
                                <FileText className="w-6 h-6 text-blue-600" />
                              </div>
                              <div>
                                <h4 className="font-medium text-gray-900">{file.filename}</h4>
                                <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                                  <span>{formatFileSize(file.size)}</span>
                                  <span>•</span>
                                  <span>{file.pages} pages</span>
                                  <span>•</span>
                                  <span className="flex items-center">
                                    <Clock className="w-3 h-3 mr-1" />
                                    {formatDate(file.uploaded_at)}
                                  </span>
                                </div>
                              </div>
                            </div>

                            <div className="flex items-center space-x-2">
                              <div className="flex space-x-1">
                                <button
                                  onClick={() => handleConvert(file.id, 'docx')}
                                  className="px-3 py-1.5 text-sm bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                                >
                                  DOCX
                                </button>
                                <button
                                  onClick={() => handleConvert(file.id, 'excel')}
                                  className="px-3 py-1.5 text-sm bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors"
                                >
                                  Excel
                                </button>
                                <button
                                  onClick={() => handleConvert(file.id, 'jpg')}
                                  className="px-3 py-1.5 text-sm bg-purple-50 text-purple-600 rounded-lg hover:bg-purple-100 transition-colors"
                                >
                                  JPG
                                </button>
                              </div>

                              <button
                                onClick={() => handleDeleteFile(file.id)}
                                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              >
                                <Trash2 className="w-5 h-5" />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'chat' && (
                <div className="bg-white rounded-2xl shadow-sm p-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Chat Sessions</h2>
                  <div className="text-center py-12">
                    <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No chat sessions yet</h3>
                    <p className="text-gray-500 mb-6">Upload a PDF and start chatting with it</p>
                    <button className="px-6 py-3 bg-blue-600 text-white rounded-full font-semibold hover:bg-blue-700 transition-colors">
                      Start New Chat
                    </button>
                  </div>
                </div>
              )}

              {activeTab === 'usage' && usage && (
                <div className="space-y-6">
                  <div className="bg-white rounded-2xl shadow-sm p-6">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">Usage Statistics</h2>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Conversions */}
                      <div className="border border-gray-200 rounded-xl p-6">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="font-semibold text-gray-900">PDF Conversions</h3>
                          <span className="text-sm font-medium text-blue-600">
                            {usage.conversions_used} / {usage.conversions_limit}
                          </span>
                        </div>
                        
                        <div className="mb-4">
                          <div className="w-full bg-gray-200 rounded-full h-2.5">
                            <div 
                              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                              style={{ 
                                width: `${Math.min(100, (usage.conversions_used / usage.conversions_limit) * 100)}%` 
                              }}
                            />
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between text-sm text-gray-600">
                          <span>Used: {usage.conversions_used}</span>
                          <span>Remaining: {usage.conversions_remaining}</span>
                        </div>
                      </div>

                      {/* AI Questions */}
                      <div className="border border-gray-200 rounded-xl p-6">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="font-semibold text-gray-900">AI Questions</h3>
                          <span className="text-sm font-medium text-purple-600">
                            {usage.ai_questions_used} / {usage.ai_questions_limit}
                          </span>
                        </div>
                        
                        <div className="mb-4">
                          <div className="w-full bg-gray-200 rounded-full h-2.5">
                            <div 
                              className="bg-purple-600 h-2.5 rounded-full transition-all duration-300"
                              style={{ 
                                width: `${Math.min(100, (usage.ai_questions_used / usage.ai_questions_limit) * 100)}%` 
                              }}
                            />
                          </div>
                        </div>
                        
                        <div className="flex items-center justify-between text-sm text-gray-600">
                          <span>Used: {usage.ai_questions_used}</span>
                          <span>Remaining: {usage.ai_questions_limit - usage.ai_questions_used}</span>
                        </div>
                      </div>
                    </div>

                    {/* Reset Info */}
                    <div className="mt-8 pt-8 border-t border-gray-200">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <Clock className="w-5 h-5 text-gray-400" />
                          <div>
                            <p className="font-medium text-gray-900">Usage resets on</p>
                            <p className="text-sm text-gray-500">
                              {new Date(usage.reset_date).toLocaleDateString('en-US', {
                                month: 'long',
                                day: 'numeric',
                                year: 'numeric'
                              })}
                            </p>
                          </div>
                        </div>
                        
                        <button className="px-6 py-2 bg-blue-600 text-white rounded-full font-semibold hover:bg-blue-700 transition-colors">
                          Upgrade Plan
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Recent Activity */}
                  <div className="bg-white rounded-2xl shadow-sm p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-6">Recent Activity</h3>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                        <div className="flex items-center space-x-3">
                          <CheckCircle className="w-5 h-5 text-green-500" />
                          <div>
                            <p className="font-medium text-gray-900">PDF converted to DOCX</p>
                            <p className="text-sm text-gray-500">2 hours ago</p>
                          </div>
                        </div>
                        <span className="text-sm text-gray-500">-1 conversion</span>
                      </div>

                      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                        <div className="flex items-center space-x-3">
                          <MessageSquare className="w-5 h-5 text-purple-500" />
                          <div>
                            <p className="font-medium text-gray-900">AI chat session</p>
                            <p className="text-sm text-gray-500">Yesterday</p>
                          </div>
                        </div>
                        <span className="text-sm text-gray-500">-1 AI question</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}