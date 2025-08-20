import React, { useState, useCallback } from 'react';
import VirtualTryOn from './VirtualTryOn';
import { useDropzone } from 'react-dropzone';

const imageModules = import.meta.glob('./assets/images/*.{png,jpg,jpeg,gif}', { eager: true });
const imageList = Object.values(imageModules).map(module => module.default);

const ProductsList = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [showTryOn, setShowTryOn] = useState(false);
  const [uploadedImage, setUploadedImage] = useState(null);
  
  const onDrop = useCallback(acceptedFiles => {
    const file = acceptedFiles[0];
    if (file) {
      setUploadedImage(URL.createObjectURL(file));
      setSelectedImage(URL.createObjectURL(file));
      setShowTryOn(true);
    }
  }, []);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif']
    }
  });
  
  const handleTryOn = (image) => {
    setSelectedImage(image);
    setShowTryOn(true);
  };
  
  const handleClose = () => {
    setShowTryOn(false);
  };

  return (
    <div className="fashion-pro-container">
      <header className="app-header">
        <h1>Custom Eyewear Try On</h1>
        <p>Try our collection virtually or upload your own design</p>
      </header>
      
      <div className="upload-section">
        <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
          <input {...getInputProps()} />
          {uploadedImage ? (
            <div className="preview-container">
              <img src={uploadedImage} alt="Uploaded eyewear" className="uploaded-preview" />
              <button className="try-again-btn" onClick={(e) => {
                e.stopPropagation();
                setUploadedImage(null);
              }}>
                Upload different image
              </button>
            </div>
          ) : (
            <div className="drop-content">
              <svg className="upload-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                <path d="M12 16.5l4-4h-3v-9h-2v9H8l4 4zm9-13h-6v1.99h6v14.02H3V5.49h6V3.5H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h18c1.1 0 2-.9 2-2v-14c0-1.1-.9-2-2-2z"/>
              </svg>
              <p>{isDragActive ? "Drop the image here" : "Drag & drop your eyewear image or click to upload"}</p>
            </div>
          )}
        </div>
        
        {uploadedImage && (
          <button 
            className="try-on-btn custom-btn" 
            onClick={() => handleTryOn(uploadedImage)}
          >
            Try On Your Design
          </button>
        )}
      </div>
      
      <h2 className="collection-title">Our Collection</h2>
      
      <div className="product-grid">
        {imageList.map((image, index) => (
          <div className="product-card" key={index}>
            <div className="product-image-container">
              <img
                src={image}
                alt={`Eyewear model ${index + 1}`}
                className="product-image"
              />
              <div className="product-overlay">
                <button className="try-on-btn" onClick={() => handleTryOn(image)}>
                  Try On
                </button>
              </div>
            </div>
            <p className="product-name">Model {index + 1}</p>
          </div>
        ))}
      </div>
      
      {showTryOn && (
        <div className="try-on-modal">
          <div className="modal-content">
            <button className="close-btn" onClick={handleClose}>×</button>
            <h2>Virtual Try-On</h2>
            <VirtualTryOn uri={selectedImage} />
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductsList;