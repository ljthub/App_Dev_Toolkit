import React, { useState } from 'react';
import { StyleSheet, View, TextInput, Text, TouchableOpacity, ActivityIndicator, ScrollView } from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { router } from 'expo-router';

export default function RegisterScreen() {
  const { register, isLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<{ 
    email?: string; 
    username?: string; 
    password?: string;
    confirmPassword?: string;
  }>({});

  const validate = () => {
    const newErrors: { 
      email?: string; 
      username?: string; 
      password?: string;
      confirmPassword?: string;
    } = {};
    
    // 驗證電子郵件
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email.trim()) {
      newErrors.email = '請輸入電子郵件';
    } else if (!emailRegex.test(email)) {
      newErrors.email = '請輸入有效的電子郵件';
    }
    
    // 驗證使用者名稱
    if (!username.trim()) {
      newErrors.username = '請輸入使用者名稱';
    } else if (username.length < 3) {
      newErrors.username = '使用者名稱必須至少包含 3 個字符';
    }
    
    // 驗證密碼
    if (!password) {
      newErrors.password = '請輸入密碼';
    } else if (password.length < 6) {
      newErrors.password = '密碼必須至少包含 6 個字符';
    }
    
    // 驗證確認密碼
    if (!confirmPassword) {
      newErrors.confirmPassword = '請再次輸入密碼';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = '兩次輸入的密碼不一致';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleRegister = async () => {
    if (validate()) {
      await register({ email, username, password });
    }
  };

  const navigateToLogin = () => {
    router.back();
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.formContainer}>
        <Text style={styles.title}>註冊帳號</Text>
        
        <View style={styles.inputGroup}>
          <Text style={styles.label}>電子郵件</Text>
          <TextInput
            style={styles.input}
            value={email}
            onChangeText={setEmail}
            placeholder="請輸入電子郵件"
            autoCapitalize="none"
            keyboardType="email-address"
          />
          {errors.email ? <Text style={styles.errorText}>{errors.email}</Text> : null}
        </View>
        
        <View style={styles.inputGroup}>
          <Text style={styles.label}>使用者名稱</Text>
          <TextInput
            style={styles.input}
            value={username}
            onChangeText={setUsername}
            placeholder="請輸入使用者名稱"
            autoCapitalize="none"
          />
          {errors.username ? <Text style={styles.errorText}>{errors.username}</Text> : null}
        </View>
        
        <View style={styles.inputGroup}>
          <Text style={styles.label}>密碼</Text>
          <TextInput
            style={styles.input}
            value={password}
            onChangeText={setPassword}
            placeholder="請輸入密碼"
            secureTextEntry
          />
          {errors.password ? <Text style={styles.errorText}>{errors.password}</Text> : null}
        </View>
        
        <View style={styles.inputGroup}>
          <Text style={styles.label}>確認密碼</Text>
          <TextInput
            style={styles.input}
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            placeholder="請再次輸入密碼"
            secureTextEntry
          />
          {errors.confirmPassword ? <Text style={styles.errorText}>{errors.confirmPassword}</Text> : null}
        </View>
        
        <TouchableOpacity
          style={styles.button}
          onPress={handleRegister}
          disabled={isLoading}
        >
          {isLoading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>註冊</Text>
          )}
        </TouchableOpacity>
        
        <View style={styles.loginContainer}>
          <Text style={styles.loginText}>已經有帳號？</Text>
          <TouchableOpacity onPress={navigateToLogin}>
            <Text style={styles.loginLink}>返回登入</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9f9f9',
    padding: 20,
  },
  formContainer: {
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 20,
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
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
    textAlign: 'center',
  },
  inputGroup: {
    marginBottom: 15,
  },
  label: {
    fontSize: 16,
    marginBottom: 5,
    color: '#333',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 5,
    padding: 10,
    fontSize: 16,
  },
  errorText: {
    color: 'red',
    fontSize: 14,
    marginTop: 5,
  },
  button: {
    backgroundColor: '#4e5ae8',
    borderRadius: 5,
    padding: 15,
    alignItems: 'center',
    marginTop: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  loginContainer: {
    flexDirection: 'row',
    marginTop: 20,
    justifyContent: 'center',
  },
  loginText: {
    color: '#666',
    fontSize: 14,
  },
  loginLink: {
    color: '#4e5ae8',
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 5,
  },
}); 