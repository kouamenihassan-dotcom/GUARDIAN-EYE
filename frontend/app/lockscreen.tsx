import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TextInput, TouchableOpacity, Alert } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { ref, onValue, update } from 'firebase/database';
import { database } from '@/services/firebase';
import * as Device from 'expo-device';
import * as Application from 'expo-application';
import { Platform } from 'react-native';
import { useRouter } from 'expo-router';

export default function LockScreen() {
  const [unlockCode, setUnlockCode] = useState('');
  const [deviceId, setDeviceId] = useState<string | null>(null);
  const [isLocked, setIsLocked] = useState(true);
  const router = useRouter();

  useEffect(() => {
    initializeDevice();
  }, []);

  const initializeDevice = async () => {
    const id = Platform.OS === 'web'
      ? 'web_' + navigator.userAgent.slice(0, 50).replace(/[^a-zA-Z0-9]/g, '')
      : Application.androidId || Device.modelId || 'unknown';
    
    setDeviceId(id);

    // Listen for unlock commands from dashboard
    const deviceRef = ref(database, `devices/${id}`);
    onValue(deviceRef, (snapshot) => {
      const data = snapshot.val();
      if (data && data.status !== 'LOCKED') {
        setIsLocked(false);
        // Navigate back to home
        setTimeout(() => router.replace('/home'), 1000);
      }
    });
  };

  const handleUnlock = async () => {
    if (!deviceId) return;

    // In a real implementation, this would verify against a server
    // For now, only dashboard can unlock
    Alert.alert(
      'Device Locked',
      'This device has been locked remotely. Only the owner can unlock it from the web dashboard.',
      [{ text: 'OK' }]
    );
    setUnlockCode('');
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        <Ionicons name="lock-closed" size={80} color="#da3633" />
        <Text style={styles.title}>Device Locked</Text>
        <Text style={styles.subtitle}>This device has been locked remotely by the owner</Text>

        <View style={styles.warningBox}>
          <Ionicons name="warning" size={24} color="#f85149" />
          <Text style={styles.warningText}>
            This device is being tracked. Attempting to tamper with this device is illegal and
            all actions are being logged.
          </Text>
        </View>

        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>To unlock this device:</Text>
          <Text style={styles.infoText}>• Contact the device owner</Text>
          <Text style={styles.infoText}>• Owner must unlock from web dashboard</Text>
          <Text style={styles.infoText}>• Device location is being tracked</Text>
        </View>

        <View style={styles.statusBox}>
          <View style={styles.statusRow}>
            <Ionicons name="location" size={16} color="#58A6FF" />
            <Text style={styles.statusText}>GPS Tracking: Active</Text>
          </View>
          <View style={styles.statusRow}>
            <Ionicons name="camera" size={16} color="#58A6FF" />
            <Text style={styles.statusText}>Camera Monitoring: Active</Text>
          </View>
          <View style={styles.statusRow}>
            <Ionicons name="shield-checkmark" size={16} color="#58A6FF" />
            <Text style={styles.statusText}>Security: Enabled</Text>
          </View>
        </View>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>Guardian Eye Security System</Text>
        <Text style={styles.footerSubtext}>Protected Device</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0D1117',
    justifyContent: 'space-between',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#da3633',
    marginTop: 24,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6e7681',
    textAlign: 'center',
    marginBottom: 32,
  },
  warningBox: {
    flexDirection: 'row',
    backgroundColor: '#f851491a',
    borderWidth: 1,
    borderColor: '#f85149',
    borderRadius: 8,
    padding: 16,
    marginBottom: 24,
    width: '100%',
  },
  warningText: {
    flex: 1,
    color: '#f85149',
    fontSize: 14,
    marginLeft: 12,
    lineHeight: 20,
  },
  infoBox: {
    backgroundColor: '#161b22',
    borderWidth: 1,
    borderColor: '#30363d',
    borderRadius: 8,
    padding: 16,
    marginBottom: 24,
    width: '100%',
  },
  infoTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 12,
  },
  infoText: {
    color: '#6e7681',
    fontSize: 14,
    marginBottom: 8,
  },
  statusBox: {
    backgroundColor: '#161b22',
    borderWidth: 1,
    borderColor: '#30363d',
    borderRadius: 8,
    padding: 16,
    width: '100%',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  statusText: {
    color: '#58A6FF',
    fontSize: 14,
    marginLeft: 8,
  },
  footer: {
    padding: 24,
    alignItems: 'center',
  },
  footerText: {
    color: '#6e7681',
    fontSize: 14,
    fontWeight: '600',
  },
  footerSubtext: {
    color: '#484f58',
    fontSize: 12,
    marginTop: 4,
  },
});
