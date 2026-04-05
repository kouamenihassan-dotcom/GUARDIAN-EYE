import { ref, onValue, off } from 'firebase/database';
import { database } from '@/services/firebase';
import { LocationService } from './LocationService';
import { CameraService } from './CameraService';
import * as Device from 'expo-device';
import * as Application from 'expo-application';
import { Platform } from 'react-native';

class DeviceMonitorClass {
  private isMonitoring = false;
  private currentStatus: 'NORMAL' | 'STOLEN' | 'LOCKED' = 'NORMAL';
  private deviceId: string | null = null;
  private unsubscribe: (() => void) | null = null;

  async getDeviceId(): Promise<string> {
    if (this.deviceId) return this.deviceId;
    
    if (Platform.OS === 'web') {
      this.deviceId = 'web_' + navigator.userAgent.slice(0, 50).replace(/[^a-zA-Z0-9]/g, '');
    } else {
      this.deviceId = Application.androidId || Device.modelId || 'unknown';
    }
    return this.deviceId;
  }

  async startMonitoring(userId: string): Promise<void> {
    if (this.isMonitoring) {
      console.log('Already monitoring device status');
      return;
    }

    const deviceId = await this.getDeviceId();
    const deviceRef = ref(database, `devices/${deviceId}`);

    console.log('🔍 Starting device status monitoring...');

    const callback = onValue(deviceRef, (snapshot) => {
      const data = snapshot.val();
      if (data && data.status) {
        const newStatus = data.status as 'NORMAL' | 'STOLEN' | 'LOCKED';
        
        if (newStatus !== this.currentStatus) {
          console.log(`📱 Device status changed: ${this.currentStatus} -> ${newStatus}`);
          this.handleStatusChange(this.currentStatus, newStatus, userId, deviceId);
          this.currentStatus = newStatus;
        }
      }
    });

    this.unsubscribe = () => off(deviceRef);
    this.isMonitoring = true;
  }

  private async handleStatusChange(
    oldStatus: string,
    newStatus: string,
    userId: string,
    deviceId: string
  ): Promise<void> {
    console.log(`Handling status change from ${oldStatus} to ${newStatus}`);

    if (newStatus === 'STOLEN') {
      console.log('🚨 Device marked as STOLEN!');
      console.log('📍 Starting GPS tracking...');
      console.log('📸 Capturing photo...');

      await LocationService.startTracking(userId);
      await CameraService.captureAndUpload(deviceId);
    } else if (oldStatus === 'STOLEN' && newStatus === 'NORMAL') {
      console.log('✅ Device marked as NORMAL - stopping tracking');
      LocationService.stopTracking();
    } else if (newStatus === 'LOCKED') {
      console.log('🔒 Device locked remotely');
    }
  }

  stopMonitoring(): void {
    if (this.unsubscribe) {
      this.unsubscribe();
      this.unsubscribe = null;
    }
    LocationService.stopTracking();
    this.isMonitoring = false;
    console.log('Device monitoring stopped');
  }

  getMonitoringStatus(): boolean {
    return this.isMonitoring;
  }
}

export const DeviceMonitor = new DeviceMonitorClass();
