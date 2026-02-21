import { 
  FileText, 
  MessageSquare, 
  Merge, 
  Compress, 
  Shield, 
  Zap,
  Download,
  Search,
  BarChart
} from "lucide-react";

const features = [
  {
    icon: <FileText className="w-8 h-8" />,
    title: "PDF Conversion",
    description: "Convert PDFs to Word, Excel, PowerPoint, HTML, and images with perfect formatting.",
    color: "text-blue-600",
    bgColor: "bg-blue-50"
  },
  {
    icon: <MessageSquare className="w-8 h-8" />,
    title: "AI Chat with PDFs",
    description: "Ask questions, get summaries, and extract data from your documents using AI.",
    color: "text-purple-600",
    bgColor: "bg-purple-50"
  },
  {
    icon: <Merge className="w-8 h-8" />,
    title: "Merge & Split",
    description: "Combine multiple PDFs into one or split large documents into smaller files.",
    color: "text-green-600",
    bgColor: "bg-green-50"
  },
  {
    icon: <Compress className="w-8 h-8" />,
    title: "Compress PDFs",
    description: "Reduce file size without losing quality. Perfect for email attachments.",
    color: "text-orange-600",
    bgColor: "bg-orange-50"
  },
  {
    icon: <Shield className="w-8 h-8" />,
    title: "Secure & Private",
    description: "Your files are encrypted and automatically deleted after processing.",
    color: "text-red-600",
    bgColor: "bg-red-50"
  },
  {
    icon: <Zap className="w-8 h-8" />,
    title: "Fast Processing",
    description: "Process documents in seconds with our optimized infrastructure.",
    color: "text-yellow-600",
    bgColor: "bg-yellow-50"
  },
  {
    icon: <Download className="w-8 h-8" />,
    title: "Batch Processing",
    description: "Upload and process multiple files simultaneously to save time.",
    color: "text-indigo-600",
    bgColor: "bg-indigo-50"
  },
  {
    icon: <Search className="w-8 h-8" />,
    title: "OCR Technology",
    description: "Extract text from scanned documents and images with high accuracy.",
    color: "text-pink-600",
    bgColor: "bg-pink-50"
  },
  {
    icon: <BarChart className="w-8 h-8" />,
    title: "Usage Analytics",
    description: "Track your PDF processing history and optimize your workflow.",
    color: "text-teal-600",
    bgColor: "bg-teal-50"
  }
];

export function FeatureGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      {features.map((feature, index) => (
        <div
          key={index}
          className="bg-white p-6 rounded-2xl border border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all duration-300"
        >
          <div className={`p-3 rounded-xl ${feature.bgColor} w-fit mb-4`}>
            <div className={feature.color}>
              {feature.icon}
            </div>
          </div>
          
          <h3 className="text-xl font-semibold text-gray-900 mb-3">
            {feature.title}
          </h3>
          
          <p className="text-gray-600">
            {feature.description}
          </p>
          
          <div className="mt-4 pt-4 border-t border-gray-100">
            <button className="text-blue-600 font-medium hover:text-blue-700 text-sm">
              Learn more →
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}