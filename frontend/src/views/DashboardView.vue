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

    <!-- 快速操作 - 移到图表区域上方 -->
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

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 资产分布环形图 -->
      <el-card class="chart-card">
        <template #header>
          <div class="chart-header">
            <span>资产分类分布</span>
            <el-button
              type="primary"
              link
              @click="refreshChartData"
              :loading="chartLoading"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </template>
        <AssetDistributionChart ref="distributionChart" />
      </el-card>

      <!-- 趋势分析折线图 -->
      <el-card class="chart-card">
        <template #header>
          <span>资产趋势分析</span>
        </template>
        <AssetTrendChart />
      </el-card>
    </div>

    <!-- 美林投资时钟 -->
    <el-card class="chart-card full-width">
      <template #header>
        <span>美林投资时钟</span>
        <el-tooltip
          content="基于经济周期理论的资产配置参考工具"
          placement="top"
        >
          <el-icon><InfoFilled /></el-icon>
        </el-tooltip>
      </template>
      <MerrillClock />
    </el-card>

    <!-- 原有的分类统计进度条 -->
    <el-card class="chart-card">
      <template #header>
        <span>分类金额详情</span>
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

    <!-- 实时数据刷新控制 -->
    <div class="refresh-controls">
      <el-checkbox v-model="autoRefresh" @change="toggleAutoRefresh">
        自动刷新 (每30秒)
      </el-checkbox>
      <el-button @click="manualRefresh" :loading="refreshing" type="primary">
        {{ refreshing ? "刷新中..." : "立即刷新" }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";
import { useAuthStore } from "@/stores/auth";
import { assetAPI } from "@/services/asset";
import { ElMessage } from "element-plus";
import { Refresh, InfoFilled } from "@element-plus/icons-vue";

// 导入图表组件
import AssetDistributionChart from "@/components/AssetDistributionChart.vue";
import AssetTrendChart from "@/components/AssetTrendChart.vue";
import MerrillClock from "@/components/MerrillClock.vue";

const authStore = useAuthStore();

// 数据
const totalAssets = ref(0);
const assetsCount = ref(0);
const categoryCount = ref(0);
const categoryStats = ref([]);
const loading = ref(false);
const chartLoading = ref(false);
const refreshing = ref(false);
const autoRefresh = ref(false);

// 图表引用
const distributionChart = ref(null);

// 当前日期
const currentDate = computed(() => new Date().toLocaleDateString("zh-CN"));

// 自动刷新定时器
let refreshInterval = null;

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
    refreshing.value = false;
  }
};

// 刷新图表数据
const refreshChartData = async () => {
  chartLoading.value = true;
  try {
    await fetchAssets();
    // 如果图表组件有刷新方法，可以调用
    if (distributionChart.value && distributionChart.value.refreshData) {
      await distributionChart.value.refreshData();
    }
    ElMessage.success("数据刷新成功");
  } catch (error) {
    ElMessage.error("刷新数据失败");
  } finally {
    chartLoading.value = false;
  }
};

// 手动刷新
const manualRefresh = () => {
  refreshing.value = true;
  refreshChartData();
};

// 自动刷新控制
const toggleAutoRefresh = () => {
  if (autoRefresh.value) {
    refreshInterval = setInterval(() => {
      refreshChartData();
    }, 30000); // 30秒刷新
  } else {
    if (refreshInterval) {
      clearInterval(refreshInterval);
      refreshInterval = null;
    }
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

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
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

/* 快速操作样式 */
.quick-actions {
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

/* 图表网格布局 */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.chart-card.full-width {
  grid-column: 1 / -1;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.refresh-controls {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .refresh-controls {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
