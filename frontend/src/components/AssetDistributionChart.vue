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
            const categoryCode = match[1];
            const categoryName = match[2];

            processedData.push({
              value: value,
              name: categoryName,
              code: categoryCode,
              level: getCategoryLevel(categoryCode),
              parentCode: getParentCategoryCode(categoryCode),
              itemStyle: { color: getCategoryColor(categoryCode) },
            });
          } else {
            // 如果没有括号格式，直接使用
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

    // 获取分类层级 - 修复后的逻辑
    const getCategoryLevel = (categoryCode) => {
      const parts = categoryCode.split(".");
      if (parts.length === 1) return 1; // equity, fixed_income 等
      if (parts.length === 2) return 2; // equity.stock, equity.fund 等
      if (parts.length === 3) return 3; // equity.stock.us, equity.stock.cn_a 等
      return 1;
    };

    // 获取父级分类代码 - 修复后的逻辑
    const getParentCategoryCode = (categoryCode) => {
      const parts = categoryCode.split(".");
      if (parts.length === 1) return null; // 一级分类没有父级
      if (parts.length === 2) return parts[0]; // equity.stock -> equity
      if (parts.length === 3) return parts[0] + "." + parts[1]; // equity.stock.us -> equity.stock
      return null;
    };

    // 一级分类颜色映射
    const level1Categories = {
      equity: { name: "权益类", color: "#5470c6" },
      fixed_income: { name: "固定收益类", color: "#91cc75" },
      cash: { name: "现金类", color: "#fac858" },
      insurance: { name: "保险类", color: "#ee6666" },
      physical: { name: "实物资产", color: "#73c0de" },
      alternative: { name: "另类投资", color: "#3ba272" },
    };

    const getCategoryColor = (categoryCode) => {
      const colorMap = {
        equity: "#5470c6",
        fixed_income: "#91cc75",
        cash: "#fac858",
        insurance: "#ee6666",
        physical: "#73c0de",
        alternative: "#3ba272",
      };

      // 获取一级分类代码
      const mainCategory = categoryCode.split(".")[0];
      return colorMap[mainCategory] || "#c0c0c0";
    };

    // 切换分类层级
    const switchLevel = (level) => {
      currentLevel.value = level;
      applyLevelFilter(level);
    };

    // 应用层级过滤 - 修复后的逻辑
    const applyLevelFilter = (targetLevel) => {
      if (targetLevel === 1) {
        // 一级视图：聚合到一级分类
        const level1Data = {};

        rawData.value.forEach((item) => {
          // 找到该分类对应的一级分类代码
          const level1Code = item.code.split(".")[0];
          const level1Info = level1Categories[level1Code] || {
            name: level1Code,
            color: getCategoryColor(level1Code),
          };

          if (!level1Data[level1Code]) {
            level1Data[level1Code] = {
              value: 0,
              name: level1Info.name,
              code: level1Code,
              level: 1,
              itemStyle: { color: level1Info.color },
            };
          }
          level1Data[level1Code].value += item.value;
        });

        chartData.value = Object.values(level1Data);
      } else {
        // 二级视图：显示二级分类，聚合三级分类数据
        const level2Data = {};

        rawData.value.forEach((item) => {
          let targetCode, targetName;

          if (item.level === 1) {
            // 一级分类在二级视图中不显示
            return;
          } else if (item.level === 2) {
            // 二级分类直接使用
            targetCode = item.code;
            targetName = item.name;
          } else if (item.level === 3) {
            // 三级分类聚合到对应的二级分类
            targetCode = item.parentCode;
            targetName = getCategoryDisplayName(targetCode);
          }

          if (targetCode && targetName) {
            if (!level2Data[targetCode]) {
              level2Data[targetCode] = {
                value: 0,
                name: targetName,
                code: targetCode,
                level: 2,
                itemStyle: { color: getCategoryColor(targetCode) },
              };
            }
            level2Data[targetCode].value += item.value;
          }
        });

        chartData.value = Object.values(level2Data);
      }

      updateChartOption();
    };

    // 获取分类显示名称
    const getCategoryDisplayName = (categoryCode) => {
      const nameMap = {
        "equity.stock": "股票",
        "equity.fund": "基金",
        "equity.derivatives": "衍生品",
        "fixed_income.bond": "债券",
        "fixed_income.deposit": "银行存款",
        "fixed_income.wealth_mgmt": "银行理财",
        "fixed_income.national_debt": "国债",
        "insurance.life": "保险",
        "insurance.health": "健康保险",
        "insurance.property": "财产保险",
        "physical.real_estate": "房地产",
        "physical.gold": "黄金",
        "physical.collectibles": "收藏品",
        "alternative.crypto": "加密货币",
        "alternative.private_equity": "私募股权",
        "alternative.other": "其他",
        "cash.savings": "活期存款",
        "cash.money_fund": "货币基金",
      };
      return nameMap[categoryCode] || categoryCode;
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
