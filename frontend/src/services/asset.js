import api from "./api";

export const assetAPI = {
  // 修正：使用正确的分类 API 路径
  getCategories() {
    return api.get("/categories/asset-categories");
  },

  // 其他方法保持不变...
  getAssets: (params) => api.get("/assets", { params }),
  getAsset: (id) => api.get(`/assets/${id}`),
  createAsset: (assetData) => api.post("/assets", assetData),
  updateAsset: (id, assetData) => api.put(`/assets/${id}`, assetData),
  deleteAsset: (id) => api.delete(`/assets/${id}`),
  getAssetSummary: () => api.get("/assets/summary/total"),
  getAssetTrend: (days = 30) =>
    api.get("/assets/chart/trend", { params: { days } }),

  // ✅ 新增：美林资产配置分析
  getAllocationAnalysis: (phase = "recovery") =>
    api.get("/assets/merrill/allocation-analysis", { params: { phase } }),

  // ✅ 新增：诊断报告相关API - 根据您的后端路由调整
  getDiagnosisReports: () => api.get("/reports"),
  getDiagnosisReport: (reportId) => api.get(`/reports/${reportId}`),
  deleteDiagnosisReport: (reportId) => api.delete(`/reports/${reportId}`),
};

// export const getAssetTrend = (days = 30) =>
//   api.get("/assets/chart/trend", {
//     params: { days }, // axios 会自动拼 ?days=30
//   });
