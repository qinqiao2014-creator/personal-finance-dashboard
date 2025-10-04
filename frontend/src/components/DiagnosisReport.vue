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
        <!-- 资产分类说明按钮 -->
        <el-button
          type="text"
          @click="showMappingGuide = true"
          :icon="InfoFilled"
          size="small"
        >
          我的资产如何分类？
        </el-button>
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
      <h4>
        配置对比分析
        <el-tooltip effect="dark" placement="top">
          <template #content>
            <div class="mapping-tip">
              <p><strong>资产分类说明：</strong></p>
              <ul>
                <li><strong>权益类</strong>: 股票、股票基金等</li>
                <li><strong>债券类</strong>: 银行理财、债券、保险等</li>
                <li><strong>商品类</strong>: 房地产、黄金、加密货币等</li>
                <li><strong>现金类</strong>: 存款、货币基金等</li>
              </ul>
            </div>
          </template>
          <el-icon class="tip-icon"><QuestionFilled /></el-icon>
        </el-tooltip>
      </h4>
      <div class="allocation-comparison">
        <div
          v-for="(userPercent, category) in report.user_allocation"
          :key="category"
          class="allocation-item"
        >
          <div class="category-info">
            <span class="category-name">
              {{ getCategoryName(category) }}
              <!-- 每个分类单独的工具提示 -->
              <el-tooltip effect="dark" placement="top">
                <template #content>
                  <div class="category-tip">
                    <p>
                      <strong>{{ getCategoryName(category) }}资产包含：</strong>
                    </p>
                    <p>{{ getCategoryDescription(category) }}</p>
                  </div>
                </template>
                <el-icon class="info-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </span>
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
        <!-- 不显示ID -->
        <!--
        <p v-if="report.report_id">报告ID: {{ report.report_id }}</p>
        <p v-if="report.id">报告ID: {{ report.id }}</p>
        -->
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

    <!-- 资产分类说明对话框 -->
    <el-dialog v-model="showMappingGuide" title="了解资产分类" width="700px">
      <div class="mapping-guide">
        <div class="guide-section">
          <h4>美林时钟四大资产类别</h4>
          <div class="category-cards">
            <div
              v-for="category in merrillCategories"
              :key="category.key"
              class="category-card"
            >
              <div class="card-header">
                <div
                  class="color-indicator"
                  :style="{ backgroundColor: category.color }"
                ></div>
                <strong>{{ category.name }}</strong>
                <el-tag :type="category.tagType" size="small">{{
                  category.risk
                }}</el-tag>
              </div>
              <div class="card-content">
                <p class="category-desc">{{ category.description }}</p>
                <div class="typical-assets">
                  <span class="asset-label">典型资产：</span>
                  <div class="asset-tags">
                    <el-tag
                      v-for="asset in category.typicalAssets"
                      :key="asset"
                      size="small"
                      effect="plain"
                    >
                      {{ asset }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="guide-section">
          <h4>常见问题解答</h4>
          <el-collapse>
            <el-collapse-item title="为什么银行理财被归为债券类？">
              <p>
                银行理财产品主要投资于债券、货币市场工具等固定收益类资产，其风险收益特征与债券基金类似，因此系统将其归入债券类别。
              </p>
            </el-collapse-item>
            <el-collapse-item title="货币基金和银行理财有什么区别？">
              <p>
                货币基金主要投资短期货币市场工具，流动性更高、风险更低，归为现金类；银行理财投资范围更广，期限更长，风险收益略高，归为债券类。
              </p>
            </el-collapse-item>
            <el-collapse-item title="为什么房地产属于商品类？">
              <p>
                房地产是实物资产，具有稀缺性、抗通胀特性，其价格受供需关系影响，这些特征与大宗商品类似，因此在美林时钟中归为商品类。
              </p>
            </el-collapse-item>
            <el-collapse-item title="为什么比特币属于商品类？">
              <p>
                比特币等加密货币在美林时钟中被归为商品类，主要基于以下原因：
              </p>
              <ul>
                <li>
                  <strong>数字商品属性</strong
                  >：比特币具有稀缺性（总量2100万枚）、可交易性等商品特征
                </li>
                <li>
                  <strong>通胀对冲功能</strong
                  >：类似黄金，在某些经济环境下具有抗通胀特性
                </li>
                <li>
                  <strong>独立于传统金融</strong
                  >：与股票、债券等传统资产相关性较低
                </li>
                <li>
                  <strong>动态权重调整</strong
                  >：系统会根据不同经济周期动态调整其在商品类中的权重比例
                </li>
              </ul>
            </el-collapse-item>

            <el-collapse-item title="为什么黄金属于商品类？">
              <p>黄金作为传统避险资产，在美林时钟中明确归为商品类：</p>
              <ul>
                <li>
                  <strong>实物商品本质</strong
                  >：黄金是典型的实物商品，具有稀缺性和工业用途
                </li>
                <li>
                  <strong>通胀时期表现突出</strong
                  >：在高通胀环境下，黄金往往有较好表现
                </li>
                <li>
                  <strong>避险属性</strong
                  >：在地缘政治危机或经济不确定性时发挥避险作用
                </li>
                <li>
                  <strong>货币属性</strong
                  >：历史上作为货币储备，具有价值存储功能
                </li>
              </ul>
              <p>在滞胀期和过热期，黄金在商品类资产中的配置权重会显著提高。</p>
            </el-collapse-item>
          </el-collapse>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, defineProps, defineEmits, watch } from "vue";
