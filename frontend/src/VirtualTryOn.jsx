import React, { useRef, useEffect, useState } from 'react';
import Webcam from 'react-webcam';
import * as THREE from 'three';
import * as tf from '@tensorflow/tfjs-core';
import '@tensorflow/tfjs-converter';
import '@tensorflow/tfjs-backend-webgl';
import * as faceLandmarksDetection from '@tensorflow-models/face-landmarks-detection';

const VirtualTryOn = ({ uri }) => {
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const [model, setModel] = useState(null);
  const [glassesMesh, setGlassesMesh] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [glassesSrc, setGlassesSrc] = useState(uri);
  const [sceneSet, setSceneSet] = useState(false);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);

  useEffect(() => {

    setGlassesSrc(uri);
 
    if (glassesMesh && sceneRef.current) {
      const textureLoader = new THREE.TextureLoader();
      textureLoader.load(uri, (texture) => {
        texture.colorSpace = THREE.SRGBColorSpace;
        glassesMesh.material.map = texture;
        glassesMesh.material.needsUpdate = true;
      });
    }
  }, [uri]);

  useEffect(() => {
    const loadResources = async () => {
      try {
        // Camera Access
        const stream = await navigator.mediaDevices.getUserMedia({ 
          video: { 
            width: { ideal: 800 },
            height: { ideal: 800 }
          } 
        });
        
        if (webcamRef.current) {
          webcamRef.current.srcObject = stream;
        }

        // TensorFlow Model
        await tf.setBackend('webgl');
        const loadedModel = await faceLandmarksDetection.load(
          faceLandmarksDetection.SupportedPackages.mediapipeFacemesh,
          { 
            shouldLoadIrisModel: true,
            maxFaces: 1
          }
        );
        setModel(loadedModel);

        // Three.js Setup
        if (!sceneSet) {
          const width = canvasRef.current.clientWidth;
          const height = canvasRef.current.clientHeight;
          
          const scene = new THREE.Scene();
          sceneRef.current = scene;
          
          const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
          camera.position.z = 5;
          cameraRef.current = camera;
          
          const renderer = new THREE.WebGLRenderer({ 
            canvas: canvasRef.current, 
            alpha: true 
          });
          renderer.setSize(width, height);
          rendererRef.current = renderer;
          
          // Animation loop
          const animate = () => {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
          };
          animate();
          
          setSceneSet(true);

          // Glasses Mesh
          const textureLoader = new THREE.TextureLoader();
          textureLoader.load(glassesSrc, (texture) => {
            texture.colorSpace = THREE.SRGBColorSpace;
            const geometry = new THREE.PlaneGeometry(2, 1);
            const material = new THREE.MeshBasicMaterial({ 
              map: texture, 
              transparent: true 
            });
            const glasses = new THREE.Mesh(geometry, material);
            scene.add(glasses);
            setGlassesMesh(glasses);
          });
        }
      } catch (error) {
        console.error("Initialization error:", error);
        setIsLoading(false);
      }
    };

    loadResources();
    
    // Cleanup function
    return () => {
      if (webcamRef.current && webcamRef.current.srcObject) {
        webcamRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
      
      // Clean up Three.js resources
      if (rendererRef.current) {
        rendererRef.current.dispose();
      }
      
      if (glassesMesh) {
        glassesMesh.geometry.dispose();
        glassesMesh.material.dispose();
        if (sceneRef.current) {
          sceneRef.current.remove(glassesMesh);
        }
      }
    };
  }, []);

  useEffect(() => {
    const detectAndPositionGlasses = async () => {
      if (!webcamRef.current || !model || !glassesMesh) return;
      
      const video = webcamRef.current.video;
      if (video.readyState !== 4) return;

      const faceEstimates = await model.estimateFaces({input: video});
      
      if (faceEstimates.length > 0) {
        setIsLoading(false);
        
        // Face mesh keypoints
        const keypoints = faceEstimates[0].scaledMesh;
        const leftEye = keypoints[130];
        const rightEye = keypoints[359];
        const eyeCenter = keypoints[168];

        // Get the video dimensions
        const videoWidth = video.videoWidth;
        const videoHeight = video.videoHeight;
        
        // Get the canvas dimensions
        const canvasWidth = canvasRef.current.width;
        const canvasHeight = canvasRef.current.height;
        
        // Calculate scale factors for coordinate mapping
        const scaleFactorX = canvasWidth / videoWidth;
        const scaleFactorY = canvasHeight / videoHeight;

        // Eye distance for glasses scaling
        const eyeDistance = Math.sqrt(
          Math.pow(rightEye[0] - leftEye[0], 2) + 
          Math.pow(rightEye[1] - leftEye[1], 2)
        );
        
       
        const scaleMultiplier = eyeDistance / 160; 
        
        
        const scaleX = -0.01;  
        const scaleY = -0.01; 
        const offsetX = 0.00;  
        const offsetY = -0.005;

        // Convert normalized coordinates to match the canvas dimensions
        const normalizedX = (eyeCenter[0] - videoWidth / 2) * scaleX + offsetX;
        const normalizedY = (eyeCenter[1] - videoHeight / 2) * scaleY + offsetY;
        
        // Position the glasses
        glassesMesh.position.x = normalizedX;
        glassesMesh.position.y = normalizedY;
        glassesMesh.scale.set(scaleMultiplier, scaleMultiplier, scaleMultiplier);
        glassesMesh.position.z = 1;

        // Rotate glasses to align with eyes
        const eyeLine = new THREE.Vector2(
          rightEye[0] - leftEye[0], 
          rightEye[1] - leftEye[1]
        );
        const rotationZ = Math.atan2(eyeLine.y, eyeLine.x);
        glassesMesh.rotation.z = rotationZ;
      }
    };

    // Run detection and positioning every 100ms
    const intervalId = setInterval(() => {
      detectAndPositionGlasses();
    }, 100);

    return () => clearInterval(intervalId);
  }, [model, glassesMesh]);

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (canvasRef.current && rendererRef.current && cameraRef.current) {
        const width = canvasRef.current.clientWidth;
        const height = canvasRef.current.clientHeight;
        
        cameraRef.current.aspect = width / height;
        cameraRef.current.updateProjectionMatrix();
        rendererRef.current.setSize(width, height);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="virtual-try-on-container">
      {isLoading && (
        <div className="loading-overlay">
          <div className="spinner"></div>
          <p>Initializing camera and face detection...</p>
        </div>
      )}
      <Webcam 
        ref={webcamRef} 
        autoPlay 
        playsInline 
        className="webcam-feed" 
        mirrored={true}
        videoConstraints={{
          width: 800,
          height: 800,
          facingMode: "user"
        }}
      />
      <canvas 
        ref={canvasRef} 
        className="glasses-overlay"
        width={800}
        height={800}
      />
    </div>
  );
};

export default VirtualTryOn;