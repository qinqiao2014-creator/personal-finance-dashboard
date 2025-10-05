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

        <!-- 新的分类列 -->
        <el-table-column label="分类" width="180">
          <template #default="{ row }">
            <div v-if="row.category_name">
              <el-tag type="info" size="small">{{ row.category_name }}</el-tag>
              <div class="category-path" v-if="row.category_code">
                {{ row.category_code }}
              </div>
            </div>
            <span v-else class="no-category">未分类</span>
          </template>
        </el-table-column>

        <el-table-column prop="amount" label="金额" width="120">
          <template #default="{ row }"
            >¥ {{ row.amount?.toFixed(2) || "0.00" }}</template
          >
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
        @submit.prevent
      >
        <el-form-item label="资产名称" prop="name">
          <el-input v-model="assetForm.name" placeholder="请输入资产名称" />
        </el-form-item>

        <!-- 重要变更：使用分类选择器替代类型选择 -->
        <el-form-item
          v-if="showCreateDialog"
          label="资产分类"
          prop="category_code"
        >
          <CategorySelector
            :value="assetForm.category_code"
            :categories-data="categoriesData"
            @input="handleCategoryInput"
            @change="handleCategoryChange"
          />

          <!-- 开发时的功能：调试信息 -->
          <template v-if="false">
            <div style="margin-top: 8px; font-size: 12px; color: #666">
              调试信息:
              <span v-if="assetForm.category_code">
                已选择: {{ assetForm.category_code }} ({{
                  getCategoryName(assetForm.category_code)
                }})
              </span>
              <span v-else style="color: red">未选择分类</span>
            </div>
          </template>
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
import { assetAPI } from "@/services/asset";
import { categoryAPI } from "@/services/categories";
import CategorySelector from "@/components/CategorySelector.vue";

// 响应式数据
const loading = ref(false);
const formLoading = ref(false);
const showCreateDialog = ref(false);
const isEditing = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const filterCategory = ref("");
const assetFormRef = ref();

// 分类数据
const categoriesData = ref([]);

// 资产列表数据
const assetsList = ref([]);

// 资产表单数据
const assetForm = reactive({
  id: null,
  name: "",
  category_code: "",
  amount: null,
  description: "",
});

// 添加分类变化监听
const onCategoryChange = (value) => {
  console.log("分类选择器变化:", value);
  console.log("当前 assetForm.category_code:", assetForm.category_code);
  console.log("值类型:", typeof value);
};

// 获取分类名称
const getCategoryName = (code) => {
  const category = categoriesData.value.find((cat) => cat.code === code);
  return category ? category.name : "未知分类";
};

// 表单验证规则
const assetRules = {
  name: [
    { required: true, message: "请输入资产名称", trigger: "change" },
    { min: 1, max: 100, message: "长度在 1 到 100 个字符", trigger: "change" },
  ],
  category_code: [
    {
      required: true,
      message: "请选择资产分类",
      trigger: "change",
    },
  ],
  amount: [
    {
      required: true,
      message: "请输入金额",
      trigger: "change",
    },
    {
      type: "number",
      min: 0.01,
      message: "金额必须大于0",
      trigger: "change",
    },
  ],
};

const formatDate = (dateString) => {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleString("zh-CN");
};

// 加载分类数据
const loadCategories = async () => {
  try {
    const response = await categoryAPI.getAssetCategories();
    console.log("分类数据:", response.data);

    const categoryData = response.data;

    if (categoryData.full_tree && Array.isArray(categoryData.full_tree)) {
      categoriesData.value = flattenCategoryTree(categoryData.full_tree);
    } else {
      categoriesData.value = categoryData.common_categories || [];
    }

    console.log("处理后的分类数据:", categoriesData.value);
  } catch (error) {
    console.error("加载分类数据失败:", error);
    ElMessage.error("加载分类数据失败");
    categoriesData.value = [];
  }
};

// 将树形结构转换为扁平数组
const flattenCategoryTree = (tree, parentCode = null, level = 1) => {
  let result = [];

  for (const node of tree) {
    const category = {
      code: node.code,
      name: node.name,
      level: level,
      parent_code: parentCode,
      is_common: node.is_common || false,
    };
    result.push(category);

    if (node.children && Array.isArray(node.children)) {
      const children = flattenCategoryTree(node.children, node.code, level + 1);
      result = result.concat(children);
    }
  }

  return result;
};

