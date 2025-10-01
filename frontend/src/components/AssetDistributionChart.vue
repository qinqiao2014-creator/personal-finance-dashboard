<template>
  <div class="distribution-chart">
    <div class="chart-header">
      <h3>资产分类分布</h3>
      <div class="level-controls">
        <el-tooltip content="切换到一级分类（大类视图）">
          <el-button
            :type="currentLevel === 1 ? 'primary' : 'default'"
            @click="switchLevel(1)"
            size="small"
            :disabled="loading"
          >
            大类
          </el-button>
        </el-tooltip>
        <el-tooltip content="切换到二级分类（细分视图）">
          <el-button
            :type="currentLevel === 2 ? 'primary' : 'default'"
            @click="switchLevel(2)"
            size="small"
            :disabled="loading"
          >
            细分
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <div v-if="loading" class="chart-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
    </div>
    <div v-else-if="chartData.length === 0" class="chart-empty">
      <el-empty description="暂无资产数据" />
    </div>
    <v-chart
      v-else
      :option="chartOption"
      :style="{ height: '400px' }"
      autoresize
    />
  </div>
</template>

<script>
import { ref, onMounted, computed } from "vue";
import { assetAPI } from "@/services/asset";
import { ElMessage } from "element-plus";
import { Loading } from "@element-plus/icons-vue";

export default {
  name: "AssetDistributionChart",
  components: {
    Loading,
  },
  setup() {
    const chartOption = ref({});
    const chartData = ref([]);
    const loading = ref(true);
    const currentLevel = ref(2); // 默认显示二级分类
    const rawData = ref([]); // 存储原始数据

    const loadDistributionData = async () => {
      try {
        loading.value = true;
        const response = await assetAPI.getAssetSummary();
        const summaryData = response.data;

        // 适配后端返回的数据格式 assets_by_type
        const assetsByType = summaryData.assets_by_type || {};
        const processedData = [];

        for (const [key, value] of Object.entries(assetsByType)) {
          // 解析格式: "equity.stock (股票)" -> name: "股票", code: "equity.stock"
          const match = key.match(/(.+) \((.+)\)/);
          if (match) {
            processedData.push({
              value: value,
              name: match[2], // 分类名称
              code: match[1], // 分类代码
              level: getCategoryLevel(match[1]),
              parentCode: getParentCategoryCode(match[1]),
              itemStyle: { color: getCategoryColor(match[1]) },
            });
          } else {
            processedData.push({
              value: value,
              name: key,
              code: key,
              level: getCategoryLevel(key),
              parentCode: getParentCategoryCode(key),
              itemStyle: { color: getCategoryColor(key) },
            });
          }
        }

        rawData.value = processedData;
        applyLevelFilter(currentLevel.value);
      } catch (error) {
        console.error("加载资产分布数据失败:", error);
        ElMessage.error("加载资产分布数据失败");
      } finally {
        loading.value = false;
      }
    };

    // 获取分类层级
    const getCategoryLevel = (categoryCode) => {
      const parts = categoryCode.split(".");
      return parts.length;
    };

    // 获取父级分类代码
    const getParentCategoryCode = (categoryCode) => {
      const parts = categoryCode.split(".");
      return parts.length > 1 ? parts[0] : null;
    };

    // 一级分类映射
    const level1Categories = {
      cash: { name: "现金类", color: "#5470c6" },
      bank: { name: "银行存款", color: "#91cc75" },
      equity: { name: "权益类", color: "#fac858" },
      bond: { name: "固收类", color: "#ee6666" },
      fund: { name: "基金", color: "#73c0de" },
      real_estate: { name: "房地产", color: "#3ba272" },
      insurance: { name: "保险", color: "#fc8452" },
      other: { name: "其他", color: "#9a60b4" },
      alternative: { name: "另类投资", color: "#ff6b6b" },
      fixed_income: { name: "固收类", color: "#4ecdc4" },
    };

    const getCategoryColor = (categoryCode) => {
      const colorMap = {
        cash: "#5470c6",
        bank: "#91cc75",
        equity: "#fac858",
        bond: "#ee6666",
        fund: "#73c0de",
        real_estate: "#3ba272",
        insurance: "#fc8452",
        other: "#9a60b4",
        alternative: "#ff6b6b",
        fixed_income: "#4ecdc4",
      };
      const mainCategory = categoryCode.split(".")[0];
      return colorMap[mainCategory] || "#c0c0c0";
    };

    // 切换分类层级
    const switchLevel = (level) => {
      currentLevel.value = level;
      applyLevelFilter(level);
    };

    // 应用层级过滤
    const applyLevelFilter = (level) => {
      if (level === 1) {
        // 聚合到一级分类
        const level1Data = {};

        rawData.value.forEach((item) => {
          const parentCode = item.parentCode || item.code;
          const level1Info = level1Categories[parentCode] || {
            name: parentCode,
            color: getCategoryColor(parentCode),
          };

          if (!level1Data[parentCode]) {
            level1Data[parentCode] = {
              value: 0,
              name: level1Info.name,
              code: parentCode,
              level: 1,
              itemStyle: { color: level1Info.color },
            };
          }
          level1Data[parentCode].value += item.value;
        });

        chartData.value = Object.values(level1Data);
      } else {
        // 显示二级分类
        chartData.value = rawData.value;
      }

      updateChartOption();
    };

    const updateChartOption = () => {
      if (chartData.value.length === 0) {
        chartOption.value = {};
        return;
      }

      chartOption.value = {
        title: {
          text: `资产分布 - ${
            currentLevel.value === 1 ? "大类视图" : "细分视图"
          }`,
          left: "center",
          textStyle: {
            fontSize: 16,
            fontWeight: "bold",
          },
        },
        tooltip: {
          trigger: "item",
          formatter: function (params) {
            return `${
              params.name
            }<br/>金额: ¥${params.value.toLocaleString()}<br/>占比: ${
              params.percent
            }%`;
          },
        },
        legend: {
          orient: "vertical",
          left: "left",
          top: "middle",
          type: "scroll",
        },
        series: [
          {
            name: "资产分布",
            type: "pie",
            radius: ["40%", "70%"],
            avoidLabelOverlap: false,
            itemStyle: {
              borderRadius: 10,
              borderColor: "#fff",
              borderWidth: 2,
            },
            label: {
              show: false,
              position: "center",
            },
            emphasis: {
              label: {
                show: true,
                fontSize: 18,
                fontWeight: "bold",
              },
            },
            labelLine: {
              show: false,
            },
            data: chartData.value,
          },
        ],
      };
    };

    // 暴露刷新方法给父组件
    const refreshData = () => {
      return loadDistributionData();
    };

    onMounted(() => {
      loadDistributionData();
    });

    return {
      chartOption,
      loading,
      chartData,
      currentLevel,
      refreshData,
      switchLevel,
    };
  },
};
</script>

<style scoped>
.distribution-chart {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.level-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #909399;
}

.chart-empty {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
