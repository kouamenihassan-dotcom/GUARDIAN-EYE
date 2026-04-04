import React, { createContext, useState, useEffect, useContext } from 'react';
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  User,
} from 'firebase/auth';
import { ref, set, get } from 'firebase/database';
import { auth, database } from '@/services/firebase';
import * as Device from 'expo-device';
import * as Application from 'expo-application';
import { Platform } from 'react-native';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signUp: (email: string, password: string) => Promise<void>;
  signIn: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Get unique device ID
  const getDeviceId = async () => {
    if (Platform.OS === 'web') {
      // For web, use a combination of factors
      return 'web_' + navigator.userAgent.slice(0, 50).replace(/[^a-zA-Z0-9]/g, '');
    }
    // For mobile, use Application ID
    const deviceId = Application.androidId || Device.modelId || 'unknown';
    return deviceId;
  };

  // Register device in Firebase
  const registerDevice = async (userId: string) => {
    try {
      const deviceId = await getDeviceId();
      const deviceInfo = {
        deviceId,
        userId,
        deviceName: Device.deviceName || 'Unknown Device',
        modelName: Device.modelName || 'Unknown Model',
        osName: Device.osName || Platform.OS,
        osVersion: Device.osVersion || 'Unknown',
        platform: Platform.OS,
        status: 'NORMAL',
        lastSeen: Date.now(),
        registeredAt: Date.now(),
      };

      // Save device to Firebase
      await set(ref(database, `devices/${deviceId}`), deviceInfo);
      
      // Add device to user's device list
      const userDevicesRef = ref(database, `users/${userId}/devices/${deviceId}`);
      await set(userDevicesRef, true);

      console.log('Device registered successfully:', deviceId);
    } catch (error) {
      console.error('Error registering device:', error);
    }
  };

  // Sign up function
  const signUp = async (email: string, password: string) => {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const userId = userCredential.user.uid;
      
      // Create user profile
      await set(ref(database, `users/${userId}`), {
        email,
        createdAt: Date.now(),
      });

      // Register device
      await registerDevice(userId);
    } catch (error: any) {
      throw new Error(error.message);
    }
  };

  // Sign in function
  const signIn = async (email: string, password: string) => {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      // Register/update device on login
      await registerDevice(userCredential.user.uid);
    } catch (error: any) {
      throw new Error(error.message);
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await signOut(auth);
    } catch (error: any) {
      throw new Error(error.message);
    }
  };

  // Listen to auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const value = {
    user,
    loading,
    signUp,
    signIn,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
