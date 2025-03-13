import FontAwesome from '@expo/vector-icons/FontAwesome';
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import { useColorScheme } from 'react-native';
import { AuthProvider } from '../contexts/AuthContext';

export {
  // Catch any errors thrown by the Layout component.
  ErrorBoundary,
} from 'expo-router';

export const unstable_settings = {
  // Ensure that reloading on `/modal` keeps a back button present.
  initialRouteName: '(tabs)',
};

// Prevent the splash screen from auto-hiding before asset loading is complete.
SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [loaded, error] = useFonts({
    SpaceMono: require('../assets/fonts/SpaceMono-Regular.ttf'),
    ...FontAwesome.font,
  });

  // Expo Router uses Error Boundaries to catch errors in the navigation tree.
  useEffect(() => {
    if (error) throw error;
  }, [error]);

  useEffect(() => {
    if (loaded) {
      SplashScreen.hideAsync();
    }
  }, [loaded]);

  if (!loaded) {
    return null;
  }

  return <RootLayoutNav />;
}

function RootLayoutNav() {
  const colorScheme = useColorScheme();

  return (
    <AuthProvider>
      <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
        <Stack>
          <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
          <Stack.Screen name="modal" options={{ presentation: 'modal' }} />
          <Stack.Screen name="auth/login" options={{ title: '登入', headerShown: true }} />
          <Stack.Screen name="auth/register" options={{ title: '註冊', headerShown: true }} />
          <Stack.Screen 
            name="auth/verification-pending" 
            options={{ 
              title: '等待驗證', 
              headerShown: true,
              // 禁止用手勢返回
              gestureEnabled: false,
              // 禁止使用返回按鈕返回
              headerBackVisible: false 
            }} 
          />
          <Stack.Screen 
            name="auth/verification-success" 
            options={{ 
              title: '驗證成功', 
              headerShown: true,
              // 禁止用手勢返回
              gestureEnabled: false,
              // 禁止使用返回按鈕返回
              headerBackVisible: false 
            }} 
          />
        </Stack>
      </ThemeProvider>
    </AuthProvider>
  );
}
