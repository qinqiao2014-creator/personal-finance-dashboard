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

      <!-- 新增：分类数量统计 -->
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">🏷️</div>
          <div class="stat-info">
            <div class="stat-value">{{ categoryCount }}</div>
            <div class="stat-label">分类数量</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 分类统计图表 -->
    <el-card class="chart-card">
      <template #header>
        <span>资产分类分布</span>
      </template>
      <div v-if="categoryStats.length > 0" class="chart-container">
        <div
          v-for="category in categoryStats"
          :key="category.id"
          class="category-item"
        >
          <div class="category-info">
            <span class="category-name">{{ category.name }}</span>
            <span class="category-amount"
              >¥ {{ category.total_amount?.toFixed(2) || "0.00" }}</span
            >
          </div>
          <el-progress
            :percentage="getCategoryPercentage(category.total_amount)"
            :show-text="false"
          />
        </div>
      </div>
      <el-empty v-else description="暂无分类统计数据" />
    </el-card>

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
import { assetAPI } from "@/services/asset";
import { ElMessage } from "element-plus";

const authStore = useAuthStore();

// 数据
const totalAssets = ref(0);
const assetsCount = ref(0);
const categoryCount = ref(0);
const categoryStats = ref([]);
const loading = ref(false);

// 当前日期
const currentDate = computed(() => new Date().toLocaleDateString("zh-CN"));

// 计算分类百分比
const getCategoryPercentage = (categoryAmount) => {
  if (totalAssets.value === 0) return 0;
  return (categoryAmount / totalAssets.value) * 100;
};

// 获取资产数据
const fetchAssets = async () => {
  loading.value = true;
  try {
    // 获取资产统计
    const summaryResponse = await assetAPI.getAssetSummary();
    console.log("资产统计响应:", summaryResponse.data);

    const summaryData = summaryResponse.data;

    // 使用后端返回的统计数据
    totalAssets.value = summaryData.total_assets || 0;
    assetsCount.value = summaryData.asset_count || 0;

    // 处理分类统计
    if (summaryData.assets_by_type) {
      categoryStats.value = Object.entries(summaryData.assets_by_type).map(
        ([key, value]) => {
          console.log("分类统计项:", key, value);
          // 解析格式: "equity.stock (股票)" -> code: "equity.stock", name: "股票"
          const match = key.match(/(.+) \((.+)\)/);
          if (match) {
            return {
              id: match[1], // 使用分类代码作为ID
              name: match[2], // 分类名称
              code: match[1], // 分类代码
              total_amount: value,
            };
          } else {
            // 如果没有括号格式，直接使用
            return {
              id: key,
              name: key,
              code: key,
              total_amount: value,
            };
          }
        }
      );
      categoryCount.value = categoryStats.value.length;
    } else {
      categoryStats.value = [];
      categoryCount.value = 0;
    }
  } catch (error) {
    console.error("获取资产统计失败:", error);
    ElMessage.error("获取资产数据失败");
    // 设置默认值
    totalAssets.value = 0;
    assetsCount.value = 0;
    categoryStats.value = [];
    categoryCount.value = 0;
  } finally {
    loading.value = false;
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

.chart-card {
  margin-bottom: 20px;
}

.chart-container {
  padding: 10px;
}

.category-item {
  margin-bottom: 15px;
}

.category-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.category-name {
  font-weight: 500;
}

.category-amount {
  color: #409eff;
  font-weight: bold;
}

.quick-actions {
  margin-top: 20px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}
</style>
