<template>
  <div class="diagnosis-process">
    <!-- 步骤1: 分析资产 -->
    <div v-if="currentStep === 1" class="diagnosis-step">
      <el-icon class="step-icon"><Search /></el-icon>
      <h3>正在分析您的资产配置</h3>
      <p>扫描您的股票、基金、债券等资产分布...</p>
      <el-progress :percentage="stepProgress" :show-text="false" />
    </div>

    <!-- 步骤2: 匹配周期 -->
    <div v-if="currentStep === 2" class="diagnosis-step">
      <el-icon class="step-icon"><TrendCharts /></el-icon>
      <h3>正在匹配美林时钟经济周期</h3>
      <p>根据当前经济阶段优化配置建议...</p>
      <el-progress :percentage="stepProgress" :show-text="false" />
    </div>

    <!-- 步骤3: 生成报告 -->
    <div v-if="currentStep === 3" class="diagnosis-step">
      <el-icon class="step-icon"><DocumentChecked /></el-icon>
      <h3>诊断完成！</h3>
      <p>已生成专业的资产配置建议</p>
      <el-result icon="success" title="诊断报告已就绪" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { Search, TrendCharts, DocumentChecked } from '@element-plus/icons-vue'

const props = defineProps({
  currentStep: {
    type: Number,
    default: 1
  },
  stepProgress: {
    type: Number,
    default: 0
  }
})

// 步骤图标可以根据需要调整
</script>

<style scoped>
.diagnosis-process {
  text-align: center;
  padding: 40px 20px;
}

.diagnosis-step {
  max-width: 400px;
  margin: 0 auto;
}

.step-icon {
  font-size: 64px;
  color: #409eff;
  margin-bottom: 20px;
}

.diagnosis-step h3 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 18px;
}

.diagnosis-step p {
  margin: 0 0 20px 0;
  color: #606266;
  font-size: 14px;
}
</style>