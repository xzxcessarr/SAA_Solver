<template>
  <div class="init-container">
    <!-- <el-row>
        <EchartsDraw :form-submitted="formSubmitted" />
    </el-row>
    <el-row>
      
      <ConfigSelect @form-submitted="handleFormSubmit" />
    </el-row>
    <footer class="init-footer">
      <p>&copy; 2023 数据分析与可视化. All rights reserved.</p>
    </footer> -->
  </div>
</template>

<script setup lang="ts" name="Init">
// import { ref } from 'vue';
// import ConfigSelect from '../components/ConfigSelect.vue';
// import EchartsDraw from '../components/EchartsDraw.vue';

// const formSubmitted = ref(false);

// const handleFormSubmit = () => {
//   formSubmitted.value = true;
// };
</script>

<style scoped>
.init-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.init-footer {
  background-color: #f5f5f5;
  padding: 20px;
  text-align: center;
}
</style>