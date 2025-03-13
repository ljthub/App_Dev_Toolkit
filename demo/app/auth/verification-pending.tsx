import React from 'react';
import { StyleSheet, View, Text, TouchableOpacity, SafeAreaView, ScrollView } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import FontAwesome from '@expo/vector-icons/FontAwesome';

export default function VerificationPendingScreen() {
  const { resendVerification, isLoading } = useAuth();
  const params = useLocalSearchParams();
  const email = params.email as string;

  const handleResendVerification = async () => {
    if (email) {
      await resendVerification(email);
    } else {
      await resendVerification();
    }
  };

  const handleBackToLogin = () => {
    router.replace('/auth/login');
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.iconContainer}>
          <FontAwesome name="envelope" size={80} color="#4e5ae8" />
        </View>

        <Text style={styles.title}>請驗證您的電子郵件</Text>
        
        <View style={styles.infoContainer}>
          <Text style={styles.infoText}>
            我們已經發送了一封驗證郵件到：
          </Text>
          <Text style={styles.emailText}>{email || '您的電子郵件地址'}</Text>
          <Text style={styles.infoText}>
            請查看您的收件箱，點擊郵件中的驗證連結以完成帳號註冊。
          </Text>
        </View>

        <View style={styles.instructionsContainer}>
          <Text style={styles.instructionsTitle}>沒有收到驗證郵件？</Text>
          <Text style={styles.instructionsText}>• 請檢查您的垃圾郵件資料夾</Text>
          <Text style={styles.instructionsText}>• 確認您輸入的電子郵件地址正確</Text>
          <Text style={styles.instructionsText}>• 點擊下方按鈕重新發送驗證郵件</Text>
        </View>

        <TouchableOpacity
          style={styles.button}
          onPress={handleResendVerification}
          disabled={isLoading}
        >
          <Text style={styles.buttonText}>重新發送驗證郵件</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.secondaryButton}
          onPress={handleBackToLogin}
        >
          <Text style={styles.secondaryButtonText}>返回登入頁面</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9f9f9',
  },
  scrollContent: {
    padding: 20,
    alignItems: 'center',
  },
  iconContainer: {
    marginVertical: 20,
  },
  icon: {
    width: 120,
    height: 120,
    resizeMode: 'contain',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 20,
  },
  infoContainer: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 20,
    width: '100%',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    marginBottom: 20,
  },
  infoText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 10,
  },
  emailText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4e5ae8',
    marginBottom: 10,
  },
  instructionsContainer: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 20,
    width: '100%',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
    marginBottom: 20,
  },
  instructionsTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  instructionsText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  button: {
    backgroundColor: '#4e5ae8',
    borderRadius: 5,
    padding: 15,
    width: '100%',
    alignItems: 'center',
    marginBottom: 15,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#4e5ae8',
    borderRadius: 5,
    padding: 15,
    width: '100%',
    alignItems: 'center',
  },
  secondaryButtonText: {
    color: '#4e5ae8',
    fontSize: 16,
    fontWeight: 'bold',
  },
}); 