import React from 'react';
import { Image, View, StyleSheet } from 'react-native';

interface GuardianEyeLogoProps {
  size?: number;
}

export const GuardianEyeLogo: React.FC<GuardianEyeLogoProps> = ({ size = 100 }) => {
  return (
    <View style={[styles.container, { width: size, height: size }]}>
      <Image
        source={require('../assets/guardianeye_logo.svg')}
        style={{ width: size, height: size }}
        resizeMode="contain"
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
  },
});
