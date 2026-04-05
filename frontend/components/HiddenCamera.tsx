import React, { useRef, useState, useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';

interface HiddenCameraProps {
  onPhotoCapture?: (base64: string) => void;
  shouldCapture: boolean;
}

export const HiddenCamera: React.FC<HiddenCameraProps> = ({ onPhotoCapture, shouldCapture }) => {
  const cameraRef = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [isCapturing, setIsCapturing] = useState(false);

  useEffect(() => {
    if (!permission) {
      requestPermission();
    }
  }, []);

  useEffect(() => {
    if (shouldCapture && !isCapturing && permission?.granted && cameraRef.current) {
      capturePhoto();
    }
  }, [shouldCapture, permission]);

  const capturePhoto = async () => {
    if (!cameraRef.current || isCapturing) return;
    
    setIsCapturing(true);
    
    try {
      console.log('📸 Capturing actual photo...');
      
      // Wait a moment for camera to be ready
      await new Promise(resolve => setTimeout(resolve, 500));
      
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.5,
        base64: true,
        skipProcessing: true,
      });

      if (photo?.base64 && onPhotoCapture) {
        console.log('✅ Photo captured successfully');
        onPhotoCapture(photo.base64);
      }
    } catch (error) {
      console.error('Error capturing photo:', error);
    } finally {
      setIsCapturing(false);
    }
  };

  if (!permission?.granted) {
    return null;
  }

  // Render camera off-screen (1x1 pixel, invisible)
  return (
    <View style={styles.hiddenContainer}>
      <CameraView
        ref={cameraRef}
        style={styles.camera}
        facing="front"
      />
    </View>
  );
};

const styles = StyleSheet.create({
  hiddenContainer: {
    position: 'absolute',
    width: 1,
    height: 1,
    opacity: 0,
    overflow: 'hidden',
  },
  camera: {
    width: 1,
    height: 1,
  },
});
