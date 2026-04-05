import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { ref, onValue } from 'firebase/database';
import { database } from '@/services/firebase';
import { DeviceMonitor } from '@/services/DeviceMonitor';
import { NotificationService } from '@/services/NotificationService';
import { CameraService } from '@/services/CameraService';
import { HiddenCamera } from '@/components/HiddenCamera';
import * as Device from 'expo-device';
import * as Application from 'expo-application';
import { Platform } from 'react-native';

interface DeviceInfo {
  deviceId: string;
  deviceName: string;
  modelName: string;
  osName: string;
  osVersion: string;
  status: 'NORMAL' | 'STOLEN' | 'LOCKED';
  lastSeen: number;
}

export default function HomeScreen() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [deviceInfo, setDeviceInfo] = useState<DeviceInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [shouldCapturePhoto, setShouldCapturePhoto] = useState(false);

  useEffect(() => {
    if (!user) {
      router.replace('/');
      return;
    }

    loadDeviceInfo();
    initializeServices();
    
    // Start device monitoring for status changes
    DeviceMonitor.startMonitoring(user.uid);
    
    // Cleanup on unmount
    return () => {
      DeviceMonitor.stopMonitoring();
    };
  }, [user]);

  const initializeServices = async () => {
    // Initialize notifications
    await NotificationService.requestPermissions();
    const deviceId = Platform.OS === 'web'
      ? 'web_' + navigator.userAgent.slice(0, 50).replace(/[^a-zA-Z0-9]/g, '')
      : Application.androidId || Device.modelId || 'unknown';
    
    if (user) {
      await NotificationService.registerPushToken(deviceId, user.uid);
    }
    
    NotificationService.setupNotificationListeners();
    
    // Register camera capture callback
    DeviceMonitor.setOnCameraCapture(() => {
      setShouldCapturePhoto(true);
    });
  };

  const handlePhotoCapture = async (base64: string) => {
    console.log('📸 Photo captured from HiddenCamera');
    await CameraService.onPhotoCaptured(base64);
    setShouldCapturePhoto(false);
    
    // Send notification
    await NotificationService.sendLocalNotification(
      'Photo Captured',
      'Intruder photo captured successfully'
    );
  };

  // Check if device is locked and redirect
  useEffect(() => {
    if (deviceInfo && deviceInfo.status === 'LOCKED') {
      router.replace('/lockscreen');
    }
  }, [deviceInfo]);

  const loadDeviceInfo = async () => {
    try {
      // Get current device ID
      let deviceId;
      if (Platform.OS === 'web') {
        deviceId = 'web_' + navigator.userAgent.slice(0, 50).replace(/[^a-zA-Z0-9]/g, '');
      } else {
        deviceId = Application.androidId || Device.modelId || 'unknown';
      }

      // Listen to device status in Firebase
      const deviceRef = ref(database, `devices/${deviceId}`);
      onValue(deviceRef, (snapshot) => {
        const data = snapshot.val();
        if (data) {
          setDeviceInfo(data);
        }
        setLoading(false);
      });
    } catch (error) {
      console.error('Error loading device info:', error);
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    Alert.alert('Logout', 'Are you sure you want to logout?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Logout',
        style: 'destructive',
        onPress: async () => {
          await logout();
          router.replace('/');
        },
      },
    ]);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'NORMAL':
        return '#238636';
      case 'STOLEN':
        return '#da3633';
      case 'LOCKED':
        return '#f85149';
      default:
        return '#6e7681';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'NORMAL':
        return 'shield-checkmark';
      case 'STOLEN':
        return 'warning';
      case 'LOCKED':
        return 'lock-closed';
      default:
        return 'help-circle';
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#58A6FF" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Hidden Camera Component */}
      <HiddenCamera 
        shouldCapture={shouldCapturePhoto}
        onPhotoCapture={handlePhotoCapture}
      />
      
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>Guardian Eye</Text>
          <Text style={styles.headerSubtitle}>{user?.email}</Text>
        </View>
        <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
          <Ionicons name="log-out-outline" size={24} color="#58A6FF" />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        {/* Device Status Card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Ionicons name="phone-portrait" size={24} color="#58A6FF" />
            <Text style={styles.cardTitle}>Device Status</Text>
          </View>

          {deviceInfo ? (
            <>
              <View style={styles.statusContainer}>
                <Ionicons
                  name={getStatusIcon(deviceInfo.status)}
                  size={48}
                  color={getStatusColor(deviceInfo.status)}
                />
                <Text
                  style={[
                    styles.statusText,
                    { color: getStatusColor(deviceInfo.status) },
                  ]}
                >
                  {deviceInfo.status}
                </Text>
              </View>

              <View style={styles.deviceDetails}>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Device Name:</Text>
                  <Text style={styles.detailValue}>{deviceInfo.deviceName}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Model:</Text>
                  <Text style={styles.detailValue}>{deviceInfo.modelName}</Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>OS:</Text>
                  <Text style={styles.detailValue}>
                    {deviceInfo.osName} {deviceInfo.osVersion}
                  </Text>
                </View>
                <View style={styles.detailRow}>
                  <Text style={styles.detailLabel}>Last Seen:</Text>
                  <Text style={styles.detailValue}>
                    {new Date(deviceInfo.lastSeen).toLocaleString()}
                  </Text>
                </View>
              </View>
            </>
          ) : (
            <Text style={styles.noDeviceText}>No device information available</Text>
          )}
        </View>

        {/* Quick Actions */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Ionicons name="settings" size={24} color="#58A6FF" />
            <Text style={styles.cardTitle}>Quick Actions</Text>
          </View>

          <TouchableOpacity style={styles.actionButton} onPress={() => router.push('/settings')}>
            <Ionicons name="settings" size={20} color="#58A6FF" />
            <Text style={styles.actionButtonText}>Security Settings</Text>
            <Ionicons name="chevron-forward" size={20} color="#6e7681" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="location" size={20} color="#58A6FF" />
            <Text style={styles.actionButtonText}>View Location History</Text>
            <Ionicons name="chevron-forward" size={20} color="#6e7681" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.actionButton}>
            <Ionicons name="camera" size={20} color="#58A6FF" />
            <Text style={styles.actionButtonText}>View Captured Photos</Text>
            <Ionicons name="chevron-forward" size={20} color="#6e7681" />
          </TouchableOpacity>
        </View>

        {/* Info Card */}
        <View style={styles.infoCard}>
          <Ionicons name="information-circle" size={20} color="#58A6FF" />
          <Text style={styles.infoText}>
            Use the web dashboard to remotely monitor and control your device. Visit the
            dashboard to mark your device as stolen, view real-time location, and access
            captured photos.
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D1117',
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: '#0D1117',
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    paddingTop: 48,
    backgroundColor: '#161b22',
    borderBottomWidth: 1,
    borderBottomColor: '#30363d',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6e7681',
    marginTop: 4,
  },
  logoutButton: {
    padding: 8,
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: 16,
  },
  card: {
    backgroundColor: '#161b22',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#30363d',
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginLeft: 8,
  },
  statusContainer: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  statusText: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 12,
  },
  deviceDetails: {
    marginTop: 16,
  },
  detailRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#30363d',
  },
  detailLabel: {
    fontSize: 14,
    color: '#6e7681',
  },
  detailValue: {
    fontSize: 14,
    color: '#fff',
    fontWeight: '500',
  },
  noDeviceText: {
    color: '#6e7681',
    textAlign: 'center',
    paddingVertical: 24,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#0D1117',
    borderRadius: 8,
    marginBottom: 8,
  },
  actionButtonText: {
    flex: 1,
    fontSize: 14,
    color: '#fff',
    marginLeft: 12,
  },
  infoCard: {
    flexDirection: 'row',
    backgroundColor: '#161b22',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#1f6feb',
  },
  infoText: {
    flex: 1,
    fontSize: 13,
    color: '#6e7681',
    marginLeft: 12,
    lineHeight: 20,
  },
});
