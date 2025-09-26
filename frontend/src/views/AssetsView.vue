<template>
  <div class="assets-container">
    <!-- 页面标题和操作栏 -->
    <div class="assets-header">
      <div class="header-left">
        <el-button @click="$router.push('/dashboard')" :icon="ArrowLeft">
          返回主页
        </el-button>
        <h1>资产管理</h1>
      </div>
      <el-button type="primary" @click="showCreateDialog = true" :icon="Plus">
        新增资产
      </el-button>
    </div>

    <!-- 资产列表 -->
    <el-card class="assets-card">
      <template #header>
        <div class="card-header">
          <span>资产列表</span>
          <div class="header-actions">
            <el-select
              v-model="filterType"
              placeholder="按类型筛选"
              clearable
              @change="fetchAssets"
            >
              <el-option label="股票" value="stock" />
              <el-option label="基金" value="fund" />
              <el-option label="银行存款" value="bank" />
              <el-option label="加密货币" value="crypto" />
              <el-option label="保险" value="insurance" />
              <el-option label="房地产" value="real_estate" />
              <el-option label="其他" value="other" />
            </el-select>

            <el-button :icon="Refresh" @click="fetchAssets" :loading="loading">
              刷新
            </el-button>
          </div>
        </div>
      </template>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>

      <!-- 空状态 -->
      <el-empty v-else-if="assetsList.length === 0" description="暂无资产数据">
        <el-button type="primary" @click="showCreateDialog = true"
          >创建第一个资产</el-button
        >
      </el-empty>

      <!-- 资产表格 -->
      <el-table v-else :data="assetsList" style="width: 100%">
        <el-table-column prop="name" label="资产名称" min-width="120" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getAssetTypeTag(row.type)">{{
              getAssetTypeLabel(row.type)
            }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }">¥ {{ row.amount.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column
          prop="description"
          label="描述"
          min-width="150"
          show-overflow-tooltip
        />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">{{
            formatDate(row.created_at)
          }}</template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editAsset(row)" :icon="Edit">
              编辑
            </el-button>
            <el-button
              size="small"
              type="danger"
              @click="deleteAsset(row)"
              :icon="Delete"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container" v-if="total > 0">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[5, 10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑资产对话框 -->
    <el-dialog
      :title="isEditing ? '编辑资产' : '新增资产'"
      v-model="showCreateDialog"
      width="500px"
      @close="resetForm"
    >
      <el-form
        ref="assetFormRef"
        :model="assetForm"
        :rules="assetRules"
        label-width="80px"
      >
        <el-form-item label="资产名称" prop="name">
          <el-input v-model="assetForm.name" placeholder="请输入资产名称" />
        </el-form-item>

        <el-form-item label="资产类型" prop="type">
          <el-select
            v-model="assetForm.type"
            placeholder="请选择资产类型"
            style="width: 100%"
          >
            <el-option label="股票" value="stock" />
            <el-option label="基金" value="fund" />
            <el-option label="银行存款" value="bank" />
            <el-option label="加密货币" value="crypto" />
            <el-option label="保险" value="insurance" />
            <el-option label="房地产" value="real_estate" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>

        <el-form-item label="金额" prop="amount">
          <el-input-number
            v-model="assetForm.amount"
            :min="0.01"
            :step="0.01"
            :precision="2"
            controls-position="right"
            style="width: 100%"
            placeholder="请输入金额"
          />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="assetForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入资产描述（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="submitAssetForm"
          :loading="formLoading"
        >
          {{ isEditing ? "更新" : "创建" }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Plus,
  Edit,
  Delete,
  Refresh,
  ArrowLeft,
} from "@element-plus/icons-vue";
import api from "@/services/api";

import { useRouter } from "vue-router";
const router = useRouter();

// 响应式数据
const loading = ref(false);
const formLoading = ref(false);
const showCreateDialog = ref(false);
const isEditing = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const filterType = ref("");
const assetFormRef = ref();

