import { StyleSheet, View, Text, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function ApiInfoScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>API 功能列表</Text>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>👤 使用者系統</Text>
          
          <View style={styles.apiItem}>
            <Text style={styles.apiTitle}>註冊 API</Text>
            <Text style={styles.apiPath}>POST /auth/register</Text>
            <Text style={styles.apiDescription}>
              允許用戶創建新帳戶。需要提供 email、username 和 password。
            </Text>
          </View>
          
          <View style={styles.apiItem}>
            <Text style={styles.apiTitle}>登入 API</Text>
            <Text style={styles.apiPath}>POST /auth/login</Text>
            <Text style={styles.apiDescription}>
              使用 username 和 password 換取訪問令牌。
            </Text>
          </View>
          
          <View style={styles.apiItem}>
            <Text style={styles.apiTitle}>驗證郵件 API</Text>
            <Text style={styles.apiPath}>POST /auth/verify-email</Text>
            <Text style={styles.apiDescription}>
              驗證用戶的電子郵件地址，需要從郵件中獲得的令牌。
            </Text>
          </View>
          
          <View style={styles.apiItem}>
            <Text style={styles.apiTitle}>重新發送驗證郵件 API</Text>
            <Text style={styles.apiPath}>POST /auth/resend-verification</Text>
            <Text style={styles.apiDescription}>
              重新發送電子郵件驗證郵件。需要登入狀態。
            </Text>
          </View>
          
          <View style={styles.apiItem}>
            <Text style={styles.apiTitle}>獲取用戶資料 API</Text>
            <Text style={styles.apiPath}>GET /auth/me</Text>
            <Text style={styles.apiDescription}>
              獲取當前登入用戶的詳細資料。需要登入狀態。
            </Text>
          </View>
        </View>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📬 通知系統</Text>
          
          <View style={styles.apiItem}>
            <Text style={styles.apiTitle}>發送郵件 API</Text>
            <Text style={styles.apiPath}>POST /email/send</Text>
            <Text style={styles.apiDescription}>
              發送自定義電子郵件。需要系統管理權限。
            </Text>
          </View>
        </View>
        
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>💡 使用提示</Text>
          
          <View style={styles.tipItem}>
            <Text style={styles.tipTitle}>認證方式</Text>
            <Text style={styles.tipDescription}>
              系統使用 JWT (JSON Web Token) 進行身份驗證。登入後，請在後續請求的 
              Authorization 標頭中包含 Bearer 令牌。
            </Text>
          </View>
          
          <View style={styles.tipItem}>
            <Text style={styles.tipTitle}>電子郵件驗證</Text>
            <Text style={styles.tipDescription}>
              註冊後，系統會自動發送一封驗證郵件。點擊郵件中的連結，或使用郵件中的驗證令牌調用 
              verify-email API 以完成驗證過程。
            </Text>
          </View>
          
          <View style={styles.tipItem}>
            <Text style={styles.tipTitle}>API 基礎 URL</Text>
            <Text style={styles.tipDescription}>
              所有 API 端點都以 http://localhost:8000 為基礎 URL。
              在生產環境中，這將是您的實際 API 服務器地址。
            </Text>
          </View>
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
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 20,
    color: '#333',
    textAlign: 'center',
  },
  section: {
    marginBottom: 25,
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
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
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  apiItem: {
    marginBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingBottom: 15,
  },
  apiTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4e5ae8',
  },
  apiPath: {
    fontFamily: 'monospace',
    backgroundColor: '#f5f5f5',
    padding: 5,
    borderRadius: 5,
    marginVertical: 5,
    fontSize: 14,
    color: '#666',
  },
  apiDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  tipItem: {
    marginBottom: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingBottom: 15,
  },
  tipTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#e88e4e',
  },
  tipDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginTop: 5,
  },
});
