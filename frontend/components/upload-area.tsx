"use client";

import { useState } from "react";
import { Upload, FileText, CheckCircle, X } from "lucide-react";
import { useDropzone } from "react-dropzone";

export function UploadArea() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      "application/pdf": [".pdf"]
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        handleFileUpload(acceptedFiles[0]);
      }
    }
  });

  const handleFileUpload = async (selectedFile: File) => {
    setFile(selectedFile);
    setIsUploading(true);
    
    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsUploading(false);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const removeFile = () => {
    setFile(null);
    setUploadProgress(0);
  };

  const processFile = async () => {
    if (!file) return;
    
    // Here you would call your backend API
    console.log("Processing file:", file.name);
    
    // Simulate processing
    setIsUploading(true);
    setTimeout(() => {
      setIsUploading(false);
      alert(`File ${file.name} processed successfully!`);
    }, 1500);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div
        {...getRootProps()}
        className={`
          border-3 border-dashed rounded-2xl p-12 text-center cursor-pointer
          transition-all duration-300
          ${isDragActive 
            ? "border-blue-500 bg-blue-50" 
            : "border-gray-300 hover:border-blue-400 hover:bg-gray-50"
          }
        `}
      >
        <input {...getInputProps()} />
        
        {!file ? (
          <>
            <div className="flex justify-center mb-6">
              <div className="p-4 bg-blue-100 rounded-full">
                <Upload className="w-12 h-12 text-blue-600" />
              </div>
            </div>
            
            <h3 className="text-2xl font-semibold text-gray-800 mb-3">
              {isDragActive ? "Drop your PDF here" : "Drag & drop your PDF"}
            </h3>
            
            <p className="text-gray-600 mb-6">
              or click to browse files
            </p>
            
            <div className="text-sm text-gray-500">
              Supports PDF files up to 100MB
            </div>
          </>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-center space-x-4">
              <div className="p-3 bg-green-100 rounded-full">
                <FileText className="w-8 h-8 text-green-600" />
              </div>
              <div className="text-left">
                <h4 className="font-semibold text-gray-800">{file.name}</h4>
                <p className="text-sm text-gray-600">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB
                </p>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeFile();
                }}
                className="p-2 hover:bg-gray-100 rounded-full"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {isUploading ? (
              <div className="space-y-2">
                <div className="w-full bg-gray-200 rounded-full h-2.5">
                  <div 
                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-sm text-gray-600">
                  {uploadProgress < 100 ? "Uploading..." : "Processing..."}
                </p>
              </div>
            ) : (
              <div className="flex items-center justify-center space-x-4">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <span className="text-green-600 font-medium">Ready to process</span>
              </div>
            )}
          </div>
        )}
      </div>

      {file && !isUploading && (
        <div className="mt-8 flex flex-wrap gap-4 justify-center">
          <button
            onClick={processFile}
            className="px-8 py-3 bg-blue-600 text-white rounded-full font-semibold hover:bg-blue-700 transition-colors"
          >
            Convert to Word
          </button>
          
          <button
            onClick={processFile}
            className="px-8 py-3 bg-white text-blue-600 border border-blue-600 rounded-full font-semibold hover:bg-blue-50 transition-colors"
          >
            Chat with PDF
          </button>
          
          <button
            onClick={processFile}
            className="px-8 py-3 bg-gray-100 text-gray-700 rounded-full font-semibold hover:bg-gray-200 transition-colors"
          >
            Compress PDF
          </button>
          
          <button
            onClick={processFile}
            className="px-8 py-3 bg-gray-100 text-gray-700 rounded-full font-semibold hover:bg-gray-200 transition-colors"
          >
            Extract Text
          </button>
        </div>
      )}

      <div className="mt-8 text-center text-sm text-gray-500">
        <p>Trusted by 10,000+ professionals • Bank-level security • No file limits</p>
      </div>
    </div>
  );
}