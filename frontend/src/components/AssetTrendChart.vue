<template>
  <div class="trend-chart">
    <h3>资产趋势分析</h3>
    <div class="controls">
      <el-select
        v-model="selectedPeriod"
        @change="loadTrendData"
        placeholder="选择时间范围"
      >
        <el-option value="7" label="最近7天" />
        <el-option value="30" label="最近30天" />
        <el-option value="90" label="最近90天" />
      </el-select>
    </div>
    <div v-if="loading" class="chart-loading">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载中...</span>
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
import { assetAPI } from "@/services/asset"; // 需要创建这个API函数
import { ElMessage } from "element-plus";
import { Loading } from "@element-plus/icons-vue";

export default {
  name: "AssetTrendChart",
  components: {
    Loading,
  },
  setup() {
    const chartOption = ref({});
    const selectedPeriod = ref("7");
    const loading = ref(false);

    const loadTrendData = async () => {
      try {
        //console.log("📦 localStorage token:", localStorage.getItem("token")); // ✅ 看这行
        loading.value = true;
        // 调用后端API获取真实数据
        const days = Math.max(
          1,
          Math.min(365, Number(selectedPeriod.value) || 30)
        );
        const response = await assetAPI.getAssetTrend(days);
        const trendData = response.data;

        updateChartOption(trendData);
      } catch (error) {
        console.error("加载趋势数据失败:", error);
        ElMessage.error("加载趋势数据失败");
        // 失败时使用模拟数据
        const mockData = generateMockTrendData(parseInt(selectedPeriod.value));
        updateChartOption(mockData);
      } finally {
        loading.value = false;
      }
    };

    const generateMockTrendData = (days) => {
      const dates = [];
      const values = [];
      const baseValue = 100000;

      for (let i = days; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        dates.push(date.toLocaleDateString());

        const variation = (Math.random() - 0.5) * 0.1;
        const value =
          i === days ? baseValue : values[values.length - 1] * (1 + variation);
        values.push(Math.round(value));
      }

      return dates.map((date, index) => ({
        date: date,
        value: values[index],
      }));
    };

    const updateChartOption = (trendData) => {
      const dates = trendData.map((item) => item.date);
      const values = trendData.map((item) => item.value);

      chartOption.value = {
        title: {
          text: "资产价值趋势",
          left: "center",
        },
        tooltip: {
          trigger: "axis",
          formatter: function (params) {
            const data = params[0];
            return `${data.axisValue}<br/>¥${data.value.toLocaleString()}`;
          },
        },
        xAxis: {
          type: "category",
          data: dates,
          axisLabel: {
            rotate: 45,
          },
        },
        yAxis: {
          type: "value",
          axisLabel: {
            formatter: "¥{value}",
          },
        },
        series: [
          {
            name: "总资产",
            type: "line",
            data: values,
            smooth: true,
            itemStyle: {
              color: "#5470c6",
            },
            areaStyle: {
              color: {
                type: "linear",
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  {
                    offset: 0,
                    color: "rgba(84, 112, 198, 0.3)",
                  },
                  {
                    offset: 1,
                    color: "rgba(84, 112, 198, 0.1)",
                  },
                ],
              },
            },
          },
        ],
        grid: {
          left: "3%",
          right: "4%",
          bottom: "15%",
          top: "15%",
          containLabel: true,
        },
      };
    };

    onMounted(() => {
      loadTrendData();
    });

    return {
      chartOption,
      selectedPeriod,
      loading,
      loadTrendData,
    };
  },
};

const loadTrendData = async () => {
  try {
    console.log("📦 localStorage token:", localStorage.getItem("token"));
    loading.value = true;
    const days = Math.max(1, Math.min(365, Number(selectedPeriod.value) || 30));
    const response = await assetAPI.getAssetTrend(days);
    const trendData = response.data;

    // 添加调试信息
    console.log("📊 趋势数据:", trendData);
    if (trendData.length > 0) {
      console.log("📈 数据范围:", {
        start: trendData[0].date,
        end: trendData[trendData.length - 1].date,
        startValue: trendData[0].value,
        endValue: trendData[trendData.length - 1].value,
      });
    }

    updateChartOption(trendData);
  } catch (error) {
    console.error("加载趋势数据失败:", error);
    ElMessage.error("加载趋势数据失败");
    // 使用模拟数据时也确保是累计逻辑
    const mockData = generateMockTrendData(parseInt(selectedPeriod.value));
    updateChartOption(mockData);
  } finally {
    loading.value = false;
  }
};
</script>
