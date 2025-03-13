import React, { useEffect } from 'react';
import { StyleSheet, View, Text, TouchableOpacity, SafeAreaView } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import FontAwesome from '@expo/vector-icons/FontAwesome';

export default function VerificationSuccessScreen() {
  const { verifyEmail, isLoading } = useAuth();
  const params = useLocalSearchParams();
  const token = params.token as string;

  // 當頁面加載時自動驗證令牌
  useEffect(() => {
    if (token) {
      handleVerifyEmail();
    }
  }, [token]);

  const handleVerifyEmail = async () => {
    if (token) {
      await verifyEmail(token);
    }
  };

  const handleGoToLogin = () => {
    router.replace('/auth/login');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.iconContainer}>
          <FontAwesome name="check-circle" size={80} color="#4CAF50" />
        </View>

        <Text style={styles.title}>電子郵件已驗證</Text>
        
        <View style={styles.messageContainer}>
          <Text style={styles.messageText}>
            您的電子郵件已成功驗證！現在您可以使用完整的帳戶功能。
          </Text>
        </View>

        <TouchableOpacity
          style={styles.button}
          onPress={handleGoToLogin}
          disabled={isLoading}
        >
          <Text style={styles.buttonText}>前往登入</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9f9f9',
  },
  content: {
    flex: 1,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  iconContainer: {
    marginBottom: 30,
  },
  icon: {
    width: 150,
    height: 150,
    resizeMode: 'contain',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#4CAF50',
    textAlign: 'center',
    marginBottom: 20,
  },
  messageContainer: {
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
    marginBottom: 30,
  },
  messageText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
  },
  button: {
    backgroundColor: '#4e5ae8',
    borderRadius: 5,
    padding: 15,
    width: '100%',
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
}); 