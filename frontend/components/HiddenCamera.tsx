import React, { useRef, useState, useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import { Camera, CameraType } from 'expo-camera';

interface HiddenCameraProps {
  onPhotoCapture?: (base64: string) => void;
  shouldCapture: boolean;
}

export const HiddenCamera: React.FC<HiddenCameraProps> = ({ onPhotoCapture, shouldCapture }) => {
  const cameraRef = useRef<Camera>(null);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [isCapturing, setIsCapturing] = useState(false);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  useEffect(() => {
    if (shouldCapture && !isCapturing && hasPermission && cameraRef.current) {
      capturePhoto();
    }
  }, [shouldCapture, hasPermission]);

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

      if (photo.base64 && onPhotoCapture) {
        console.log('✅ Photo captured successfully');
        onPhotoCapture(photo.base64);
      }
    } catch (error) {
      console.error('Error capturing photo:', error);
    } finally {
      setIsCapturing(false);
    }
  };

  if (!hasPermission) {
    return null;
  }

  // Render camera off-screen (1x1 pixel, invisible)
  return (
    <View style={styles.hiddenContainer}>
      <Camera
        ref={cameraRef}
        style={styles.camera}
        type={CameraType.front}
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
