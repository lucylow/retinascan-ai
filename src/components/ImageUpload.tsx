import { useState, useCallback } from "react";
import { Upload, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import { supabase } from "@/integrations/supabase/client";

interface ImageUploadProps {
  onPrediction: (prediction: any) => void;
  isAnalyzing: boolean;
  setIsAnalyzing: (analyzing: boolean) => void;
}

export function ImageUpload({ onPrediction, isAnalyzing, setIsAnalyzing }: ImageUploadProps) {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { toast } = useToast();

  const handleImageSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      toast({
        title: "Invalid file type",
        description: "Please upload an image file",
        variant: "destructive",
      });
      return;
    }

    if (file.size > 16 * 1024 * 1024) {
      toast({
        title: "File too large",
        description: "Maximum file size is 16MB",
        variant: "destructive",
      });
      return;
    }

    setSelectedFile(file);
    const reader = new FileReader();
    reader.onload = (e) => setSelectedImage(e.target?.result as string);
    reader.readAsDataURL(file);
  }, [toast]);

  const analyzeImage = async () => {
    if (!selectedFile || !selectedImage) return;

    setIsAnalyzing(true);
    try {
      const { data, error } = await supabase.functions.invoke("analyze-retina", {
        body: { image: selectedImage },
      });

      if (error) throw error;
      
      onPrediction(data);
      toast({
        title: "Analysis complete",
        description: "Your retinal image has been analyzed",
      });
    } catch (error: any) {
      console.error("Analysis error:", error);
      toast({
        title: "Analysis failed",
        description: error.message || "Failed to analyze image",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <Card className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Upload Retinal Image</h2>
      
      <div className="space-y-4">
        <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors">
          {selectedImage ? (
            <div className="space-y-4">
              <img
                src={selectedImage}
                alt="Selected retinal scan"
                className="max-h-64 mx-auto rounded-lg"
              />
              <label htmlFor="image-input" className="cursor-pointer text-sm text-primary hover:underline">
                Change image
              </label>
            </div>
          ) : (
            <label htmlFor="image-input" className="cursor-pointer block">
              <Upload className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-lg mb-2">Click to upload or drag and drop</p>
              <p className="text-sm text-muted-foreground">PNG, JPG, JPEG (max 16MB)</p>
            </label>
          )}
          <input
            id="image-input"
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
            disabled={isAnalyzing}
          />
        </div>

        {selectedImage && (
          <Button
            onClick={analyzeImage}
            disabled={isAnalyzing}
            className="w-full"
            size="lg"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              "Analyze Image"
            )}
          </Button>
        )}
      </div>
    </Card>
  );
}
