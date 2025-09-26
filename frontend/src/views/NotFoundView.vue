<template>
  <div class="not-found-container">
    <h1>404 - 页面未找到</h1>
    <p>抱歉，您访问的页面不存在。</p>
    <router-link to="/dashboard">返回首页</router-link>
  </div>
</template>

<script setup>
// 404页面
</script>

<style scoped>
.not-found-container {
  text-align: center;
  padding: 50px;
}
</style>
