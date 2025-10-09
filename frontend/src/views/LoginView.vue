<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <div class="login-header">
          <h2>个人资产管理系统</h2>
          <p>请登录您的账户</p>
        </div>
      </template>

      <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" @submit.prevent="handleLogin">
        <el-form-item prop="identifier">
          <el-input v-model="loginForm.identifier" placeholder="请输入用户名或邮箱" size="large" :prefix-icon="User" :disabled="loading" />
        </el-form-item>

        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" size="large" :prefix-icon="Lock" :disabled="loading" show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="handleLogin" class="login-button">
            {{ loading ? "登录中..." : "登录" }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <p>还没有账户？ <router-link to="/register">立即注册</router-link></p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { User, Lock } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const router = useRouter();
const loading = ref(false);
const loginFormRef = ref();

const loginForm = reactive({
  identifier: "",  // 改为统一的标识符字段
  password: "",
});

// 表单验证规则
const loginRules = {
  identifier: [
    { required: true, message: "请输入用户名或邮箱", trigger: "blur" },
    {
      min: 3,
      max: 50,
      message: "用户名或邮箱长度在 3 到 50 个字符",
      trigger: "blur",
    },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码长度至少 6 个字符", trigger: "blur" },
  ],
};

// 判断是用户名还是邮箱
const determineLoginType = (identifier) => {
  // 简单的邮箱验证正则
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(identifier) ? 'email' : 'username';
};

const handleLogin = async () => {
  // 表单验证
  if (!loginFormRef.value) return;

  const valid = await loginFormRef.value.validate().catch(() => false);
  if (!valid) return;

  loading.value = true;

  try {
    // 使用新的登录方法，支持双通道
    await authStore.loginDual(loginForm.identifier, loginForm.password);

    ElMessage.success("登录成功！");
    router.push("/dashboard");
  } catch (error) {
    const errorMessage = error.response?.data?.detail || "登录失败，请检查用户名/邮箱和密码";
    ElMessage.error(errorMessage);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
}

.login-header {
  text-align: center;
}

.login-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-weight: 600;
}

.login-header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.login-button {
  width: 100%;
  margin-top: 10px;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.login-footer a {
  color: #409eff;
  text-decoration: none;
}

.login-footer a:hover {
  text-decoration: underline;
}
</style>