// 资产列表数据
const assetsList = ref([]);

// 资产表单数据
const assetForm = reactive({
  id: null,
  name: "",
  type: "",
  amount: null,
  description: "",
});

// 表单验证规则
const assetRules = {
  name: [
    { required: true, message: "请输入资产名称", trigger: "blur" },
    { min: 1, max: 100, message: "长度在 1 到 100 个字符", trigger: "blur" },
  ],
  type: [{ required: true, message: "请选择资产类型", trigger: "change" }],
  amount: [
    { required: true, message: "请输入金额", trigger: "blur" },
    { type: "number", min: 0.01, message: "金额必须大于0", trigger: "blur" },
  ],
};

// 资产类型标签映射
const assetTypeLabels = {
  stock: "股票",
  fund: "基金",
  bank: "银行存款",
  crypto: "加密货币",
  insurance: "保险",
  real_estate: "房地产",
  other: "其他",
};

const assetTypeTags = {
  stock: "success",
  fund: "warning",
  bank: "primary",
  crypto: "danger",
  insurance: "info",
  real_estate: "gray",
  other: "primary",
};

// 方法定义
const getAssetTypeLabel = (type) => assetTypeLabels[type] || type;
const getAssetTypeTag = (type) => assetTypeTags[type] || "";

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString("zh-CN");
};

// 获取资产列表
const fetchAssets = async () => {
  loading.value = true;
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    };

    if (filterType.value) {
      params.type = filterType.value;
    }

    const response = await api.get("/assets", { params });
    assetsList.value = response.data.items;
    total.value = response.data.total;

    ElMessage.success("数据加载成功");
  } catch (error) {
    console.error("获取资产列表失败:", error);
    ElMessage.error("获取资产列表失败");
  } finally {
    loading.value = false;
  }
};

// 分页处理
const handleSizeChange = (newSize) => {
  pageSize.value = newSize;
  currentPage.value = 1;
  fetchAssets();
};

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage;
  fetchAssets();
};

// 编辑资产
const editAsset = (asset) => {
  isEditing.value = true;
  Object.assign(assetForm, {
    id: asset.id,
    name: asset.name,
    type: asset.type,
    amount: asset.amount,
    description: asset.description || "",
  });
  showCreateDialog.value = true;
};

// 删除资产
const deleteAsset = async (asset) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除资产"${asset.name}"吗？此操作不可恢复。`,
      "删除确认",
      {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      }
    );

    await api.delete(`/assets/${asset.id}`);
    ElMessage.success("资产删除成功");
    fetchAssets();
  } catch (error) {
    if (error !== "cancel") {
      console.error("删除资产失败:", error);
      ElMessage.error("删除资产失败");
    }
  }
};

// 提交表单
const submitAssetForm = async () => {
  if (!assetFormRef.value) return;

  const valid = await assetFormRef.value.validate().catch(() => false);
  if (!valid) return;

  formLoading.value = true;

  try {
    if (isEditing.value) {
      // 更新资产
      await api.put(`/assets/${assetForm.id}`, assetForm);
      ElMessage.success("资产更新成功");
    } else {
      // 创建资产
      await api.post("/assets", assetForm);
      ElMessage.success("资产创建成功");
    }

    showCreateDialog.value = false;
    fetchAssets();
  } catch (error) {
    console.error("操作失败:", error);
    ElMessage.error(isEditing.value ? "更新失败" : "创建失败");
  } finally {
    formLoading.value = false;
  }
};

// 重置表单
const resetForm = () => {
  isEditing.value = false;
  assetFormRef.value?.resetFields();
  Object.assign(assetForm, {
    id: null,
    name: "",
    type: "",
    amount: null,
    description: "",
  });
};

// 生命周期
onMounted(() => {
  fetchAssets();
});
</script>

<style scoped>
.assets-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.assets-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h1 {
  margin: 0;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.loading-container {
  padding: 20px 0;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.assets-card {
  margin-bottom: 20px;
}
</style>
