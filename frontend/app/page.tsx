import { UploadArea } from "@/components/upload-area";
import { FeatureGrid } from "@/components/feature-grid";
import { PricingSection } from "@/components/pricing-section";
import { ChatDemo } from "@/components/chat-demo";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <section className="text-center py-12">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            Process PDFs like a pro,
            <span className="block text-blue-600">chat with them like a human</span>
          </h1>
          <p className="text-xl text-gray-600 mb-10 max-w-3xl mx-auto">
            PDF Genius combines powerful PDF processing with AI chat capabilities.
            Convert, merge, compress, and ask questions about your documents—all in one place.
          </p>
          
          <UploadArea />
        </section>

        {/* Features Grid */}
        <section className="py-12">
          <h2 className="text-3xl font-bold text-center mb-10">
            Everything you need for PDFs
          </h2>
          <FeatureGrid />
        </section>

        {/* Live Chat Demo */}
        <section className="py-12 bg-white rounded-2xl shadow-lg p-6 mb-12">
          <h2 className="text-3xl font-bold text-center mb-8">
            Try our AI chat with PDFs
          </h2>
          <p className="text-gray-600 text-center mb-8 max-w-2xl mx-auto">
            Upload a PDF and ask questions, get summaries, or extract data instantly.
          </p>
          <ChatDemo />
        </section>

        {/* Pricing */}
        <section className="py-12">
          <h2 className="text-3xl font-bold text-center mb-10">
            Simple, transparent pricing
          </h2>
          <PricingSection />
        </section>

        {/* CTA */}
        <section className="text-center py-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl text-white">
          <h2 className="text-3xl font-bold mb-6">
            Ready to revolutionize your PDF workflow?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Join thousands of professionals who trust PDF Genius
          </p>
          <button className="bg-white text-blue-600 px-8 py-4 rounded-full text-lg font-semibold hover:bg-gray-100 transition-colors">
            Get Started Free
          </button>
          <p className="mt-4 text-sm opacity-80">
            No credit card required • 10 free conversions/month
          </p>
        </section>
      </main>

      <Footer />
    </div>
  );
}