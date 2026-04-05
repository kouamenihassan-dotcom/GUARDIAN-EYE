import * as Crypto from 'expo-crypto';
import AsyncStorage from '@react-native-async-storage/async-storage';

class EncryptionServiceClass {
  private encryptionKey: string = 'GUARDIAN_EYE_SECRET_KEY_2025'; // In production, use secure key generation

  // Simple XOR encryption for demonstration
  // In production, use proper encryption libraries
  encrypt(data: string): string {
    try {
      const encrypted = Buffer.from(data)
        .toString('base64')
        .split('')
        .map((char, i) => 
          String.fromCharCode(char.charCodeAt(0) ^ this.encryptionKey.charCodeAt(i % this.encryptionKey.length))
        )
        .join('');
      
      return Buffer.from(encrypted).toString('base64');
    } catch (error) {
      console.error('Encryption error:', error);
      return data;
    }
  }

  decrypt(encryptedData: string): string {
    try {
      const decoded = Buffer.from(encryptedData, 'base64').toString();
      const decrypted = decoded
        .split('')
        .map((char, i) => 
          String.fromCharCode(char.charCodeAt(0) ^ this.encryptionKey.charCodeAt(i % this.encryptionKey.length))
        )
        .join('');
      
      return Buffer.from(decrypted, 'base64').toString();
    } catch (error) {
      console.error('Decryption error:', error);
      return encryptedData;
    }
  }

  async secureStore(key: string, value: string): Promise<void> {
    try {
      const encrypted = this.encrypt(value);
      await AsyncStorage.setItem(`secure_${key}`, encrypted);
    } catch (error) {
      console.error('Secure store error:', error);
    }
  }

  async secureRetrieve(key: string): Promise<string | null> {
    try {
      const encrypted = await AsyncStorage.getItem(`secure_${key}`);
      if (!encrypted) return null;
      return this.decrypt(encrypted);
    } catch (error) {
      console.error('Secure retrieve error:', error);
      return null;
    }
  }

  async generateHash(data: string): Promise<string> {
    try {
      const hash = await Crypto.digestStringAsync(
        Crypto.CryptoDigestAlgorithm.SHA256,
        data
      );
      return hash;
    } catch (error) {
      console.error('Hash generation error:', error);
      return '';
    }
  }
}

export const EncryptionService = new EncryptionServiceClass();
