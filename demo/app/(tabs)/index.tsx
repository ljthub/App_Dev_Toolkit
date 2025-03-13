import React from 'react';
import { StyleSheet, View, Text, TouchableOpacity, ActivityIndicator, SafeAreaView } from 'react-native';
import { router } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';

export default function HomeScreen() {
  const { user, isAuthenticated, logout, isLoading, resendVerification } = useAuth();

  const handleLogin = () => {
    router.push('/auth/login');
  };

  const handleRegister = () => {
    router.push('/auth/register');
  };

  const handleLogout = () => {
    logout();
  };

  const handleResendVerification = async () => {
    await resendVerification();
  };

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>App Dev Toolkit Demo</Text>
      <Text style={styles.subtitle}>測試後端 API 功能</Text>

      {isLoading ? (
        <ActivityIndicator size="large" color="#4e5ae8" style={styles.loader} />
      ) : (
        <>
          {isAuthenticated ? (
            <View style={styles.userInfoContainer}>
              <Text style={styles.heading}>使用者資訊</Text>
              
              <View style={styles.infoRow}>
                <Text style={styles.label}>ID:</Text>
                <Text style={styles.value}>{user?.id}</Text>
              </View>
              
              <View style={styles.infoRow}>
                <Text style={styles.label}>使用者名稱:</Text>
                <Text style={styles.value}>{user?.username}</Text>
              </View>
              
              <View style={styles.infoRow}>
                <Text style={styles.label}>電子郵件:</Text>
                <Text style={styles.value}>{user?.email}</Text>
              </View>
              
              <View style={styles.infoRow}>
                <Text style={styles.label}>已驗證:</Text>
                <Text style={styles.value}>{user?.is_verified ? '是' : '否'}</Text>
              </View>
              
              <View style={styles.infoRow}>
                <Text style={styles.label}>建立時間:</Text>
                <Text style={styles.value}>
                  {user?.created_at ? new Date(user.created_at).toLocaleString() : 'N/A'}
                </Text>
              </View>
              
              {!user?.is_verified && (
                <TouchableOpacity
                  style={styles.secondaryButton}
                  onPress={handleResendVerification}
                >
                  <Text style={styles.secondaryButtonText}>重新發送驗證郵件</Text>
                </TouchableOpacity>
              )}
              
              <TouchableOpacity
                style={styles.button}
                onPress={handleLogout}
              >
                <Text style={styles.buttonText}>登出</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View style={styles.authContainer}>
              <Text style={styles.authText}>
                請登入或註冊以測試後端 API 功能
              </Text>
              
              <TouchableOpacity
                style={styles.button}
                onPress={handleLogin}
              >
                <Text style={styles.buttonText}>登入</Text>
              </TouchableOpacity>
              
              <TouchableOpacity
                style={styles.secondaryButton}
                onPress={handleRegister}
              >
                <Text style={styles.secondaryButtonText}>註冊新帳號</Text>
              </TouchableOpacity>
            </View>
          )}
        </>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f9f9f9',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginTop: 20,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginTop: 10,
    marginBottom: 30,
  },
  loader: {
    marginTop: 30,
  },
  authContainer: {
    width: '100%',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  authText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 20,
  },
  button: {
    backgroundColor: '#4e5ae8',
    borderRadius: 5,
    padding: 15,
    width: '100%',
    alignItems: 'center',
    marginTop: 15,
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
    marginTop: 15,
  },
  secondaryButtonText: {
    color: '#4e5ae8',
    fontSize: 16,
    fontWeight: 'bold',
  },
  userInfoContainer: {
    width: '100%',
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  heading: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
    textAlign: 'center',
  },
  infoRow: {
    flexDirection: 'row',
    marginBottom: 10,
    paddingBottom: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  label: {
    width: '40%',
    fontSize: 16,
    color: '#666',
    fontWeight: 'bold',
  },
  value: {
    width: '60%',
    fontSize: 16,
    color: '#333',
  },
});
