<template>
  <input v-model="username" placeholder="用户名">
  <input v-model="password" type="password" placeholder="密码">
  <button @click="handleLogin">登录</button>
  <button @click="handleRegister">注册</button>
</template>


<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

// 组件逻辑
const authStore = useAuthStore();
const username = ref('');
const password = ref('');

const handleLogin = async () => {
  await authStore.login({
    username: username.value,
    password: password.value
  });
};
</script>

<style scoped>
.login-container {
  padding: 20px;
}
</style>