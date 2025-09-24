// 这个文件负责管理页面导航
import { createRouter, createWebHistory } from "vue-router";

// 导入页面组件 - 我们先创建这两个文件
import LoginView from "../views/LoginView.vue";
import DashboardView from "../views/DashboardView.vue";

// 定义路由规则：什么路径显示什么页面
const routes = [
  {
    path: "/", // 当访问网站根目录时
    name: "login", // 路由名称
    component: LoginView, // 显示登录页面
  },
  {
    path: "/dashboard", // 当访问/dashboard时
    name: "dashboard", // 路由名称
    component: DashboardView, // 显示仪表盘页面
  },
];

// 创建路由实例
const router = createRouter({
  history: createWebHistory(), // 使用HTML5 history模式
  routes, // 传入路由配置
});

// 导出路由，以便在其他文件中使用
export default router;
