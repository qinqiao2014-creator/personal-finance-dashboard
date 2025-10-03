<template>
  <div class="merrill-clock">
    <!-- 顶部标题 -->
    <div class="clock-header">
      <h3>美林投资时钟</h3>
      <div class="phase-indicator">
        <span class="current-phase">{{ currentPhaseData.name }}</span>
        <span class="economy-state">{{ currentPhaseData.economy }}</span>
      </div>
    </div>

    <!-- 时钟主体 -->
    <div class="clock-container">
      <div
        class="clock-circle"
        :class="{ 'pulse-animation': config.pulseEnabled }"
      >
        <!-- 指针 -->
        <div class="clock-hand" :style="handStyle" />

        <!-- 1. 背景象限（只负责颜色） -->
        <div
          v-for="phase in phases"
          :key="phase.id"
          class="phase-quadrant"
          :class="[
            `phase-${phase.id}`,
            { active: config.currentPhase === phase.id },
          ]"
          :style="getQuadrantStyle(phase.id)"
        />

        <!-- 2. 文字层（不旋转，位于象限中心） -->
        <div class="phase-labels">
          <div
            v-for="phase in phases"
            :key="'label-' + phase.id"
            class="phase-label"
            :class="`phase-${phase.id}-label`"
          >
            <div class="phase-name">{{ phase.name }}</div>
            <div class="phase-economy">{{ phase.economy }}</div>
            <div class="phase-assets">
              <span
                v-for="asset in phase.recommendedAssets"
                :key="asset"
                class="asset-tag"
              >
                {{ asset }}
              </span>
            </div>
          </div>
        </div>

        <!-- 中心圆 -->
        <div class="clock-center">
          <div class="center-title">当前阶段</div>
          <div class="center-phase">{{ currentPhaseData.name }}</div>
        </div>
      </div>
    </div>

    <!-- 资产配置建议 -->
    <div class="recommendation-section">
      <h4>资产配置建议</h4>
      <div class="asset-recommendations">
        <div
          v-for="(weight, asset) in currentPhaseData.assetWeights"
          :key="asset"
          class="asset-item"
        >
          <div class="asset-name">{{ asset }}</div>
          <el-progress
            :percentage="weight"
            :show-text="false"
            :color="getAssetColor(asset)"
          />
          <div class="asset-percent">{{ weight }}%</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

// ==================== 配置区域 - 只需修改这里 ====================
const config = {
  // 当前经济阶段（四选一）：
  // 'recovery' - 复苏期 | 'overheat' - 过热期
  // 'stagflation' - 滞胀期 | 'recession' - 衰退期
  currentPhase: "recovery",

  // 是否启用闪烁效果
  pulseEnabled: true,
};
// ==================== 配置区域结束 ====================

// 美林时钟阶段定义
const phases = ref([
  {
    id: "recovery",
    name: "复苏期",
    economy: "高GDP + 低CPI",
    angle: 135,
    recommendedAssets: ["股票", "债券", "现金", "商品"],
    assetWeights: { 股票: 60, 债券: 30, 现金: 5, 商品: 5 },
  },
  {
    id: "overheat",
    name: "过热期",
    economy: "高GDP + 高CPI",
    angle: 225,
    recommendedAssets: ["商品", "股票", "现金", "债券"],
    assetWeights: { 商品: 50, 股票: 35, 现金: 10, 债券: 5 },
  },
  {
    id: "stagflation",
    name: "滞胀期",
    economy: "低GDP + 高CPI",
    angle: 315,
    recommendedAssets: ["现金", "商品", "债券", "股票"],
    assetWeights: { 现金: 50, 商品: 25, 债券: 20, 股票: 5 },
  },
  {
    id: "recession",
    name: "衰退期",
    economy: "低GDP + 低CPI",
    angle: 45,
    recommendedAssets: ["债券", "现金", "股票", "商品"],
    assetWeights: { 债券: 60, 现金: 25, 股票: 10, 商品: 5 },
  },
]);

// 计算当前阶段数据
const currentPhaseData = computed(() => {
  return (
    phases.value.find((phase) => phase.id === config.currentPhase) ||
    phases.value[0]
  );
});

// 指针样式
const handStyle = computed(() => ({
  transform: `rotate(${currentPhaseData.value.angle}deg)`,
}));

// 获取象限样式
const getQuadrantStyle = (phaseId) => {
  const angles = {
    recovery: "0deg",
    overheat: "90deg",
    stagflation: "180deg",
    recession: "270deg",
  };
  return { transform: `rotate(${angles[phaseId]})` };
};

// 资产颜色
const getAssetColor = (asset) => {
  const colors = {
    股票: "#e6a23c",
    债券: "#67c23a",
    现金: "#409eff",
    商品: "#f56c6c",
  };
  return colors[asset] || "#909399";
};
</script>

