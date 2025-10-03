<template>
  <div class="diagnosis-report">
    <!-- 报告头部 -->
    <div class="report-header">
      <h3>资产配置诊断报告</h3>
      <div class="report-meta">
        <span>生成时间: {{ new Date().toLocaleString("zh-CN") }}</span>
        <el-tag type="primary">美林时钟分析</el-tag>
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
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { Top, Bottom } from "@element-plus/icons-vue";

defineProps({
  report: {
    type: Object,
    required: true,
  },
});

// 分类名称映射
const getCategoryName = (category) => {
  const names = {
    equity: "权益类",
    bond: "债券类",
    commodity: "商品类",
    cash: "现金类",
  };
  return names[category] || category;
};

// 进度条颜色
const getProgressColor = (category) => {
  const colors = {
    equity: "#e6a23c",
    bond: "#67c23a",
    commodity: "#f56c6c",
    cash: "#409eff",
  };
  return colors[category] || "#909399";
};

// 健康度描述
const getHealthDescription = (score) => {
  if (score >= 80) return "您的资产配置较为合理，与当前经济周期匹配度较高";
  if (score >= 60) return "配置基本合理，有少量优化空间";
  return "配置与建议偏差较大，建议及时调整";
};

// 总结标题和类型
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
</script>

<style scoped>
.diagnosis-report {
  padding: 10px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  gap: 5px;
  font-size: 12px;
  color: #909399;
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
</style>
