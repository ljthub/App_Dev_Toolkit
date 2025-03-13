import React, { createContext, useState, useEffect, useContext } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Alert } from 'react-native';
import { router } from 'expo-router';
import { API_URL, API_ROUTES, AUTH_TOKEN_KEY, AUTH_USER_KEY } from '../constants/Config';
import { 
  User, 
  Token, 
  LoginRequest, 
  RegisterRequest, 
  EmailVerificationRequest,
  AuthContextType 
} from '../types/auth';

// 創建認證上下文
const AuthContext = createContext<AuthContextType | null>(null);

// 認證上下文提供者
export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 在應用啟動時從 AsyncStorage 加載用戶數據
  useEffect(() => {
    const loadUserData = async () => {
      try {
        const storedToken = await AsyncStorage.getItem(AUTH_TOKEN_KEY);
        const storedUser = await AsyncStorage.getItem(AUTH_USER_KEY);
        
        if (storedToken && storedUser) {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
        }
      } catch (error) {
        console.error('加載使用者數據時發生錯誤:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadUserData();
  }, []);

  // 登入功能
  const login = async (data: LoginRequest) => {
    setIsLoading(true);
    console.log(`${API_URL}${API_ROUTES.LOGIN}`);
    try {
      const response = await fetch(`${API_URL}${API_ROUTES.LOGIN}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: data.username,
          password: data.password,
        }).toString(),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '登入失敗');
      }
      
      const tokenData: Token = await response.json();
      
      // 獲取用戶資料
      const userResponse = await fetch(`${API_URL}${API_ROUTES.ME}`, {
        headers: {
          'Authorization': `Bearer ${tokenData.access_token}`,
        },
      });
      
      if (!userResponse.ok) {
        throw new Error('無法獲取使用者資料');
      }
      
      const userData: User = await userResponse.json();
      
      // 存儲數據
      await AsyncStorage.setItem(AUTH_TOKEN_KEY, tokenData.access_token);
      await AsyncStorage.setItem(AUTH_USER_KEY, JSON.stringify(userData));
      
      setToken(tokenData.access_token);
      setUser(userData);
      
      Alert.alert('成功', '登入成功');
    } catch (error) {
      Alert.alert('錯誤', error instanceof Error ? error.message : '登入時發生錯誤');
    } finally {
      setIsLoading(false);
    }
  };

  // 註冊功能
  const register = async (data: RegisterRequest) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}${API_ROUTES.REGISTER}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '註冊失敗');
      }
      
      const userData: User = await response.json();
      
      // 註冊成功後，不再顯示提示框，直接導航到等待驗證頁面
      router.replace({
        pathname: '/auth/verification-pending',
        params: { email: data.email }
      });
      
      // 移除自動登入邏輯
      // await login({
      //   username: data.username,
      //   password: data.password
      // });
    } catch (error) {
      Alert.alert('錯誤', error instanceof Error ? error.message : '註冊時發生錯誤');
    } finally {
      setIsLoading(false);
    }
  };

  // 登出功能
  const logout = async () => {
    try {
      await AsyncStorage.removeItem(AUTH_TOKEN_KEY);
      await AsyncStorage.removeItem(AUTH_USER_KEY);
      setToken(null);
      setUser(null);
    } catch (error) {
      console.error('登出時發生錯誤:', error);
    }
  };

  // 電子郵件驗證功能
  const verifyEmail = async (verificationToken: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_URL}${API_ROUTES.VERIFY_EMAIL}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: verificationToken } as EmailVerificationRequest),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '電子郵件驗證失敗');
      }
      
      // 更新用戶資料
      if (token) {
        const userResponse = await fetch(`${API_URL}${API_ROUTES.ME}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (userResponse.ok) {
          const userData: User = await userResponse.json();
          await AsyncStorage.setItem(AUTH_USER_KEY, JSON.stringify(userData));
          setUser(userData);
        }
      }
      
      Alert.alert('成功', '您的電子郵件已成功驗證');
    } catch (error) {
      Alert.alert('錯誤', error instanceof Error ? error.message : '電子郵件驗證時發生錯誤');
    } finally {
      setIsLoading(false);
    }
  };

  // 重新發送驗證電子郵件
  const resendVerification = async (email?: string) => {
    setIsLoading(true);
    try {
      // 如果已登入，使用帳戶的已有身份發送請求
      if (token) {
        const response = await fetch(`${API_URL}${API_ROUTES.RESEND_VERIFICATION}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || '無法重新發送驗證電子郵件');
        }
      } 
      // 如果未登入但提供了電子郵件，使用公開端點發送請求
      else if (email) {
        const response = await fetch(`${API_URL}${API_ROUTES.RESEND_VERIFICATION_PUBLIC}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email }),
        });
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || '無法重新發送驗證電子郵件');
        }
      } 
      // 未登入且未提供電子郵件
      else {
        throw new Error('您必須提供電子郵件地址或已登入才能重新發送驗證郵件');
      }
      
      Alert.alert('成功', '驗證電子郵件已重新發送，請檢查您的收件箱');
    } catch (error) {
      Alert.alert('錯誤', error instanceof Error ? error.message : '重新發送驗證電子郵件時發生錯誤');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        register,
        logout,
        verifyEmail,
        resendVerification,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// 使用認證上下文的 Hook
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error('useAuth 必須在 AuthProvider 內部使用');
  }
  return context;
};

export default AuthContext; 