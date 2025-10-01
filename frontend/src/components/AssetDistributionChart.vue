<template>
  <div class="distribution-chart">
    <h3>资产分类分布</h3>
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
import { ref, onMounted } from "vue";
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
              itemStyle: { color: getCategoryColor(match[1]) },
            });
          } else {
            processedData.push({
              value: value,
              name: key,
              code: key,
              itemStyle: { color: getCategoryColor(key) },
            });
          }
        }

        chartData.value = processedData;
        updateChartOption(processedData);
      } catch (error) {
        console.error("加载资产分布数据失败:", error);
        ElMessage.error("加载资产分布数据失败");
      } finally {
        loading.value = false;
      }
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
      };
      const mainCategory = categoryCode.split(".")[0];
      return colorMap[mainCategory] || "#c0c0c0";
    };

    const updateChartOption = (chartData) => {
      chartOption.value = {
        title: {
          text: "资产分布",
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
            data: chartData,
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
      refreshData, // 暴露给父组件调用
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
