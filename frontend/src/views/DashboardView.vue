<template>
  <div class="dashboard-container">
    <h2>个人（家庭）资产管理系统</h2>

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
    <!-- 美林投资时钟部分简化 -->
    <el-card class="chart-card full-width">
      <template #header>
        <div class="clock-header-with-diagnosis">
          <span>美林投资时钟</span>
          <div class="diagnosis-controls">
            <el-button
              v-if="!diagnosisResult"
              type="primary"
              @click="startDiagnosis"
              :loading="diagnosing"
              size="small"
            >
              <el-icon><Search /></el-icon>
              诊断资产配置
            </el-button>

            <div v-else class="diagnosis-brief">
              <span class="health-badge"
                >健康度: {{ diagnosisResult.health_score }}/100</span
              >
              <el-button @click="showDiagnosisDetail" size="small"
                >查看详情</el-button
              >
            </div>
          </div>
        </div>
      </template>
      <MerrillClock ref="merrillClockRef" />
    </el-card>

    <!-- 诊断结果对话框 -->
    <el-dialog
      v-model="showDiagnosisDialog"
      class="diagnosis-dialog"
      :title="diagnosisResult ? '资产配置诊断报告' : '资产配置诊断中...'"
      width="900px"
    >
      <DiagnosisProcess
        v-if="!diagnosisResult"
        :current-step="currentStep"
        :step-progress="stepProgress"
      />
      <!-- 修复：添加 showHistoryControls 属性和事件处理 -->
      <DiagnosisReport
        v-else
        :report="diagnosisResult"
        :show-history-controls="true"
        @rediagnose="startDiagnosis"
        @report-loaded="handleReportLoaded"
        @report-deleted="handleReportDeleted"
      />
    </el-dialog>

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
import { Refresh, InfoFilled, Search } from "@element-plus/icons-vue"; // 添加Search图标
import DiagnosisReport from "@/components/DiagnosisReport.vue"; // 新增导入
import DiagnosisProcess from "@/components/DiagnosisProcess.vue";

// 导入图表组件
import AssetDistributionChart from "@/components/AssetDistributionChart.vue";
import AssetTrendChart from "@/components/AssetTrendChart.vue";
import MerrillClock from "@/components/MerrillClock.vue";

const authStore = useAuthStore();
// 美林时钟组件
const merrillClockRef = ref(null);
// 数据
const totalAssets = ref(0);
const assetsCount = ref(0);
const categoryCount = ref(0);
const categoryStats = ref([]);
const loading = ref(false);
const chartLoading = ref(false);
const refreshing = ref(false);
const autoRefresh = ref(false);
// 现有响应式数据保持不变，新增：
const diagnosisResult = ref(null);
const diagnosing = ref(false);
const showDiagnosisDialog = ref(false);
// 新增：动画相关变量
const currentStep = ref(1);
const stepProgress = ref(0);

// 图表引用
const distributionChart = ref(null);

// 当前日期
const currentDate = computed(() => new Date().toLocaleDateString("zh-CN"));

// 自动刷新定时器
let refreshInterval = null;

// 新增：加载最新诊断报告
const loadLatestDiagnosisReport = async () => {
  try {
    console.log("正在加载最新诊断报告...");
    const response = await assetAPI.getDiagnosisReports();
    const reports = response.data.reports || [];

    if (reports.length > 0) {
      // 获取最新的报告
      const latestReport = reports[0];
      console.log("找到最新诊断报告:", latestReport);

      // 设置诊断结果，这样首页就会显示"查看详情"
      diagnosisResult.value = {
        ...latestReport,
        report_id: latestReport.id, // 确保有 report_id
      };
    } else {
      console.log("没有找到历史诊断报告");
      diagnosisResult.value = null;
    }
  } catch (error) {
    console.error("加载最新诊断报告失败:", error);
    // 不显示错误消息，因为可能是没有报告
  }
};

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

// 开始诊断流程
const startDiagnosis = async () => {
  diagnosing.value = true;
  showDiagnosisDialog.value = true;
  diagnosisResult.value = null;

  try {
    // 运行动画步骤
    currentStep.value = 1;
    stepProgress.value = 0;
    await runDiagnosisStep(2000);

    currentStep.value = 2;
    stepProgress.value = 0;
    await runDiagnosisStep(1500);

    currentStep.value = 3;
    stepProgress.value = 0;
    await runDiagnosisStep(1000);

    // 获取真实数据
    // 直接从 MerrillClock 即ref="merrillClockRef" 组件获取当前周期
    const currentPhase = merrillClockRef.value.getCurrentPhase();
    const response = await assetAPI.getAllocationAnalysis(currentPhase);
    diagnosisResult.value = response.data;

    ElMessage.success("资产配置诊断完成");
  } catch (error) {
    console.error("诊断失败:", error);
    ElMessage.error("诊断失败，请重试");
  } finally {
    diagnosing.value = false;
  }
};

// 查看诊断详情
const showDiagnosisDetail = () => {
  showDiagnosisDialog.value = true;
};

// 处理报告加载事件
const handleReportLoaded = (report) => {
  diagnosisResult.value = report;
};

// 新增：运行动画步骤的方法
const runDiagnosisStep = (duration) => {
  return new Promise((resolve) => {
    const interval = 50;
    const steps = duration / interval;
    let currentStepProgress = 0;

    const progressInterval = setInterval(() => {
      currentStepProgress++;
      stepProgress.value = Math.min((currentStepProgress / steps) * 100, 100);

      if (currentStepProgress >= steps) {
        clearInterval(progressInterval);
        resolve();
      }
    }, interval);
  });
};

// 处理报告删除事件
const handleReportDeleted = (reportId) => {
  console.log("报告被删除:", reportId);

  // 如果删除的是当前显示的报告，清空诊断结果
  if (
    diagnosisResult.value &&
    (diagnosisResult.value.id === reportId ||
      diagnosisResult.value.report_id === reportId)
  ) {
    diagnosisResult.value = null;
    showDiagnosisDialog.value = false;
  }

  ElMessage.success("报告删除成功");
};

// 退出登录
const logout = () => {
  authStore.logout();
  window.location.replace("/login");
};

onMounted(() => {
  fetchAssets();
  // 新增：页面加载时检查是否有历史诊断记录
  loadLatestDiagnosisReport();
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

/* 新增样式 */
.clock-header-with-diagnosis {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.diagnosis-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.diagnosis-brief {
  display: flex;
  align-items: center;
  gap: 10px;
}

.health-badge {
  padding: 4px 8px;
  background: #f0f9ff;
  border: 1px solid #409eff;
  border-radius: 4px;
  color: #409eff;
  font-size: 12px;
  font-weight: 500;
}

/* 诊断对话框样式 */
:deep(.diagnosis-dialog .el-dialog__body) {
  max-height: 70vh;
  overflow-y: auto;
  padding: 15px 20px;
}
</style>
