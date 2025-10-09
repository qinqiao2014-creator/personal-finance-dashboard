import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/services/api";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);
  const token = ref(localStorage.getItem("token"));
  const isAuthenticated = ref(!!localStorage.getItem("token"));

  // 🔄 新增：统一的认证设置方法
  const setAuth = (userData, authToken) => {
    user.value = userData;
    token.value = authToken;
    isAuthenticated.value = true;
    localStorage.setItem("token", authToken);
    console.log("user.value数据：", user.value);
    console.log("token.value数据:", token.value);
    console.log("user数据:", user);

    // ⚡ 重要更新：设置axios默认授权头
    api.defaults.headers.common["Authorization"] = `Bearer ${authToken}`;
  };

  // 🔄 新增：统一的认证清除方法
  const clearAuth = () => {
    user.value = null;
    token.value = null;
    isAuthenticated.value = false;
    localStorage.removeItem("token");
    delete api.defaults.headers.common["Authorization"];
  };

  // 🔄 判断登录类型（用户名或邮箱）
  const determineLoginType = (identifier) => {
    // 简单的邮箱验证正则
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(identifier) ? "email" : "username";
  };

  // 🔄 新增：双通道登录方法
  const loginDual = async (identifier, password) => {
    try {
      const loginType = determineLoginType(identifier);
      const requestData = {
        password: password,
      };

      // 根据类型设置对应的字段
      if (loginType === "email") {
        requestData.email = identifier;
      } else {
        requestData.username = identifier;
      }

      console.log(`🔐 ${loginType}登录请求:`, requestData);

      const response = await api.post("/auth/login", requestData);

      const { access_token, user: userData } = response.data;
      setAuth(userData, access_token); // 使用统一的设置方法

      return response.data;
    } catch (error) {
      clearAuth(); // 登录失败时清除认证状态
      throw error; // 重新抛出错误供页面处理
    }
  };

  // 🔄 保留原有登录方法（向后兼容）
  const login = async (username, password) => {
    return loginDual(username, password);
  };

  // 🔄 更新：使用新的clearAuth方法
  const logout = () => {
    clearAuth(); // 使用统一的清除方法
  };

  // 🔄 新增：检查认证状态的方法（用于路由守卫）
  const checkAuth = async () => {
    if (!token.value) {
      clearAuth();
      return false;
    }

    try {
      // 可以添加一个验证token的接口调用
      // 或者直接使用现有的用户信息接口
      const response = await api.get("/users/me");
      user.value = response.data;

      // TODO: 后端接口返回的用户数据结构不一致
      // 登录接口: { user_id, username, email, role }
      // 用户信息接口: { id, username, email, role, created_at, is_active }
      // 当前临时使用，等前端需求明确后再统一

      return true;
    } catch (error) {
      clearAuth();
      return false;
    }
  };

  return {
    user,
    token,
    isAuthenticated,
    login, // 原有登录方法（向后兼容）
    loginDual, // 🔄 新增：双通道登录方法
    logout,
    checkAuth, // 🔄 新增：供路由守卫使用
    setAuth, // 🔄 新增：统一设置方法
    clearAuth, // 🔄 新增：统一清除方法
  };
});
