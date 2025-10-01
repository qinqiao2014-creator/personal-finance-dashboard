<template>
  <div class="category-selector">
    <!-- 常用分类快速选择 -->
    <div
      class="quick-categories"
      v-if="showQuickSelect && commonCategories.length > 0"
    >
      <div class="quick-title">常用分类</div>
      <div class="quick-buttons">
        <button
          v-for="category in commonCategories"
          :key="category.code"
          class="quick-btn"
          :class="{ active: selectedCategory === category.code }"
          @click="selectQuickCategory(category)"
        >
          {{ category.name }}
        </button>
      </div>
    </div>

    <!-- 精细分类选择 -->
    <div class="detailed-categories">
      <div class="detailed-title">精细分类</div>
      <div class="category-levels">
        <!-- 一级分类 -->
        <div class="level-group">
          <label>大类:</label>
          <select v-model="selectedLevel1" @change="onLevel1Change">
            <option value="">请选择</option>
            <option
              v-for="category in level1Categories"
              :key="category.code"
              :value="category.code"
            >
              {{ category.name }}
            </option>
          </select>
        </div>

        <!-- 二级分类 -->
        <div
          class="level-group"
          v-if="selectedLevel1 && level2Categories.length > 0"
        >
          <label>中类:</label>
          <select v-model="selectedLevel2" @change="onLevel2Change">
            <option value="">请选择</option>
            <option
              v-for="category in level2Categories"
              :key="category.code"
              :value="category.code"
            >
              {{ category.name }}
            </option>
          </select>
        </div>

        <!-- 三级分类 -->
        <div
          class="level-group"
          v-if="selectedLevel2 && level3Categories.length > 0"
        >
          <label>小类:</label>
          <select v-model="selectedLevel3" @change="onLevel3Change">
            <option value="">请选择</option>
            <option
              v-for="category in level3Categories"
              :key="category.code"
              :value="category.code"
            >
              {{ category.name }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- 当前选择显示 -->
    <div
      class="selected-display"
      v-if="selectedCategory && selectedCategoryName"
    >
      <span>已选择: {{ selectedCategoryName }}</span>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">加载分类数据中...</div>

    <!-- 错误状态 -->
    <div v-if="error" class="error">分类数据加载失败</div>
  </div>
</template>

<script>
export default {
  name: "CategorySelector",
  props: {
    value: {
      type: String,
      default: "",
    },
    showQuickSelect: {
      type: Boolean,
      default: true,
    },
    categoriesData: {
      type: Array,
      default: () => [],
    },
    apiUrl: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      selectedCategory: this.value,
      selectedLevel1: "",
      selectedLevel2: "",
      selectedLevel3: "",
      loading: false,
      error: false,
      internalCategories: [],
    };
  },
  computed: {
    actualCategories() {
      return this.categoriesData && this.categoriesData.length > 0
        ? this.categoriesData
        : this.internalCategories;
    },

    commonCategories() {
      if (!this.actualCategories || !Array.isArray(this.actualCategories)) {
        return [];
      }

      return this.actualCategories.filter((cat) => cat.is_common);
    },

    level1Categories() {
      if (!this.actualCategories || !Array.isArray(this.actualCategories)) {
        return [];
      }

      return this.actualCategories.filter((cat) => cat.level === 1);
    },

    level2Categories() {
      if (!this.selectedLevel1 || !this.actualCategories) return [];

      return this.actualCategories.filter(
        (cat) => cat.level === 2 && cat.parent_code === this.selectedLevel1
      );
    },

    level3Categories() {
      if (!this.selectedLevel2 || !this.actualCategories) return [];

      return this.actualCategories.filter(
        (cat) => cat.level === 3 && cat.parent_code === this.selectedLevel2
      );
    },

    selectedCategoryName() {
      if (!this.selectedCategory || !this.actualCategories) return "";

      const category = this.actualCategories.find(
        (cat) => cat.code === this.selectedCategory
      );
      if (!category) return this.selectedCategory;

      return this.getCategoryPath(category);
    },
  },
  watch: {
    value(newVal) {
      this.selectedCategory = newVal;
      this.updateLevelSelections(newVal);
    },

    categoriesData(newData) {
      if (newData && newData.length > 0) {
        this.internalCategories = newData;
        this.updateLevelSelections(this.selectedCategory);
      }
    },
  },
  methods: {
    getCategoryPath(category) {
      if (!category || !this.actualCategories) return category.name;

      if (category.level === 1) {
        return category.name;
      }

      let path = category.name;
      let parent = this.findParentCategory(category);

      while (parent) {
        path = `${parent.name} › ${path}`;
        parent = this.findParentCategory(parent);
      }

      return path;
    },

    findParentCategory(category) {
      if (!category.parent_code) return null;

      return this.actualCategories.find(
        (cat) => cat.code === category.parent_code
      );
    },

    selectQuickCategory(category) {
      this.selectedCategory = category.code;
      this.updateLevelSelections(category.code);
      this.emitChange();
    },

    onLevel1Change() {
      this.selectedLevel2 = "";
      this.selectedLevel3 = "";
      this.updateSelectedCategory();
    },

    onLevel2Change() {
      this.selectedLevel3 = "";
      this.updateSelectedCategory();
    },

    onLevel3Change() {
      this.updateSelectedCategory();
    },

    updateSelectedCategory() {
      if (this.selectedLevel3) {
        this.selectedCategory = this.selectedLevel3;
      } else if (this.selectedLevel2) {
        this.selectedCategory = this.selectedLevel2;
      } else if (this.selectedLevel1) {
        this.selectedCategory = this.selectedLevel1;
      } else {
        this.selectedCategory = "";
      }
      this.emitChange();
    },

    updateLevelSelections(categoryCode) {
      if (!categoryCode) {
        this.selectedLevel1 = "";
        this.selectedLevel2 = "";
        this.selectedLevel3 = "";
        return;
      }

      const category = this.actualCategories.find(
        (cat) => cat.code === categoryCode
      );
      if (!category) return;

      if (category.level === 1) {
        this.selectedLevel1 = category.code;
        this.selectedLevel2 = "";
        this.selectedLevel3 = "";
      } else if (category.level === 2) {
        this.selectedLevel1 = category.parent_code;
        this.selectedLevel2 = category.code;
        this.selectedLevel3 = "";
      } else if (category.level === 3) {
        const parent = this.findParentCategory(category);
        this.selectedLevel1 = parent.parent_code;
        this.selectedLevel2 = category.parent_code;
        this.selectedLevel3 = category.code;
      }
    },

    emitChange() {
      console.log("发射变化:", this.selectedCategory);
      this.$emit("input", this.selectedCategory);
      this.$emit("change", this.selectedCategory);
    },

    async loadCategories() {
      if (!this.apiUrl) return;

      this.loading = true;
      this.error = false;

      try {
        const response = await fetch(this.apiUrl);
        const data = await response.json();
        this.internalCategories = data;
      } catch (err) {
        console.error("加载分类数据失败:", err);
        this.error = true;
      } finally {
        this.loading = false;
      }
    },
  },
  mounted() {
    if (
      (!this.categoriesData || this.categoriesData.length === 0) &&
      this.apiUrl
    ) {
      this.loadCategories();
    } else if (this.categoriesData && this.categoriesData.length > 0) {
      this.internalCategories = this.categoriesData;
    }

    if (this.value) {
      this.updateLevelSelections(this.value);
    }
  },
};
</script>

<style scoped>
.category-selector {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
}

.quick-categories,
.detailed-categories {
  margin-bottom: 16px;
}

.quick-title,
.detailed-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

.quick-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #f5f5f5;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-btn:hover {
  background: #e9e9e9;
}

.quick-btn.active {
  background: #1890ff;
  color: white;
  border-color: #1890ff;
}

.category-levels {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.level-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.level-group label {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

.level-group select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 120px;
}

.selected-display {
  margin-top: 12px;
  padding: 8px;
  background: #f0f8ff;
  border-radius: 4px;
  font-size: 14px;
  color: #1890ff;
}

.loading,
.error {
  padding: 8px;
  border-radius: 4px;
  text-align: center;
  margin-top: 12px;
}

.loading {
  background: #fffbf0;
  color: #d46b08;
}

.error {
  background: #fff2f0;
  color: #a8071a;
}
</style>