// 获取资产列表
const fetchAssets = async () => {
  loading.value = true;
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
    };

    if (filterCategory.value) {
      params.category_code = filterCategory.value;
    }

    const response = await assetAPI.getAssets(params);
    console.log("资产列表响应:", response.data);

    assetsList.value = response.data.items || [];
    total.value = response.data.total || 0;

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
    category_code: asset.category_code,
    amount: asset.amount,
    description: asset.description || "",
  });
  showCreateDialog.value = true;
};

// 删除资产
const deleteAsset = async (asset) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除资产 "${asset.name}" 吗？`,
      "确认删除",
      {
        type: "warning",
      }
    );

    await assetAPI.deleteAsset(asset.id);
    ElMessage.success("资产删除成功");
    fetchAssets();
  } catch (error) {
    if (error !== "cancel") {
      console.error("删除资产失败:", error);
      ElMessage.error("删除资产失败");
    }
  }
};

// 提交资产表单
const submitAssetForm = async (event) => {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  formLoading.value = true;
  try {
    console.log("开始提交表单验证");

    // 使用 Element Plus 的表单验证
    await assetFormRef.value.validate();

    console.log("表单验证通过，准备提交数据");

    const formData = {
      name: assetForm.name.trim(),
      category_code: assetForm.category_code,
      amount: parseFloat(assetForm.amount),
      description: assetForm.description?.trim() || "",
    };

    console.log("提交的表单数据:", formData);

    if (isEditing.value) {
      await assetAPI.updateAsset(assetForm.id, formData);
      ElMessage.success("资产更新成功");
    } else {
      await assetAPI.createAsset(formData);
      ElMessage.success("资产创建成功");
    }

    showCreateDialog.value = false;
    fetchAssets();
  } catch (error) {
    console.error("提交表单失败:", error);
    console.error("错误详情:", JSON.stringify(error, null, 2));

    // 专门处理 Element Plus 的表单验证错误
    if (error && typeof error === "object") {
      // 检查是否是表单验证错误
      const fieldErrors = Object.keys(error);
      if (fieldErrors.length > 0) {
        const firstError = error[fieldErrors[0]];
        if (Array.isArray(firstError) && firstError.length > 0) {
          ElMessage.error(
            `表单验证失败: ${firstError[0].message || "请检查输入"}`
          );
          return;
        }
      }
    }

    // 其他类型的错误
    if (error.message) {
      ElMessage.error(error.message);
    } else {
      ElMessage.error(isEditing.value ? "更新资产失败" : "创建资产失败");
    }
  } finally {
    formLoading.value = false;
  }
};

// 重置表单
const resetForm = () => {
  if (assetFormRef.value) {
    assetFormRef.value.resetFields();
  }
  isEditing.value = false;
  Object.assign(assetForm, {
    id: null,
    name: "",
    category_code: "",
    amount: null,
    description: "",
  });
};

// 分类选择器输入事件处理
const handleCategoryInput = (value) => {
  console.log("分类选择器输入:", value);
  // 确保 value 是字符串，不是 Event 对象
  if (typeof value === "string") {
    assetForm.category_code = value;
  } else if (value && value.target) {
    // 如果是 Event 对象，从 target 获取值
    assetForm.category_code = value.target.value;
  }
};

// 分类选择器变化事件处理
const handleCategoryChange = (value) => {
  console.log("分类选择器变化:", value);
  // 确保 value 是字符串，不是 Event 对象
  if (typeof value === "string") {
    assetForm.category_code = value;
  } else if (value && value.target) {
    // 如果是 Event 对象，从 target 获取值
    assetForm.category_code = value.target.value;
  }
};

// 生命周期
onMounted(() => {
  loadCategories();
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
  padding: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.category-path {
  font-size: 0.8em;
  color: #909399;
  margin-top: 2px;
}

.no-category {
  color: #c0c4cc;
  font-style: italic;
}
</style>
