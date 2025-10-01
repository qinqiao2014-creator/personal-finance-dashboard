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
};
