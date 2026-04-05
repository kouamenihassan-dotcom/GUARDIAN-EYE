import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert,
  TextInput,
} from 'react-native';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { ref, update } from 'firebase/database';
import { database } from '@/services/firebase';
import * as Device from 'expo-device';
import * as Application from 'expo-application';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function SettingsScreen() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [stealthMode, setStealthMode] = useState(false);
  const [emergencyContact, setEmergencyContact] = useState('');
  const [deviceId, setDeviceId] = useState<string>('');

  useEffect(() => {
    if (!user) {
      router.replace('/');
      return;
    }
    loadSettings();
  }, [user]);

  const loadSettings = async () => {
    try {
      const id = Platform.OS === 'web'
        ? 'web_' + navigator.userAgent.slice(0, 50).replace(/[^a-zA-Z0-9]/g, '')
        : Application.androidId || Device.modelId || 'unknown';
      
      setDeviceId(id);

      // Load saved settings
      const savedStealth = await AsyncStorage.getItem('stealthMode');
      const savedContact = await AsyncStorage.getItem('emergencyContact');
      
      if (savedStealth) setStealthMode(savedStealth === 'true');
      if (savedContact) setEmergencyContact(savedContact);
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const toggleStealthMode = async (value: boolean) => {
    try {
      setStealthMode(value);
      await AsyncStorage.setItem('stealthMode', value.toString());
      
      if (value) {
        Alert.alert(
          'Stealth Mode Enabled',
          'App will minimize notifications and reduce visibility. Background monitoring continues.',
          [{ text: 'OK' }]
        );
      }
    } catch (error) {
      console.error('Error toggling stealth mode:', error);
    }
  };

  const saveEmergencyContact = async () => {
    try {
      await AsyncStorage.setItem('emergencyContact', emergencyContact);
      await update(ref(database, `devices/${deviceId}`), {
        emergencyContact,
      });
      
      Alert.alert('Success', 'Emergency contact saved');
    } catch (error) {
      console.error('Error saving emergency contact:', error);
      Alert.alert('Error', 'Failed to save emergency contact');
    }
  };

  const requestPermissions = async () => {
    Alert.alert(
      'Permissions',
      'Guardian Eye requires the following permissions:\n\n• Location (GPS tracking)\n• Camera (photo capture)\n• Background execution\n\nThese are essential for security features.',
      [{ text: 'OK' }]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#58A6FF" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Settings</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        {/* Device Info */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Device Information</Text>
          <View style={styles.card}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Device ID:</Text>
              <Text style={styles.infoValue}>{deviceId.slice(0, 20)}...</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Account:</Text>
              <Text style={styles.infoValue}>{user?.email}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Platform:</Text>
              <Text style={styles.infoValue}>{Platform.OS}</Text>
            </View>
          </View>
        </View>

        {/* Security Settings */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Security</Text>
          
          <View style={styles.card}>
            <View style={styles.settingRow}>
              <View style={styles.settingInfo}>
                <Ionicons name="eye-off" size={20} color="#58A6FF" />
                <View style={{ marginLeft: 12, flex: 1 }}>
                  <Text style={styles.settingTitle}>Stealth Mode</Text>
                  <Text style={styles.settingDescription}>Minimize app visibility</Text>
                </View>
              </View>
              <Switch
                value={stealthMode}
                onValueChange={toggleStealthMode}
                trackColor={{ false: '#30363d', true: '#238636' }}
                thumbColor={stealthMode ? '#2ea043' : '#6e7681'}
              />
            </View>
          </View>

          <TouchableOpacity style={styles.card} onPress={requestPermissions}>
            <View style={styles.settingRow}>
              <Ionicons name="shield-checkmark" size={20} color="#58A6FF" />
              <View style={{ marginLeft: 12, flex: 1 }}>
                <Text style={styles.settingTitle}>App Permissions</Text>
                <Text style={styles.settingDescription}>View required permissions</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color="#6e7681" />
            </View>
          </TouchableOpacity>
        </View>

        {/* Emergency Contact */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Emergency</Text>
          <View style={styles.card}>
            <Text style={styles.inputLabel}>Emergency Contact Email</Text>
            <TextInput
              style={styles.input}
              placeholder="email@example.com"
              placeholderTextColor="#6e7681"
              value={emergencyContact}
              onChangeText={setEmergencyContact}
              keyboardType="email-address"
              autoCapitalize="none"
            />
            <TouchableOpacity style={styles.saveButton} onPress={saveEmergencyContact}>
              <Text style={styles.saveButtonText}>Save Contact</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* About */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About</Text>
          <View style={styles.card}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Version:</Text>
              <Text style={styles.infoValue}>1.0.0 (Phase 2)</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Edition:</Text>
              <Text style={styles.infoValue}>Play Store Clean</Text>
            </View>
          </View>
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
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6e7681',
    marginBottom: 12,
    textTransform: 'uppercase',
  },
  card: {
    backgroundColor: '#161b22',
    borderRadius: 12,
    padding: 16,
    borderWidth: 1,
    borderColor: '#30363d',
    marginBottom: 8,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#30363d',
  },
  infoLabel: {
    fontSize: 14,
    color: '#6e7681',
  },
  infoValue: {
    fontSize: 14,
    color: '#fff',
    fontWeight: '500',
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  settingInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    color: '#fff',
    fontWeight: '500',
  },
  settingDescription: {
    fontSize: 12,
    color: '#6e7681',
    marginTop: 2,
  },
  inputLabel: {
    fontSize: 14,
    color: '#c9d1d9',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#0D1117',
    borderWidth: 1,
    borderColor: '#30363d',
    borderRadius: 6,
    padding: 12,
    color: '#fff',
    fontSize: 14,
    marginBottom: 12,
  },
  saveButton: {
    backgroundColor: '#238636',
    borderRadius: 6,
    padding: 12,
    alignItems: 'center',
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
});
