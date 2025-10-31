import React, { useRef, useCallback } from 'react';

interface ImageUploadAreaProps {
  onUpload: (files: FileList) => void;
  isProcessing: boolean;
}

export const ImageUploadArea: React.FC<ImageUploadAreaProps> = ({ onUpload, isProcessing }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = React.useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        onUpload(files);
      }
    },
    [onUpload]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        onUpload(files);
      }
    },
    [onUpload]
  );

  const handleClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return (
    <div className="upload-area">
      <div
        className={`upload-zone ${isDragOver ? 'drag-over' : ''} ${isProcessing ? 'processing' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*,.dcm"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          disabled={isProcessing}
        />

        <div className="upload-content">
          {isProcessing ? (
            <>
              <div className="processing-spinner"></div>
              <p>Processing Retina Image...</p>
            </>
          ) : (
            <>
              <div className="upload-icon">📷</div>
              <h3>Upload Retina Image</h3>
              <p>Drag & drop or click to select an image</p>
              <div className="supported-formats">Supports: JPG, PNG, DICOM</div>
            </>
          )}
        </div>
      </div>

      <div className="upload-guidelines">
        <h4>Image Guidelines:</h4>
        <ul>
          <li>✅ High contrast, focused retina images</li>
          <li>✅ Include optic disc and macula when possible</li>
          <li>❌ Avoid blurry or overexposed images</li>
          <li>❌ Remove personal identifiers from images</li>
        </ul>
      </div>
    </div>
  );
};

export default ImageUploadArea;