<style scoped>
.merrill-clock {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
.clock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}
.clock-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}
.phase-indicator {
  text-align: right;
}
.current-phase {
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
}
.economy-state {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.clock-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}
.clock-circle {
  width: 360px;
  height: 360px;
  border-radius: 50%;
  background: conic-gradient(
    from 0deg,
    #e8f5e8 0deg 90deg,
    #fff3e0 90deg 180deg,
    #fce4ec 180deg 270deg,
    #e1f5fe 270deg 360deg
  );
  position: relative;
  border: 6px solid #e8e8e8;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}
.clock-circle.pulse-animation {
  animation: clockPulse 2s ease-in-out infinite;
}
@keyframes clockPulse {
  0%,
  100% {
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  }
  50% {
    box-shadow: 0 8px 32px rgba(64, 158, 255, 0.25);
  }
}

.clock-hand {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 3px;
  height: 140px;
  background: linear-gradient(to top, #f56c6c, #ff9c6c);
  transform-origin: 50% 0;
  border-radius: 3px;
  z-index: 10;
}
.clock-hand::after {
  content: "";
  position: absolute;
  top: -10px;
  left: -7px;
  width: 18px;
  height: 18px;
  background: #f56c6c;
  border-radius: 50%;
  border: 3px solid white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* 背景象限 - 修复后的样式 */
.phase-quadrant {
  position: absolute;
  width: 180px;
  height: 180px;
  transform-origin: 100% 100%;
  transition: all 0.3s ease;
}

/* 激活状态的脉冲效果 */
.phase-quadrant.active {
  border: 3px solid #409eff;
  box-shadow: inset 0 0 20px rgba(64, 158, 255, 0.15),
    0 0 20px rgba(64, 158, 255, 0.3); /* 添加外发光 */
  animation: quadrantPulse 2s ease-in-out infinite;
}

@keyframes quadrantPulse {
  0%,
  100% {
    box-shadow: inset 0 0 20px rgba(64, 158, 255, 0.15),
      0 0 20px rgba(64, 158, 255, 0.3);
  }
  50% {
    box-shadow: inset 0 0 20px rgba(64, 158, 255, 0.25),
      0 0 30px rgba(64, 158, 255, 0.5);
  }
}

.phase-quadrant.active::after {
  opacity: 1;
}

/* 为每个象限设置不同的圆角 */
.phase-recovery {
  top: -3px;
  left: -3px;
  border-radius: 180px 0 0 0; /* 左上角圆角 */
}
.phase-overheat {
  top: -5px;
  left: -8px;
  border-radius: 180px 0 0 0; /* 右上角圆角 */
}

.phase-stagflation {
  top: -10px;
  left: -10px;
  border-radius: 180px 0 0 0; /* 右下角圆角 */
}
.phase-recession {
  top: -9px;
  left: -2px;
  border-radius: 180px 0 0 0; /* 左下角圆角 */
}

/* 文字层 – 不旋转，位于象限中心 */
.phase-labels {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 100;
}
.phase-label {
  position: absolute;
  width: 120px;
  height: 110px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}
/* 象限中心坐标（360×360） */
.phase-recovery-label {
  top: 35px;
  left: 40px;
}
.phase-overheat-label {
  top: 35px;
  right: 40px;
}
.phase-stagflation-label {
  bottom: 55px;
  right: 40px;
}
.phase-recession-label {
  bottom: 55px;
  left: 40px;
}

.phase-name {
  font-weight: 700;
  font-size: 14px;
  color: #1a1a1a;
  margin-bottom: 4px;
}
.phase-economy {
  font-size: 11px;
  color: #666;
  margin-bottom: 6px;
}
.phase-assets {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2px;
}
.asset-tag {
  background: rgba(255, 255, 255, 0.85);
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 9px;
  color: #409eff;
  font-weight: 500;
}

/* 中心圆 */
.clock-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 100px;
  background: white;
  border-radius: 50%;
  border: 4px solid #409eff;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 30;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}
.center-title {
  font-size: 10px;
  color: #666;
}
.center-phase {
  font-size: 13px;
  font-weight: 700;
  color: #409eff;
}

/* 资产配置建议 */
.recommendation-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}
.recommendation-section h4 {
  margin: 0 0 16px;
  font-size: 16px;
  font-weight: 600;
}
.asset-recommendations {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
.asset-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}
.asset-item:hover {
  background: #f0f2f5;
}
.asset-name {
  min-width: 50px;
  font-weight: 500;
  font-size: 14px;
}
.asset-percent {
  min-width: 35px;
  text-align: right;
  font-weight: 700;
  color: #409eff;
  font-size: 14px;
}

/* 响应式 */
@media (max-width: 640px) {
  .merrill-clock {
    padding: 16px;
  }
  .clock-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  .clock-circle {
    width: 360px;
    height: 360px;
    border-radius: 50%;
    background: transparent; /* 改为透明 */
    position: relative;
    border: 6px solid #e8e8e8;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    overflow: hidden; /* 添加这个 */
  }
  /* 修复象限样式 */
  .phase-quadrant {
    position: absolute;
    width: 180px;
    height: 180px;
    transform-origin: 100% 100%;
    transition: all 0.3s ease;
    background: transparent !important; /* 移除背景色 */
  }
  .phase-overheat {
    left: 140px;
  }
  .phase-stagflation {
    top: 140px;
    left: 140px;
  }
  .phase-recession {
    top: 140px;
  }
  .phase-label {
    width: 90px;
    height: 90px;
    font-size: 12px;
  }
  /* 重新校准小屏中心位置 */
  .phase-recovery-label {
    top: 40px;
    left: 40px;
  }
  .phase-overheat-label {
    top: 40px;
    right: 40px;
  }
  .phase-stagflation-label {
    bottom: 40px;
    right: 40px;
  }
  .phase-recession-label {
    bottom: 40px;
    left: 40px;
  }
  .asset-recommendations {
    grid-template-columns: 1fr;
  }
}
</style>
