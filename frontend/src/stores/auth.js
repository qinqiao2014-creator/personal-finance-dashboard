import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { authAPI } from "@/services/api"; 

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);
  const token = ref(localStorage.getItem("token"));
  const isAuthenticated = computed(() => !!token.value);

  // 工具方法（内部使用）
  function setToken(newToken) {
    token.value = newToken;
    localStorage.setItem("token", newToken);
  }

  function setUser(userData) {
    user.value = userData;
  }

  // 业务方法
  async function login(credentials) {
    const response = await authAPI.login(credentials);
    setToken(response.data.access_token);
    setUser(response.data.user);
  }

  function logout() {
    token.value = null;
    user.value = null;
    localStorage.removeItem("token");
  }

  return {
    user,
    token,
    isAuthenticated,
    setToken,
    setUser,
    login,
    logout    
  };
});

