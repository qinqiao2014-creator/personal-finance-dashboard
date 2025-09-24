
// import { createApp } from "vue";
// import App from "./App.vue";
// import router from "./router"; // 导入路由配置

// // 创建Vue应用
// const app = createApp(App);

// // 使用路由
// app.use(router);

// // 将应用挂载到页面上的#app元素
// app.mount("#app");

import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import App from "./App.vue";
import router from "./router";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(ElementPlus);
app.use(router);
app.mount("#app");