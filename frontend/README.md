# frontend

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

MerrillClock.vue美林时钟模块：script 脚本用于选择周期
// ==================== 配置区域 - 只需修改这里 ====================
const config = {
// 当前经济阶段（四选一）：
// 'recovery' - 复苏期 | 'overheat' - 过热期
// 'stagflation' - 滞胀期 | 'recession' - 衰退期
currentPhase: "recovery",

// 是否启用闪烁效果
pulseEnabled: true,
};
// ==================== 配置区域结束 ====================
