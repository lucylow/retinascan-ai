import { useState, useRef } from "react";
import { ImageUpload } from "@/components/ImageUpload";
import { DiagnosisResult } from "@/components/DiagnosisResult";
import { AIChatAssistant } from "@/components/AIChatAssistant";
import { FeatureCard } from "@/components/FeatureCard";
import { StatCard } from "@/components/StatCard";
import { ConfigWarning } from "@/components/ConfigWarning";
import { Button } from "@/components/ui/button";
import {
  Eye,
  Zap,
  Shield,
  BarChart3,
  Upload,
  ArrowRight,
  CheckCircle2,
  TrendingUp,
  Users,
  Brain,
} from "lucide-react";

export default function Index() {
  const [prediction, setPrediction] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const uploadSectionRef = useRef<HTMLDivElement>(null);

  const scrollToUpload = () => {
    uploadSectionRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-32">
        <div className="absolute inset-0 bg-grid-slate-900/[0.04] bg-[size:20px_20px] dark:bg-grid-slate-100/[0.05]" />
        <div className="container mx-auto px-4 relative z-10">
          <div className="text-center max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-8 duration-1000">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="relative">
                <Eye className="w-16 h-16 text-primary animate-pulse" />
                <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full" />
              </div>
              <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-primary via-primary/80 to-primary/60 bg-clip-text text-transparent">
                RetinaScan AI
              </h1>
            </div>
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 leading-relaxed">
              Revolutionary AI-powered diabetic retinopathy detection
              <br />
              <span className="text-lg">Get instant analysis of retinal fundus images with clinical-grade accuracy</span>
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button
                onClick={scrollToUpload}
                size="lg"
                className="text-lg px-8 py-6 h-auto shadow-lg hover:shadow-xl transition-all"
              >
                Get Started <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
              <Button
                variant="outline"
                size="lg"
                className="text-lg px-8 py-6 h-auto"
              >
                Learn More
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="container mx-auto px-4 py-16 -mt-20 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard icon={TrendingUp} value="95%+" label="Accuracy Rate" />
          <StatCard icon={Zap} value="<5s" label="Analysis Time" />
          <StatCard icon={Users} value="5" label="Severity Levels" />
          <StatCard icon={Brain} value="AI" label="Powered by Gemini" />
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-24">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Why Choose <span className="text-primary">RetinaScan AI</span>?
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Cutting-edge AI technology designed for healthcare professionals and researchers
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon={Zap}
            title="Lightning Fast"
            description="Get results in seconds with our optimized AI pipeline. No waiting, no delays."
          />
          <FeatureCard
            icon={Shield}
            title="Highly Accurate"
            description="State-of-the-art vision models trained on thousands of retinal images for reliable diagnosis."
          />
          <FeatureCard
            icon={BarChart3}
            title="Detailed Insights"
            description="Comprehensive analysis with confidence scores, severity classification, and clinical recommendations."
          />
          <FeatureCard
            icon={CheckCircle2}
            title="5 Severity Levels"
            description="Precise classification from No DR to Proliferative DR with actionable insights."
          />
          <FeatureCard
            icon={Brain}
            title="AI-Powered"
            description="Powered by Google Gemini 2.5 Flash vision model for advanced pattern recognition."
          />
          <FeatureCard
            icon={Upload}
            title="Easy to Use"
            description="Simply upload your retinal image and get instant, comprehensive analysis results."
          />
        </div>
      </section>

      {/* How It Works Section */}
      <section className="bg-muted/50 py-24">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              How It <span className="text-primary">Works</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Simple, fast, and reliable retinal image analysis in three easy steps
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center space-y-4 animate-in fade-in slide-in-from-left duration-700">
              <div className="h-16 w-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold mx-auto">
                1
              </div>
              <h3 className="text-2xl font-semibold">Upload Image</h3>
              <p className="text-muted-foreground">
                Upload a retinal fundus image (PNG, JPG, or JPEG) up to 16MB
              </p>
            </div>
            <div className="text-center space-y-4 animate-in fade-in duration-700 delay-300">
              <div className="h-16 w-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold mx-auto">
                2
              </div>
              <h3 className="text-2xl font-semibold">AI Analysis</h3>
              <p className="text-muted-foreground">
                Our AI analyzes the image using advanced vision models to detect diabetic retinopathy
              </p>
            </div>
            <div className="text-center space-y-4 animate-in fade-in slide-in-from-right duration-700 delay-500">
              <div className="h-16 w-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold mx-auto">
                3
              </div>
              <h3 className="text-2xl font-semibold">Get Results</h3>
              <p className="text-muted-foreground">
                Receive detailed diagnosis with severity level, confidence scores, and recommendations
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Main Upload Section */}
      <section ref={uploadSectionRef} className="container mx-auto px-4 py-24 scroll-mt-20">
        <ConfigWarning />
        <div className="text-center mb-12">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Analyze Your <span className="text-primary">Retinal Image</span>
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload a retinal fundus image to get instant AI-powered analysis and diagnosis
          </p>
        </div>
        <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          <ImageUpload
            onPrediction={setPrediction}
            isAnalyzing={isAnalyzing}
            setIsAnalyzing={setIsAnalyzing}
          />
          {prediction ? (
            <DiagnosisResult prediction={prediction} />
          ) : (
            <div className="flex items-center justify-center min-h-[400px] rounded-lg border-2 border-dashed border-muted">
              <div className="text-center space-y-4 p-8">
                <Eye className="w-16 h-16 mx-auto text-muted-foreground/50" />
                <p className="text-lg text-muted-foreground">
                  Upload an image to see analysis results here
                </p>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-muted/50 py-12 mt-24">
        <div className="container mx-auto px-4">
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Eye className="w-6 h-6 text-primary" />
              <span className="text-xl font-bold">RetinaScan AI</span>
            </div>
            <div className="flex flex-col gap-2 text-sm text-muted-foreground">
              <p className="font-semibold text-foreground">⚠️ Medical Disclaimer</p>
              <p>This tool is for research and educational purposes only.</p>
              <p>Always consult a qualified healthcare professional for medical diagnosis.</p>
            </div>
            <p className="text-xs text-muted-foreground pt-4">
              © 2024 RetinaScan AI. Powered by AI technology.
            </p>
          </div>
        </div>
      </footer>

      {/* AI Chat Assistant */}
      <AIChatAssistant />
    </div>
  );
}
