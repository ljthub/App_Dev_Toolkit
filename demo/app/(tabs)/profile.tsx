import React from 'react';
import { StyleSheet, View, Text, TouchableOpacity, ActivityIndicator, SafeAreaView, ScrollView, Alert } from 'react-native';
import { router } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import FontAwesome from '@expo/vector-icons/FontAwesome';

export default function ProfileScreen() {
  const { user, isAuthenticated, logout, isLoading, resendVerification } = useAuth();

  // 如果沒有登入，重定向到登入頁面
  React.useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      router.replace('/auth/login');
    }
  }, [isAuthenticated, isLoading]);

  const handleLogout = () => {
    Alert.alert(
      '確認登出',
      '您確定要登出嗎？',
      [
        {
          text: '取消',
          style: 'cancel'
        },
        {
          text: '確定',
          onPress: () => logout()
        }
      ]
    );
  };

  const handleResendVerification = async () => {
    await resendVerification();
  };

  const handleChangePassword = () => {
    // 實現修改密碼邏輯
    Alert.alert('功能開發中', '密碼修改功能正在開發中...');
  };

  const handleEditProfile = () => {
    // 實現編輯個人資料邏輯
    Alert.alert('功能開發中', '個人資料編輯功能正在開發中...');
  };

  if (isLoading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#4e5ae8" />
          <Text style={styles.loadingText}>載入中...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (!user) {
    return null; // 將由 useEffect 重定向到登入頁面
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <FontAwesome name="user-circle" size={100} color="#4e5ae8" />
          <Text style={styles.username}>{user.username}</Text>
          <Text style={styles.email}>{user.email}</Text>
          {!user.is_verified && (
            <View style={styles.verificationBanner}>
              <FontAwesome name="exclamation-triangle" size={16} color="#ff9800" style={styles.verificationIcon} />
              <Text style={styles.verificationText}>您的帳戶尚未驗證</Text>
            </View>
          )}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>帳戶詳情</Text>
          
          <View style={styles.infoRow}>
            <Text style={styles.label}>帳戶ID:</Text>
            <Text style={styles.value}>{user.id}</Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.label}>帳戶狀態:</Text>
            <Text style={[styles.value, user.is_active ? styles.activeText : styles.inactiveText]}>
              {user.is_active ? '啟用' : '停用'}
            </Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.label}>驗證狀態:</Text>
            <Text style={[styles.value, user.is_verified ? styles.verifiedText : styles.unverifiedText]}>
              {user.is_verified ? '已驗證' : '未驗證'}
            </Text>
          </View>
          
          <View style={styles.infoRow}>
            <Text style={styles.label}>註冊日期:</Text>
            <Text style={styles.value}>
              {new Date(user.created_at).toLocaleDateString('zh-TW')}
            </Text>
          </View>
          
          {user.updated_at && (
            <View style={styles.infoRow}>
              <Text style={styles.label}>最後更新:</Text>
              <Text style={styles.value}>
                {new Date(user.updated_at).toLocaleDateString('zh-TW')}
              </Text>
            </View>
          )}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>帳戶操作</Text>
          
          <TouchableOpacity style={styles.actionButton} onPress={handleEditProfile}>
            <FontAwesome name="edit" size={18} color="#4e5ae8" style={styles.actionIcon} />
            <Text style={styles.actionText}>編輯個人資料</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.actionButton} onPress={handleChangePassword}>
            <FontAwesome name="lock" size={18} color="#4e5ae8" style={styles.actionIcon} />
            <Text style={styles.actionText}>修改密碼</Text>
          </TouchableOpacity>
          
          {!user.is_verified && (
            <TouchableOpacity style={styles.actionButton} onPress={handleResendVerification}>
              <FontAwesome name="envelope" size={18} color="#4e5ae8" style={styles.actionIcon} />
              <Text style={styles.actionText}>重新發送驗證郵件</Text>
            </TouchableOpacity>
          )}
          
          <TouchableOpacity style={[styles.actionButton, styles.logoutButton]} onPress={handleLogout}>
            <FontAwesome name="sign-out" size={18} color="#f44336" style={styles.actionIcon} />
            <Text style={[styles.actionText, styles.logoutText]}>登出</Text>
          </TouchableOpacity>
        </View>
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
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  header: {
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  username: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 15,
  },
  email: {
    fontSize: 16,
    color: '#666',
    marginTop: 5,
  },
  verificationBanner: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff8e1',
    borderRadius: 5,
    padding: 10,
    marginTop: 15,
    width: '100%',
  },
  verificationIcon: {
    marginRight: 10,
  },
  verificationText: {
    color: '#ff9800',
    fontWeight: 'bold',
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  infoRow: {
    flexDirection: 'row',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  label: {
    width: '35%',
    fontSize: 16,
    color: '#666',
  },
  value: {
    flex: 1,
    fontSize: 16,
    color: '#333',
  },
  activeText: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  inactiveText: {
    color: '#F44336',
    fontWeight: 'bold',
  },
  verifiedText: {
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  unverifiedText: {
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