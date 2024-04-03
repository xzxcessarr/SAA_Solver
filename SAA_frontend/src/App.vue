<template>
  <div class="app-container">
    <header class="app-header">
      <h1>数据分析与可视化</h1>
    </header>
    <main class="app-main">
      <ConfigSelect @form-submitted="handleFormSubmit" />
      <EchartsDraw :form-submitted="formSubmitted" />
      <ClusterSample/>
    </main>
    <footer class="app-footer">
      <p>&copy; 2023 数据分析与可视化. All rights reserved.</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import ConfigSelect from './components/ConfigSelect.vue';
import EchartsDraw from './components/EchartsDraw.vue';
import ClusterSample from './components/ClusterSample.vue';

const formSubmitted = ref(false);

const handleFormSubmit = () => {
  formSubmitted.value = true;
};
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background-color: #f5f5f5;
  padding: 20px;
  text-align: center;
}

.app-main {
  flex: 1;
  padding: 20px;
}

.app-footer {
  background-color: #f5f5f5;
  padding: 20px;
  text-align: center;
}
</style>