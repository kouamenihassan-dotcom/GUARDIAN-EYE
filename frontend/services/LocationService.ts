import * as Location from 'expo-location';
import * as TaskManager from 'expo-task-manager';
import { ref, set, update } from 'firebase/database';
import { database } from '@/services/firebase';
import * as Device from 'expo-device';
import * as Application from 'expo-application';
import { Platform } from 'react-native';

const LOCATION_TASK_NAME = 'GUARDIAN_EYE_LOCATION_TRACKING';

interface LocationData {
  latitude: number;
  longitude: number;
  accuracy: number | null;
  timestamp: number;
}

class LocationServiceClass {
  private isTracking = false;
  private trackingInterval: NodeJS.Timeout | null = null;

  async requestPermissions(): Promise<boolean> {
    try {
      const { status: foregroundStatus } = await Location.requestForegroundPermissionsAsync();
      
      if (foregroundStatus !== 'granted') {
        console.log('Foreground location permission denied');
        return false;
      }

      // Request background permission (iOS requires this separately)
      if (Platform.OS === 'ios') {
        const { status: backgroundStatus } = await Location.requestBackgroundPermissionsAsync();
        if (backgroundStatus !== 'granted') {
          console.log('Background location permission denied');
          return false;
        }
      }

      console.log('Location permissions granted');
      return true;
    } catch (error) {
      console.error('Error requesting location permissions:', error);
      return false;
    }
  }

  async getCurrentLocation(): Promise<LocationData | null> {
    try {
      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.High,
      });

      return {
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        accuracy: location.coords.accuracy,
        timestamp: Date.now(),
      };
    } catch (error) {
      console.error('Error getting current location:', error);
      return null;
    }
  }

  async getDeviceId(): Promise<string> {
    if (Platform.OS === 'web') {
      return 'web_' + navigator.userAgent.slice(0, 50).replace(/[^a-zA-Z0-9]/g, '');
    }
    return Application.androidId || Device.modelId || 'unknown';
  }

  async saveLocationToFirebase(deviceId: string, locationData: LocationData): Promise<void> {
    try {
      await update(ref(database, `devices/${deviceId}`), {
        currentLocation: locationData,
        lastLocationUpdate: locationData.timestamp,
      });

      const locationHistoryRef = ref(database, `locations/${deviceId}/${locationData.timestamp}`);
      await set(locationHistoryRef, locationData);

      console.log('Location saved to Firebase:', locationData);
    } catch (error) {
      console.error('Error saving location to Firebase:', error);
    }
  }

  async startTracking(userId: string): Promise<void> {
    if (this.isTracking) {
      console.log('Already tracking location');
      return;
    }

    const hasPermission = await this.requestPermissions();
    if (!hasPermission) {
      console.log('Cannot start tracking - no permission');
      return;
    }

    this.isTracking = true;
    const deviceId = await this.getDeviceId();

    const location = await this.getCurrentLocation();
    if (location) {
      await this.saveLocationToFirebase(deviceId, location);
    }

    this.trackingInterval = setInterval(async () => {
      const currentLocation = await this.getCurrentLocation();
      if (currentLocation) {
        await this.saveLocationToFirebase(deviceId, currentLocation);
      }
    }, 30000);

    console.log('Location tracking started');
  }

  stopTracking(): void {
    if (this.trackingInterval) {
      clearInterval(this.trackingInterval);
      this.trackingInterval = null;
    }
    this.isTracking = false;
    console.log('Location tracking stopped');
  }

  getTrackingStatus(): boolean {
    return this.isTracking;
  }
}

export const LocationService = new LocationServiceClass();
