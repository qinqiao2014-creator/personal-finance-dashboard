import axios from "axios";

// 根据环境选择API地址
const getBaseURL = () => {
  const hostname = window.location.hostname;

  console.log("🌐 检测到域名:", hostname);

  // 如果是 Tailscale 公网域名
  if (hostname === "pc.tail4461b.ts.net") {
    return "/api"; // 使用相对路径，Funnel会自动转发到后端8000端口
  } else {
    return "http://localhost:8000"; // 开发环境
  }
};

const api = axios.create({
  // baseURL: "http://localhost:8000",
  baseURL: getBaseURL(),
  timeout: 10000,
});

// 请求拦截器 - 自动添加token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 错误处理
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      // window.location.href = "/login"; //不需要跳转
    }
    return Promise.reject(error);
  }
);

export default api;

// export const authAPI = {
//   login: (credentials) => api.post("/auth/login", credentials),
//   register: (userData) => api.post("/auth/register", userData),
// };
