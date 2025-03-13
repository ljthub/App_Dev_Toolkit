import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, TouchableOpacity, Image, ActivityIndicator, SafeAreaView } from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import FontAwesome from '@expo/vector-icons/FontAwesome';

export default function VerifyEmailScreen() {
  const { verifyEmail } = useAuth();
  const [verificationStatus, setVerificationStatus] = useState<'pending' | 'success' | 'error'>('pending');
  const [errorMessage, setErrorMessage] = useState<string>('');
  
  // 從URL參數獲取token
  const params = useLocalSearchParams();
  const token = params.token as string;

  // 頁面加載時自動驗證
  useEffect(() => {
    if (token) {
      handleVerifyEmail();
    } else {
      setVerificationStatus('error');
      setErrorMessage('驗證失敗：未提供驗證令牌');
    }
  }, [token]);

  // 處理驗證函數
  const handleVerifyEmail = async () => {
    try {
      await verifyEmail(token);
      setVerificationStatus('success');
    } catch (error) {
      setVerificationStatus('error');
      setErrorMessage(error instanceof Error ? error.message : '驗證過程中發生錯誤');
    }
  };

  // 返回登入頁面
  const handleGoToLogin = () => {
    router.replace('/auth/login');
  };

  // 返回首頁
  const handleGoToHome = () => {
    router.replace('/');
  };

  // 根據不同狀態顯示不同內容
  const renderContent = () => {
    switch(verificationStatus) {
      case 'pending':
        return (
          <View style={styles.statusContainer}>
            <ActivityIndicator size="large" color="#4e5ae8" style={styles.loader} />
            <Text style={styles.statusText}>正在驗證您的電子郵件...</Text>
          </View>
        );
      
      case 'success':
        return (
          <View style={styles.statusContainer}>
            <View style={styles.iconContainer}>
              <FontAwesome name="check-circle" size={80} color="#4CAF50" />
            </View>
            <Text style={[styles.statusText, styles.successText]}>電子郵件驗證成功！</Text>
            <Text style={styles.descriptionText}>
              您的帳戶已成功驗證，現在可以使用所有功能。
            </Text>
            <TouchableOpacity
              style={styles.button}
              onPress={handleGoToLogin}
            >
              <Text style={styles.buttonText}>前往登入</Text>
            </TouchableOpacity>
          </View>
        );
      
      case 'error':
        return (
          <View style={styles.statusContainer}>
            <View style={styles.iconContainer}>
              <FontAwesome name="times-circle" size={80} color="#F44336" />
            </View>
            <Text style={[styles.statusText, styles.errorText]}>驗證失敗</Text>
            <Text style={styles.descriptionText}>{errorMessage}</Text>
            <Text style={styles.instructionText}>
              請嘗試重新點擊郵件中的驗證連結，或者聯繫客服獲取幫助。
            </Text>
            <TouchableOpacity
              style={styles.button}
              onPress={handleGoToHome}
            >
              <Text style={styles.buttonText}>返回首頁</Text>
            </TouchableOpacity>
          </View>
        );
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.title}>電子郵件驗證</Text>
        {renderContent()}
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
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 30,
    textAlign: 'center',
  },
  statusContainer: {
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
  },
  iconContainer: {
    marginBottom: 20,
  },
  statusText: {
    fontSize: 20,
    fontWeight: 'bold',
    marginVertical: 15,
    textAlign: 'center',
  },
  successText: {
    color: '#4CAF50',
  },
  errorText: {
    color: '#F44336',
  },
  descriptionText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
    lineHeight: 24,
  },
  instructionText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
    fontStyle: 'italic',
  },
  loader: {
    marginVertical: 20,
  },
  button: {
    backgroundColor: '#4e5ae8',
    borderRadius: 5,
    padding: 15,
    width: '100%',
    alignItems: 'center',
    marginTop: 20,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});