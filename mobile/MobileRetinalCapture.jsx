import React, { useState, useRef, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { Camera } from 'expo-camera';

const MobileRetinalCapture = ({ navigation }) => {
  const [hasPermission, setHasPermission] = useState(null);
  const [imageQuality, setImageQuality] = useState(null);
  const [processing, setProcessing] = useState(false);
  const cameraRef = useRef(null);

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  const checkImageQuality = async (base64Image) => {
    const response = await fetch('https://api.retinascan.ai/quality', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: base64Image }),
    });
    return response.json();
  };

  const processRetinalImage = async (base64Image) => {
    const response = await fetch('https://api.retinascan.ai/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: base64Image }),
    });
    return response.json();
  };

  const captureImage = async () => {
    if (!cameraRef.current) return;
    try {
      setProcessing(true);
      const photo = await cameraRef.current.takePictureAsync({ quality: 1, base64: true });
      const qualityCheck = await checkImageQuality(photo.base64);

      if (!qualityCheck.acceptable) {
        Alert.alert('Image Quality Issue', (qualityCheck.feedback || []).join('\n'), [
          { text: 'Retake', onPress: () => setProcessing(false) },
        ]);
        return;
      }

      setImageQuality({ grade: qualityCheck.grade, confidence: qualityCheck.confidence });
      const result = await processRetinalImage(photo.base64);
      if (navigation && navigation.navigate) {
        navigation.navigate('Results', { data: result });
      }
    } catch (err) {
      Alert.alert('Capture Error', err?.message || 'Unknown error');
    } finally {
      setProcessing(false);
    }
  };

  if (hasPermission === null) {
    return (
      <View style={styles.centered}><Text>Requesting camera permission...</Text></View>
    );
  }
  if (hasPermission === false) {
    return (
      <View style={styles.centered}><Text>No access to camera</Text></View>
    );
  }

  return (
    <View style={styles.container}>
      <Camera style={styles.camera} type={Camera.Constants.Type.back} ref={cameraRef}>
        <View style={styles.overlay}>
          <View style={styles.targetCircle} />
          <Text style={styles.instruction}>Align retina within circle. Hold steady.</Text>
        </View>
      </Camera>

      <TouchableOpacity style={styles.captureButton} onPress={captureImage} disabled={processing}>
        <Text style={styles.captureText}>{processing ? 'Processing...' : 'Capture Retinal Image'}</Text>
      </TouchableOpacity>

      {imageQuality && (
        <View style={styles.qualityIndicator}>
          <Text>Quality: {imageQuality.grade}</Text>
          <Text>Confidence: {Math.round((imageQuality.confidence || 0) * 100)}%</Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  centered: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  camera: { flex: 1 },
  overlay: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  targetCircle: { width: 300, height: 300, borderRadius: 150, borderWidth: 3, borderColor: '#00ff00', opacity: 0.7 },
  instruction: { marginTop: 20, color: '#fff', fontSize: 16, textAlign: 'center', padding: 10, backgroundColor: 'rgba(0,0,0,0.5)' },
  captureButton: { position: 'absolute', bottom: 30, alignSelf: 'center', backgroundColor: '#007AFF', paddingHorizontal: 30, paddingVertical: 15, borderRadius: 25 },
  captureText: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  qualityIndicator: { position: 'absolute', top: 50, right: 20, backgroundColor: 'rgba(255,255,255,0.9)', padding: 10, borderRadius: 10 },
});

export default MobileRetinalCapture;


