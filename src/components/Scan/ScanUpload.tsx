import React, { useState, useRef } from 'react';
import { Patient, RetinaScan } from '../../types/retina';
import { useRetinaAnalysis } from '../../hooks/useRetinaAnalysis';

interface ScanUploadProps {
  patient: Patient | null;
  onScanUpload: (scan: RetinaScan) => void;
}

export const ScanUpload: React.FC<ScanUploadProps> = ({ patient, onScanUpload }) => {
  const [selectedEye, setSelectedEye] = useState<'left' | 'right' | 'both'>('left');
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { analyzeScan, isAnalyzing, progress } = useRetinaAnalysis();

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      await processFile(e.target.files[0]);
    }
  };

  const processFile = async (file: File) => {
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file');
      return;
    }

    for (let i = 0; i <= 100; i += 10) {
      setUploadProgress(i);
      // eslint-disable-next-line no-await-in-loop
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    const scan: RetinaScan = {
      id: `scan_${Date.now()}`,
      patientId: patient?.id || 'unknown',
      image: file,
      uploadDate: new Date().toISOString(),
      status: 'processing',
      eye: selectedEye,
      quality: 85,
    };

    onScanUpload(scan);

    const result = await analyzeScan(scan);
    // eslint-disable-next-line no-console
    console.log('Analysis result:', result);
  };

  if (!patient) {
    return (
      <div className="p-8 text-center">
        <div className="text-gray-500 text-lg mb-4">Please enter patient information first</div>
        <div className="text-gray-400">Patient details are required before uploading retina scans</div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Retina Scan</h2>
        <p className="text-gray-600">Upload high-quality retina images for AI-powered diabetic retinopathy detection</p>
      </div>

      <div className="mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-3">Select Eye</label>
        <div className="flex space-x-4">
          {[
            { value: 'left', label: 'Left Eye', icon: '👁️' },
            { value: 'right', label: 'Right Eye', icon: '👁️' },
            { value: 'both', label: 'Both Eyes', icon: '👀' },
          ].map((eye) => (
            <button
              key={eye.value}
              onClick={() => setSelectedEye(eye.value as any)}
              className={`flex-1 p-4 border-2 rounded-lg text-center transition-all ${
                selectedEye === eye.value
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="text-2xl mb-2">{eye.icon}</div>
              <div className="font-medium">{eye.label}</div>
            </button>
          ))}
        </div>
      </div>

      <div
        className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
          dragActive ? 'border-blue-400 bg-blue-50' : 'border-gray-300 bg-gray-50 hover:border-gray-400'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input ref={fileInputRef} type="file" accept="image/*" onChange={handleFileSelect} className="hidden" />

        <div className="max-w-md mx-auto">
          <div className="text-6xl mb-4">📷</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Upload Retina Image</h3>
          <p className="text-gray-600 mb-6">Drag and drop your retina scan image, or click to browse</p>

          <button
            onClick={() => fileInputRef.current?.click()}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            disabled={isAnalyzing}
          >
            Select Image
          </button>

          <div className="mt-4 text-sm text-gray-500">Supports JPG, PNG, TIFF • Max 10MB</div>
        </div>
      </div>

      {uploadProgress > 0 && uploadProgress < 100 && (
        <div className="mt-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Uploading...</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-blue-600 h-2 rounded-full transition-all duration-300" style={{ width: `${uploadProgress}%` }} />
          </div>
        </div>
      )}

      {isAnalyzing && (
        <div className="mt-6 p-6 bg-blue-50 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-blue-900">AI Analysis in Progress</h4>
            <span className="text-blue-700 font-medium">{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-blue-200 rounded-full h-3">
            <div className="bg-blue-600 h-3 rounded-full transition-all duration-500" style={{ width: `${progress}%` }} />
          </div>
          <div className="mt-3 text-sm text-blue-700">Analyzing retinal features... This may take a few moments.</div>
        </div>
      )}

      <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <h4 className="font-semibold text-yellow-900 mb-2">Image Quality Guidelines</h4>
        <ul className="text-yellow-800 text-sm space-y-1 list-disc list-inside">
          <li>Ensure proper lighting and focus</li>
          <li>Center the retina in the image</li>
          <li>Avoid blurry or overexposed images</li>
          <li>Include the optic disc and macula when possible</li>
        </ul>
      </div>
    </div>
  );
};


