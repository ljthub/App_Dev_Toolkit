// API 連接設定
export const API_URL = "https://api.ljthub.com/api/v1";

// 認證相關設定
export const AUTH_TOKEN_KEY = "auth_token";
export const AUTH_USER_KEY = "auth_user";

// 路由設定
export const API_ROUTES = {
  REGISTER: "/auth/register",
  LOGIN: "/auth/login",
  VERIFY_EMAIL: "/auth/verify-email",
  RESEND_VERIFICATION: "/auth/resend-verification",
  RESEND_VERIFICATION_PUBLIC: "/auth/public/resend-verification",
  ME: "/auth/me"
}; 