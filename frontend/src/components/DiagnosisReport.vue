<template>
  <div class="diagnosis-report">
    <!-- 报告头部 -->
    <div class="report-header">
      <h3>资产配置诊断报告</h3>
      <div class="report-meta">
        <span
          >生成时间:
          {{
            formatDate(report.created_at) || new Date().toLocaleString("zh-CN")
          }}</span
        >
        <el-tag type="primary">美林时钟分析</el-tag>
        <!-- 历史报告操作按钮 -->
        <div v-if="showHistoryControls" class="history-controls">
          <el-button size="small" @click="openHistoryReports" :icon="Clock">
            历史报告
          </el-button>
          <el-button size="small" type="primary" @click="$emit('rediagnose')">
            重新诊断
          </el-button>
          <!-- 新增：删除当前报告按钮 -->
          <el-button
            size="small"
            type="danger"
            @click="deleteCurrentReport"
            :loading="deletingCurrent"
            v-if="report.id || report.report_id"
          >
            <el-icon><Delete /></el-icon>
            删除报告
          </el-button>
        </div>
      </div>
    </div>

    <!-- 健康度评分 -->
    <div class="health-section">
      <div class="score-display">
        <div class="score-circle">
          <div class="score-value">{{ report.health_score }}</div>
          <div class="score-label">健康度</div>
        </div>
        <div class="score-description">
          <h4>配置评价</h4>
          <p>{{ getHealthDescription(report.health_score) }}</p>
          <p class="economic-phase">
            当前经济周期:
            <el-tag :type="getPhaseTagType(report.economic_phase)">{{
              getPhaseName(report.economic_phase)
            }}</el-tag>
          </p>
        </div>
      </div>
    </div>

    <!-- 配置对比 -->
    <div class="comparison-section">
      <h4>配置对比分析</h4>
      <div class="allocation-comparison">
        <div
          v-for="(userPercent, category) in report.user_allocation"
          :key="category"
          class="allocation-item"
        >
          <div class="category-info">
            <span class="category-name">{{ getCategoryName(category) }}</span>
            <div class="percent-comparison">
              <span class="user-percent"
                >{{ (userPercent * 100).toFixed(1) }}%</span
              >
              <span class="vs">vs</span>
              <span class="suggested-percent"
                >{{
                  (report.merrill_suggestion[category] * 100).toFixed(1)
                }}%</span
              >
            </div>
          </div>
          <el-progress
            :percentage="userPercent * 100"
            :show-text="false"
            :color="getProgressColor(category)"
          />
        </div>
      </div>
    </div>

    <!-- 调整建议 -->
    <div class="advice-section">
      <h4>优化建议</h4>
      <div class="advice-list">
        <div
          v-for="advice in report.adjustment_advice"
          :key="advice.category"
          class="advice-item"
          :class="advice.action"
        >
          <div class="advice-icon">
            <el-icon v-if="advice.action === 'increase'"><Top /></el-icon>
            <el-icon v-else><Bottom /></el-icon>
          </div>
          <div class="advice-content">
            <div class="advice-title">
              {{ advice.action === "increase" ? "增持" : "减持" }}
              {{ advice.category_name }}
            </div>
            <div class="advice-details">
              <span class="amount">¥{{ advice.amount.toFixed(2) }}</span>
              <span class="reason">{{ advice.reason }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 总结 -->
    <div class="summary-section">
      <el-alert
        :title="getSummaryTitle(report.health_score)"
        :type="getSummaryType(report.health_score)"
        :closable="false"
      >
        <p>总资产: ¥{{ report.total_amount.toFixed(2) }}</p>
        <p v-if="report.report_id">报告ID: {{ report.report_id }}</p>
        <p v-if="report.id">报告ID: {{ report.id }}</p>
      </el-alert>
    </div>

    <!-- 历史报告对话框 -->
    <el-dialog v-model="showHistoryReports" title="历史诊断报告" width="900px">
      <div class="history-reports">
        <el-table :data="historyReports" style="width: 100%">
          <el-table-column prop="title" label="报告标题" width="200">
            <template #default="{ row }">
              <div class="report-title">
                <span>{{ row.title }}</span>
                <el-tag size="small" :type="getScoreTagType(row.health_score)">
                  {{ row.health_score }}分
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="economic_phase" label="经济周期" width="120">
            <template #default="{ row }">
              <el-tag :type="getPhaseTagType(row.economic_phase)">
                {{ getPhaseName(row.economic_phase) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_amount" label="总资产" width="150">
            <template #default="{ row }">
              ¥{{ row.total_amount.toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="生成时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button size="small" @click="loadReportDetail(row.id)">
                查看详情
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="deleteReport(row.id)"
                :loading="deletingReportId === row.id"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="historyReports.length === 0" class="empty-reports">
          <el-empty description="暂无历史诊断报告" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits } from "vue";
import { Top, Bottom, Clock, Delete } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { assetAPI } from "@/services/asset";

const props = defineProps({
  report: {
    type: Object,
    required: true,
  },
  showHistoryControls: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(["rediagnose", "reportLoaded", "reportDeleted"]);

// 响应式数据
const showHistoryReports = ref(false);
const historyReports = ref([]);
const loadingHistory = ref(false);
const deletingCurrent = ref(false);
const deletingReportId = ref(null);

// 删除当前报告
const deleteCurrentReport = async () => {
  const reportId = props.report.id || props.report.report_id;
  if (!reportId) {
    ElMessage.error("无法获取报告ID");
    return;
  }

  try {
    await ElMessageBox.confirm(
      "确定要删除这份诊断报告吗？此操作不可恢复。",
      "删除确认",
      { type: "warning" }
    );

    deletingCurrent.value = true;
    await assetAPI.deleteDiagnosisReport(reportId);

    ElMessage.success("报告删除成功");

    // 发射删除事件，让父组件处理
    emit("reportDeleted", reportId);

    // 重新加载历史报告
    await loadHistoryReports();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("删除报告失败");
    }
  } finally {
    deletingCurrent.value = false;
  }
};

// 删除历史报告
const deleteReport = async (reportId) => {
  try {
    await ElMessageBox.confirm(
      "确定要删除这份诊断报告吗？此操作不可恢复。",
      "删除确认",
      { type: "warning" }
    );

    deletingReportId.value = reportId;
    await assetAPI.deleteDiagnosisReport(reportId);

    ElMessage.success("报告删除成功");

    // 如果删除的是当前正在查看的报告，通知父组件
    const currentReportId = props.report.id || props.report.report_id;
    if (currentReportId === reportId) {
      emit("reportDeleted", reportId);
    }

    // 重新加载历史报告列表
    await loadHistoryReports();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("删除报告失败");
    }
  } finally {
    deletingReportId.value = null;
  }
};

// 加载历史报告
const loadHistoryReports = async () => {
  loadingHistory.value = true;
  try {
    console.log("开始加载历史报告...");
    const response = await assetAPI.getDiagnosisReports();
    console.log("历史报告响应:", response);
    historyReports.value = response.data.reports || [];
  } catch (error) {
    console.error("加载历史报告失败:", error);
    ElMessage.error("加载历史报告失败");
  } finally {
    loadingHistory.value = false;
  }
};

// 加载报告详情
const loadReportDetail = async (reportId) => {
  try {
    const response = await assetAPI.getDiagnosisReport(reportId);
    // 发射事件让父组件更新当前报告
    emit("reportLoaded", response.data);
    showHistoryReports.value = false;
  } catch (error) {
    console.error("加载报告详情失败:", error);
    ElMessage.error("加载报告详情失败");
  }
};

// 工具函数
const getCategoryName = (category) => {
  const names = {
    equity: "权益类",
    bond: "债券类",
    commodity: "商品类",
    cash: "现金类",
  };
  return names[category] || category;
};

const getProgressColor = (category) => {
  const colors = {
    equity: "#e6a23c",
    bond: "#67c23a",
    commodity: "#f56c6c",
    cash: "#409eff",
  };
  return colors[category] || "#909399";
};

const getHealthDescription = (score) => {
  if (score >= 80) return "您的资产配置较为合理，与当前经济周期匹配度较高";
  if (score >= 60) return "配置基本合理，有少量优化空间";
  return "配置与建议偏差较大，建议及时调整";
};

const getSummaryTitle = (score) => {
  if (score >= 80) return "配置良好";
  if (score >= 60) return "配置一般";
  return "需要优化";
};

const getSummaryType = (score) => {
  if (score >= 80) return "success";
  if (score >= 60) return "warning";
  return "error";
};

const getScoreTagType = (score) => {
  if (score >= 80) return "success";
  if (score >= 60) return "warning";
  return "danger";
};

const getPhaseTagType = (phase) => {
  const types = {
    recovery: "success",
    overheat: "warning",
    stagflation: "danger",
    recession: "info",
  };
  return types[phase] || "info";
};

const getPhaseName = (phase) => {
  const names = {
    recovery: "复苏期",
    overheat: "过热期",
    stagflation: "滞胀期",
    recession: "衰退期",
  };
  return names[phase] || phase;
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  return new Date(dateString).toLocaleString("zh-CN");
};

// 打开历史报告时加载数据
const openHistoryReports = () => {
  showHistoryReports.value = true;
  loadHistoryReports();
};

// 组件挂载时，如果是历史报告模式，加载历史数据
onMounted(() => {
  if (props.showHistoryControls) {
    loadHistoryReports();
  }
});

// 暴露方法给父组件
defineExpose({
  loadHistoryReports,
  openHistoryReports,
});
</script>

<style scoped>
.diagnosis-report {
  padding: 10px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.report-header h3 {
  margin: 0;
  color: #303133;
}

.report-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  font-size: 12px;
  color: #909399;
}

.history-controls {
  display: flex;
  gap: 8px;
  margin-top: 5px;
}

.health-section {
  margin-bottom: 25px;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 20px;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff, #67c23a);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  font-weight: bold;
}

.score-value {
  font-size: 24px;
  line-height: 1;
}

.score-label {
  font-size: 12px;
  opacity: 0.9;
}

.score-description h4 {
  margin: 0 0 5px 0;
  color: #303133;
}

.score-description p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.economic-phase {
  margin-top: 8px !important;
  font-size: 13px !important;
}

.comparison-section {
  margin-bottom: 25px;
}

.comparison-section h4 {
  margin-bottom: 15px;
  color: #303133;
}

.allocation-comparison {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.allocation-item {
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
}

.category-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.category-name {
  font-weight: 500;
  color: #303133;
}

.percent-comparison {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.user-percent {
  color: #409eff;
  font-weight: bold;
}

.vs {
  color: #909399;
}

.suggested-percent {
  color: #67c23a;
}

.advice-section {
  margin-bottom: 20px;
}

.advice-section h4 {
  margin-bottom: 15px;
  color: #303133;
}

.advice-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.advice-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
}

.advice-item.increase {
  border-left: 4px solid #67c23a;
  background: #f0f9f4;
}

.advice-item.decrease {
  border-left: 4px solid #f56c6c;
  background: #fef0f0;
}

.advice-icon {
  font-size: 18px;
}

.advice-item.increase .advice-icon {
  color: #67c23a;
}

.advice-item.decrease .advice-icon {
  color: #f56c6c;
}

.advice-content {
  flex: 1;
}

.advice-title {
  font-weight: 500;
  margin-bottom: 4px;
}

.advice-details {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #606266;
}

.amount {
  font-weight: bold;
}

.summary-section {
  margin-top: 20px;
}

.history-reports {
  max-height: 60vh;
  overflow-y: auto;
}

.empty-reports {
  padding: 40px 0;
}

.report-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 确保按钮在小屏幕上也能正常显示 */
@media (max-width: 768px) {
  .history-controls {
    flex-direction: column;
    align-items: flex-end;
  }
}
</style>
