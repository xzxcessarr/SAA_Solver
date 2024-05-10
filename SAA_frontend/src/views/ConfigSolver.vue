<template>
    <div>
      <div class="flex justify-center w-full max-w-6xl mx-auto my-5">
        <el-switch v-model="showDefault" active-color="#13ce66" inactive-color="#ff4949" active-text="算例选择与计算" inactive-text="方法参数设置"></el-switch>
      </div>
      <div v-if="showDefault">
        <div class="flex justify-center w-full max-w-6xl mx-auto">
          <ConfigSelect />
        </div>
        <div class="flex justify-center mb-5 w-full max-w-6xl mx-auto">
          <EchartsMapsDraw />
        </div>
        <div class="flex justify-center w-full max-w-6xl mx-auto">
          <EchartsScatterDraw />
        </div>
      </div>
      <div v-else>
        <div class="flex justify-center mb-5 w-full max-w-6xl mx-auto">
          <ClusterParamsAnalyzer />
        </div>
      </div>
      
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue';
  import ConfigSelect from '@/components/ConfigSelect.vue';
  import EchartsScatterDraw from '@/components/EchartsDraw/EchartsScatterDraw.vue';
  import EchartsMapsDraw from '@/components/EchartsDraw/EchartsMapsDraw.vue';
  import ClusterParamsAnalyzer from '@/components/ClusterParamsAnalyzer.vue';
  
  const showDefault = ref(true); // 默认显示第一组组件
  </script>