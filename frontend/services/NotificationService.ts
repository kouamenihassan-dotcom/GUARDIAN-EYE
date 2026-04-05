import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';
import { ref, update } from 'firebase/database';
import { database } from '@/services/firebase';

// Configure notification handler
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

class NotificationServiceClass {
  async requestPermissions(): Promise<boolean> {
    try {
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      
      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      
      if (finalStatus !== 'granted') {
        console.log('Notification permission denied');
        return false;
      }

      console.log('Notification permissions granted');
      return true;
    } catch (error) {
      console.error('Error requesting notification permissions:', error);
      return false;
    }
  }

  async getExpoPushToken(): Promise<string | null> {
    try {
      if (Platform.OS === 'web') {
        console.log('Push notifications not supported on web');
        return null;
      }

      const hasPermission = await this.requestPermissions();
      if (!hasPermission) return null;

      const token = (await Notifications.getExpoPushTokenAsync({
        projectId: 'guardianeye-feb2d',
      })).data;

      console.log('Expo Push Token:', token);
      return token;
    } catch (error) {
      console.error('Error getting push token:', error);
      return null;
    }
  }

  async registerPushToken(deviceId: string, userId: string): Promise<void> {
    try {
      const token = await this.getExpoPushToken();
      if (!token) return;

      // Save token to Firebase
      await update(ref(database, `devices/${deviceId}`), {
        expoPushToken: token,
        userId,
      });

      console.log('Push token registered in Firebase');
    } catch (error) {
      console.error('Error registering push token:', error);
    }
  }

  async sendLocalNotification(title: string, body: string): Promise<void> {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          sound: true,
          priority: Notifications.AndroidNotificationPriority.HIGH,
        },
        trigger: null, // Show immediately
      });
    } catch (error) {
      console.error('Error sending local notification:', error);
    }
  }

  setupNotificationListeners() {
    // Handle notification when app is in foreground
    Notifications.addNotificationReceivedListener(notification => {
      console.log('Notification received:', notification);
    });

    // Handle notification tap
    Notifications.addNotificationResponseReceivedListener(response => {
      console.log('Notification tapped:', response);
    });
  }
}

export const NotificationService = new NotificationServiceClass();
