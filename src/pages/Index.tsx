import { useState } from "react";
import { ImageUpload } from "@/components/ImageUpload";
import { DiagnosisResult } from "@/components/DiagnosisResult";
import { Eye } from "lucide-react";

export default function Index() {
  const [prediction, setPrediction] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <header className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Eye className="w-12 h-12 text-primary" />
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              RetinaScan AI
            </h1>
          </div>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            AI-powered diabetic retinopathy detection from retinal fundus images
          </p>
        </header>

        <div className="grid md:grid-cols-2 gap-8">
          <ImageUpload 
            onPrediction={setPrediction}
            isAnalyzing={isAnalyzing}
            setIsAnalyzing={setIsAnalyzing}
          />
          
          {prediction && (
            <DiagnosisResult prediction={prediction} />
          )}
        </div>

        <footer className="mt-16 text-center text-sm text-muted-foreground">
          <p>⚠️ This tool is for research and educational purposes only.</p>
          <p>Always consult a qualified healthcare professional for medical diagnosis.</p>
        </footer>
      </div>
    </div>
  );
}
