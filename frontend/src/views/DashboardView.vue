<template>
  <div class="dashboard-container">
    <h2>个人资产管理系统</h2>

    <!-- 用户欢迎信息 -->
    <el-card class="welcome-card">
      <div class="welcome-content">
        <h3>欢迎回来，{{ authStore.user?.username }}！</h3>
        <p>今天是 {{ currentDate }}</p>
      </div>
    </el-card>

    <!-- 资产统计 -->
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">💰</div>
          <div class="stat-info">
            <div class="stat-value">¥ {{ totalAssets.toFixed(2) }}</div>
            <div class="stat-label">总资产</div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">📈</div>
          <div class="stat-info">
            <div class="stat-value">{{ assetsCount }}</div>
            <div class="stat-label">资产数量</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 快速操作 -->
    <el-card class="quick-actions">
      <template #header>
        <span>快速操作</span>
      </template>
      <div class="action-buttons">
        <el-button type="primary" @click="$router.push('/assets')">
          管理资产
        </el-button>
        <el-button @click="logout">退出登录</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import api from "@/services/api";

const authStore = useAuthStore();

// 数据
const totalAssets = ref(0);
const assetsCount = ref(0);
const assetsList = ref([]);

// 当前日期
const currentDate = computed(() => new Date().toLocaleDateString("zh-CN"));

// 获取资产数据 - 修复后的版本
const fetchAssets = async () => {
  try {
    const response = await api.get("/assets");
    console.log("API响应数据:", response.data); // 调试用

    // 正确的数据提取方式
    assetsList.value = response.data.items || [];

    // 计算统计信息
    totalAssets.value = assetsList.value.reduce((sum, asset) => {
      return sum + (asset.amount || 0); // 注意：后端字段是amount，不是value
    }, 0);

    assetsCount.value = assetsList.value.length;
  } catch (error) {
    console.error("获取资产失败:", error);
    // 设置默认值
    assetsList.value = [];
    totalAssets.value = 0;
    assetsCount.value = 0;
  }
};

// 退出登录
const logout = () => {
  authStore.logout();
  window.location.replace("/login");
};

onMounted(() => {
  fetchAssets();
});
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-content h3 {
  margin: 0;
  color: #303133;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.stat-icon {
  font-size: 2.5em;
}

.stat-value {
  font-size: 1.8em;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  color: #909399;
  font-size: 0.9em;
}

.quick-actions {
  margin-top: 20px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}
</style>
