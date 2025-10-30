import { useState, useRef } from "react";
import { Link } from "react-router-dom";
import { ConfigWarning } from "@/components/ConfigWarning";
import { Eye } from "lucide-react";

export default function Index() {
  const uploadSectionRef = useRef<HTMLDivElement>(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
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
        <div className="max-w-3xl mx-auto text-center space-y-6">
          <div className="flex items-center justify-center min-h-[200px] rounded-lg border-2 border-dashed border-muted">
            <div className="text-center space-y-4 p-8">
              <Eye className="w-16 h-16 mx-auto text-muted-foreground/50" />
              <p className="text-lg text-muted-foreground">
                Use the header’s "Start Retina Scan" to upload your image
              </p>
              <p className="text-sm text-muted-foreground">
                Or <Link to="/retina" className="text-primary underline">open Retina Scan</Link>
              </p>
            </div>
          </div>
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

    </div>
  );
}
