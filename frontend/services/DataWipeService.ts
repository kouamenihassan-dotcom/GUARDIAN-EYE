import { ref, remove, set, update } from 'firebase/database';
import { ref as storageRef, deleteObject, listAll } from 'firebase/storage';
import { database, storage } from '@/services/firebase';
import * as Device from 'expo-device';
import * as Application from 'expo-application';
import { Platform } from 'react-native';

class DataWipeServiceClass {
  async getDeviceId(): Promise<string> {
    if (Platform.OS === 'web') {
      return 'web_' + navigator.userAgent.slice(0, 50).replace(/[^a-zA-Z0-9]/g, '');
    }
    return Application.androidId || Device.modelId || 'unknown';
  }

  async wipeDeviceData(deviceId: string): Promise<void> {
    try {
      console.log('🗑️ Starting data wipe for device:', deviceId);

      // Log the wipe event before clearing
      await set(ref(database, `wipeEvents/${deviceId}/${Date.now()}`), {
        timestamp: Date.now(),
        deviceId,
        action: 'DATA_WIPE',
      });

      // Remove location history
      await remove(ref(database, `locations/${deviceId}`));
      console.log('✅ Location history cleared');

      // Remove photos from database
      await remove(ref(database, `photos/${deviceId}`));
      console.log('✅ Photo metadata cleared');

      // Delete photos from storage
      try {
        const photosStorageRef = storageRef(storage, `photos/${deviceId}`);
        const photosList = await listAll(photosStorageRef);
        
        for (const item of photosList.items) {
          await deleteObject(item);
        }
        console.log('✅ Photos deleted from storage');
      } catch (error) {
        console.log('No photos to delete from storage');
      }

      // Reset device status
      await update(ref(database, `devices/${deviceId}`), {
        status: 'NORMAL',
        currentLocation: null,
        lastLocationUpdate: null,
        markedStolenAt: null,
        lockedAt: null,
        dataWipedAt: Date.now(),
      });

      console.log('✅ Device data wipe completed successfully');
    } catch (error) {
      console.error('Error wiping device data:', error);
      throw error;
    }
  }

  async emergencyWipe(): Promise<void> {
    try {
      const deviceId = await this.getDeviceId();
      await this.wipeDeviceData(deviceId);
      
      // Also clear local app data if needed
      // This would require AsyncStorage or SecureStore
      console.log('🚨 Emergency wipe completed');
    } catch (error) {
      console.error('Error in emergency wipe:', error);
      throw error;
    }
  }
}

export const DataWipeService = new DataWipeServiceClass();
