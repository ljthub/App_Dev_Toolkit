import FontAwesome from '@expo/vector-icons/FontAwesome';
import { Tabs } from 'expo-router';
import React, { useEffect } from 'react';
import { Platform } from 'react-native';

import { HapticTab } from '@/components/HapticTab';
import { IconSymbol } from '@/components/ui/IconSymbol';
import TabBarBackground from '@/components/ui/TabBarBackground';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';
import { useAuth } from '@/contexts/AuthContext';
import { router } from 'expo-router';

/**
 * 你可以用這個模式來讓特定圖示路徑指向 FontAwesome
 */
function TabBarIcon(props: {
  name: React.ComponentProps<typeof FontAwesome>['name'];
  color: string;
}) {
  return <FontAwesome size={28} style={{ marginBottom: -3 }} {...props} />;
}

export default function TabLayout() {
  const colorScheme = useColorScheme();
  const { isAuthenticated, user } = useAuth();

  // 可以選擇在這裡檢查用戶是否已經登入
  useEffect(() => {
    if (!isAuthenticated) {
      // 如果用戶未登入，可以選擇重定向到登入頁面
      // 但我們不一定要強制登入，因為首頁可以顯示給未登入用戶
      // router.replace('/auth/login');
    }
  }, [isAuthenticated]);

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: Colors[colorScheme ?? 'light'].tint,
        headerShown: false,
        tabBarButton: HapticTab,
        tabBarBackground: TabBarBackground,
        tabBarStyle: Platform.select({
          ios: {
            // Use a transparent background on iOS to show the blur effect
            position: 'absolute',
          },
          default: {},
        }),
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: '首頁',
          tabBarIcon: ({ color }) => <TabBarIcon name="home" color={color} />,
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: 'API 資訊',
          tabBarIcon: ({ color }) => <TabBarIcon name="code" color={color} />,
        }}
      />
      {isAuthenticated && (
        <Tabs.Screen
          name="profile"
          options={{
            title: '個人資料',
            tabBarIcon: ({ color }) => <TabBarIcon name="user" color={color} />,
          }}
        />
      )}
      {/* 如果需要載入驗證頁面作為標籤頁，可以加入 */}
      <Tabs.Screen
        name="verifyemail"
        options={{
          title: '驗證郵件',
          tabBarIcon: ({ color }) => <TabBarIcon name="envelope" color={color} />,
          href: null,  // 隱藏此標籤，但保留路由
        }}
      />
    </Tabs>
  );
}
