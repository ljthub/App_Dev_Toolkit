import React from 'react';
import { StyleSheet, View, Text, TouchableOpacity, ActivityIndicator, SafeAreaView, ScrollView } from 'react-native';
import { router } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import FontAwesome from '@expo/vector-icons/FontAwesome';

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
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>App Dev Toolkit Demo</Text>
        <Text style={styles.subtitle}>測試後端 API 功能</Text>

        {isLoading ? (
          <ActivityIndicator size="large" color="#4e5ae8" style={styles.loader} />
        ) : (
          <>
            {isAuthenticated ? (
              <View style={styles.authenticatedContainer}>
                <View style={styles.welcomeCard}>
                  <FontAwesome name="user-circle" size={50} color="#4e5ae8" style={styles.welcomeIcon} />
                  <Text style={styles.welcomeText}>歡迎，{user?.username}！</Text>
                  {!user?.is_verified && (
                    <View style={styles.verificationBanner}>
                      <FontAwesome name="exclamation-triangle" size={16} color="#ff9800" style={styles.verificationIcon} />
                      <Text style={styles.verificationText}>您的帳戶尚未驗證</Text>
                    </View>
                  )}
                </View>
                
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
                    <Text style={[styles.value, user?.is_verified ? styles.verifiedText : styles.unverifiedText]}>
                      {user?.is_verified ? '是' : '否'}
                    </Text>
                  </View>
                  
                  <View style={styles.infoRow}>
                    <Text style={styles.label}>狀態:</Text>
                    <Text style={[styles.value, user?.is_active ? styles.activeText : styles.inactiveText]}>
                      {user?.is_active ? '啟用' : '停用'}
                    </Text>
                  </View>
                  
                  <View style={styles.infoRow}>
                    <Text style={styles.label}>建立時間:</Text>
                    <Text style={styles.value}>
                      {user?.created_at ? new Date(user.created_at).toLocaleString() : 'N/A'}
                    </Text>
                  </View>
                </View>
                
                <View style={styles.actionsContainer}>
                  <Text style={styles.heading}>帳戶操作</Text>
                  
                  {!user?.is_verified && (
                    <TouchableOpacity
                      style={styles.actionButton}
                      onPress={handleResendVerification}
                    >
                      <FontAwesome name="envelope" size={18} color="#4e5ae8" style={styles.actionIcon} />
                      <Text style={styles.actionText}>重新發送驗證郵件</Text>
                    </TouchableOpacity>
                  )}
                  
                  <TouchableOpacity
                    style={styles.actionButton}
                    onPress={() => router.push('/auth/verification-pending')}
                  >
                    <FontAwesome name="info-circle" size={18} color="#4e5ae8" style={styles.actionIcon} />
                    <Text style={styles.actionText}>查看驗證頁面</Text>
                  </TouchableOpacity>
                  
                  <TouchableOpacity
                    style={[styles.actionButton, styles.logoutButton]}
                    onPress={handleLogout}
                  >
                    <FontAwesome name="sign-out" size={18} color="#f44336" style={styles.actionIcon} />
                    <Text style={[styles.actionText, styles.logoutText]}>登出</Text>
                  </TouchableOpacity>
                </View>
              </View>
            ) : (
              <View style={styles.authContainer}>
                <FontAwesome name="lock" size={50} color="#4e5ae8" style={styles.authIcon} />
                <Text style={styles.authTitle}>訪問受限</Text>
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
  authenticatedContainer: {
    width: '100%',
  },
  welcomeCard: {
    width: '100%',
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 20,
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
  welcomeIcon: {
    marginBottom: 10,
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  verificationBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff8e1',
    borderRadius: 5,
    padding: 10,
    width: '100%',
    marginTop: 10,
  },
  verificationIcon: {
    marginRight: 10,
  },
  verificationText: {
    color: '#ff9800',
    fontWeight: 'bold',
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
  authIcon: {
    marginBottom: 20,
  },
  authTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
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
    marginBottom: 20,
  },
  actionsContainer: {
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
    marginBottom: 20,
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
  verifiedText: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  unverifiedText: {
    color: '#F44336',
    fontWeight: 'bold',
  },
  activeText: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  inactiveText: {
    color: '#F44336',
    fontWeight: 'bold',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    borderRadius: 5,
    padding: 15,
    marginBottom: 10,
  },
  actionIcon: {
    marginRight: 15,
  },
  actionText: {
    fontSize: 16,
    color: '#333',
  },
  logoutButton: {
    backgroundColor: '#ffebee',
  },
  logoutText: {
    color: '#f44336',
  },
});
