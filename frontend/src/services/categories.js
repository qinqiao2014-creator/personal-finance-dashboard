import api from "./api";

export const categoryAPI = {
  // 获取资产分类树
  getAssetCategories: () => api.get("/categories/asset-categories"),

  // 获取扁平分类列表
  getFlatCategories: () => api.get("/categories/asset-categories/flat"),
};
