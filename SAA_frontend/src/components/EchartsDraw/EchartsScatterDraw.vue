<!-- 
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Echarts.

Author: cessarr
Date Created: 2024-05-19
License: MIT License

Description:
------------
此组件用于在Vue3框架下实现散点图表的显示和数据的动态更新。 
-->
<template>
  <div class="w-screen"> <!-- 确保父容器有足够的宽度 -->
      <div class="w-full h-[400px] border-2 border-gray-800 shadow-lg p-2.5 bg-white">
          <div ref="chartRef" class="w-full h-full"></div>
      </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, onMounted } from 'vue';
import { useECharts } from '@/hooks/useEchartsScatter';
import axios from 'axios';
import { useEchartsStore } from '@/store/echartsStore';

// const props = defineProps({
//   IS: Number,
//   NS: Number
// });

const echartsParams = useEchartsStore()
const chartRef = ref<HTMLElement | null>(null);
const chartData = ref([]);

// 使用自定义钩子
const { updateChart } = useECharts(chartRef, chartData);

async function fetchAndUpdateEchartsData(IS:Number, NS:Number) {
  try {
      const response = await axios.post('/api/get_echarts_data', {
          cities: IS,
          scenes: NS,


      });

      chartData.value = response.data.data;
      updateChart();
  } catch (error) {
      console.error('Error fetching ECharts data:', error);
  }
}

// 监听 props.IS 和 props.NS 的变化
watch([() => echartsParams.params.IS, () => echartsParams.params.NS], ([newIS, newNS]) => {
  // console.log(newIS, newNS)
  fetchAndUpdateEchartsData(newIS, newNS);
}, { immediate: true });

onMounted(() => {
  fetchAndUpdateEchartsData(echartsParams.params.IS, echartsParams.params.NS);
});
</script>
