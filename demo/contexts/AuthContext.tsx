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

  // 驗證已存儲 token 的有效性
  const validateToken = async (storedToken: string) => {
    try {
      const userResponse = await fetch(`${API_URL}${API_ROUTES.ME}`, {
        headers: {
          'Authorization': `Bearer ${storedToken}`,
        },
      });
      
      if (userResponse.ok) {
        const userData: User = await userResponse.json();
        await AsyncStorage.setItem(AUTH_USER_KEY, JSON.stringify(userData));
        setUser(userData);
        setToken(storedToken);
        return true;
      } else {
        // Token 無效或過期，清除存儲的認證信息
        await AsyncStorage.removeItem(AUTH_TOKEN_KEY);
        await AsyncStorage.removeItem(AUTH_USER_KEY);
        return false;
      }
    } catch (error) {
      console.error('驗證 Token 時發生錯誤:', error);
      return false;
    }
  };

  // 在應用啟動時從 AsyncStorage 加載用戶數據
  useEffect(() => {
    const loadUserData = async () => {
      try {
        const storedToken = await AsyncStorage.getItem(AUTH_TOKEN_KEY);
        const storedUser = await AsyncStorage.getItem(AUTH_USER_KEY);
        
        if (storedToken) {
          console.log('發現已存儲的 token，正在驗證...');
          const isValid = await validateToken(storedToken);
          
          if (!isValid && storedUser) {
            // 顯示已過期的消息
            const userData = JSON.parse(storedUser);
            Alert.alert(
              '登入已過期',
              `${userData.username}，您的登入狀態已過期，請重新登入。`
            );
          }
        }
      } catch (error) {
        console.error('加載使用者數據時發生錯誤:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    loadUserData();
  }, []);

  // 定期檢查 token 有效性（例如每30分鐘）
  useEffect(() => {
    let tokenCheckInterval: NodeJS.Timeout;
    
    if (token) {
      tokenCheckInterval = setInterval(async () => {
        console.log('正在檢查 token 有效性...');
        const isValid = await validateToken(token);
        if (!isValid) {
          // Token 無效，清除計時器
          clearInterval(tokenCheckInterval);
        }
      }, 30 * 60 * 1000); // 30分鐘檢查一次
    }
    
    return () => {
      if (tokenCheckInterval) {
        clearInterval(tokenCheckInterval);
      }
    };
  }, [token]);

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
      
      // 如果用戶選擇「記住我」，則將 token 保存在 AsyncStorage
      if (data.remember !== false) {
        await AsyncStorage.setItem(AUTH_TOKEN_KEY, tokenData.access_token);
        await AsyncStorage.setItem(AUTH_USER_KEY, JSON.stringify(userData));
        console.log('用戶已選擇「記住我」，token 已保存');
      } else {
        // 如果用戶沒有選擇「記住我」，則僅在內存中保存 token，不使用 AsyncStorage
        console.log('用戶未選擇「記住我」，token 僅保存在內存中');
        // 可以選擇在這裡設置一個定時器，在一段時間後自動登出
        setTimeout(() => {
          logout();
          Alert.alert('登入已過期', '您的登入已過期，請重新登入。');
        }, 8 * 60 * 60 * 1000); // 假設設置為8小時後過期
      }
      
      setToken(tokenData.access_token);
      setUser(userData);
      
      // 顯示用戶特定信息
      Alert.alert(
        '登入成功', 
        `歡迎回來，${userData.username}！\n\n` +
        `帳號狀態: ${userData.is_active ? '啟用' : '停用'}\n` +
        `電子郵件: ${userData.email}\n` +
        `驗證狀態: ${userData.is_verified ? '已驗證' : '未驗證'}`
      );
      
      // 登入成功後導航到首頁
      router.replace('/');
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
      
      // 可以選擇在註冊後自動登入
      // await login({
      //   username: data.email, // 使用電子郵件作為登入使用者名稱
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
      Alert.alert('已登出', '您已成功登出系統');
    } catch (error) {
      console.error('登出時發生錯誤:', error);
      Alert.alert('錯誤', '登出時發生錯誤');
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