import {
  Top,
  Bottom,
  Clock,
  Delete,
  InfoFilled,
  QuestionFilled,
} from "@element-plus/icons-vue";
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

// 资产分类说明相关
const showMappingGuide = ref(false);

// 美林时钟分类数据
const merrillCategories = [
  {
    key: "equity",
    name: "权益类",
    color: "#e6a23c",
    tagType: "warning",
    risk: "中高风险",
    description: "代表企业所有权，收益与经济增长正相关",
    typicalAssets: ["股票", "股票型基金", "偏股混合基金"],
  },
  {
    key: "bond",
    name: "债券类",
    color: "#67c23a",
    tagType: "success",
    risk: "中低风险",
    description: "固定收益资产，在经济衰退期表现较好",
    typicalAssets: ["银行理财", "债券", "保险产品"],
  },
  {
    key: "commodity",
    name: "商品类",
    color: "#f56c6c",
    tagType: "danger",
    risk: "高风险",
    description: "实物商品和资源，通胀时期表现突出",
    typicalAssets: ["房地产", "黄金", "加密货币"],
  },
  {
    key: "cash",
    name: "现金类",
    color: "#409eff",
    tagType: "primary",
    risk: "低风险",
    description: "高流动性资产，防御性配置",
    typicalAssets: ["活期存款", "货币基金", "短期理财"],
  },
];

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

const getCategoryDescription = (category) => {
  const descriptions = {
    equity: "包括股票、股票基金等权益类投资，收益与经济增长正相关",
    bond: "包括银行理财、债券、保险等固定收益产品，风险相对较低",
    commodity: "包括房地产、黄金、加密货币等实物和另类资产，抗通胀",
    cash: "包括存款、货币基金等高流动性资产，用于资金管理",
  };
  return descriptions[category] || "各类资产配置";
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
  // 添加空值检查
  if (!phase) return "info";
  const types = {
    recovery: "success",
    overheat: "warning",
    stagflation: "danger",
    recession: "info",
  };
  return types[phase] || "info";
};

const getPhaseName = (phase) => {
  // 添加空值检查
  if (!phase) return "未知周期";

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

//debug
// 添加详细的调试方法
const debugReportData = () => {
  console.log("🔍 报告数据调试:", {
    economic_phase: props.report.economic_phase,
    has_economic_phase: !!props.report.economic_phase,
    report_id: props.report.id || props.report.report_id,
    id: props.report.id,
    report_id: props.report.report_id,
    all_keys: Object.keys(props.report),
  });
  // 检查经济周期相关的可能字段
  const possiblePhaseFields = [
    "economic_phase",
    "phase",
    "economicPhase",
    "economic_period",
    "period",
  ];
  possiblePhaseFields.forEach((field) => {
    if (props.report[field]) {
      console.log(`📌 找到经济周期字段 ${field}:`, props.report[field]);
    }
  });
};

// 监听报告数据变化
watch(
  () => props.report,
  (newReport) => {
    console.log("🔄 报告数据更新");
    debugReportData();
  },
  { deep: true, immediate: true }
);

// 组件挂载时也调试
onMounted(() => {
  console.log("🚀 组件挂载完成");
  debugReportData();
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
  display: flex;
  align-items: center;
}

.tip-icon {
  color: #409eff;
  margin-left: 8px;
  cursor: help;
}

.info-icon {
  color: #909399;
  margin-left: 4px;
  cursor: help;
  font-size: 12px;
}

.mapping-tip {
  max-width: 250px;
}

.mapping-tip ul {
  margin: 8px 0;
  padding-left: 16px;
}

.mapping-tip li {
  margin-bottom: 4px;
  font-size: 12px;
}

.category-tip {
  max-width: 200px;
  font-size: 12px;
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
  display: flex;
  align-items: center;
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

/* 资产分类说明样式 */
.mapping-guide {
  padding: 10px;
}

.guide-section {
  margin-bottom: 20px;
}

.guide-section h4 {
  margin-bottom: 12px;
  color: #303133;
}

.category-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.category-card {
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  padding: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.color-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.card-header strong {
  flex: 1;
}

.category-desc {
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
}

.typical-assets {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.asset-label {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
}

.asset-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

/* 确保按钮在小屏幕上也能正常显示 */
@media (max-width: 768px) {
  .history-controls {
    flex-direction: column;
    align-items: flex-end;
  }

  .category-cards {
    grid-template-columns: 1fr;
  }
}
</style>
