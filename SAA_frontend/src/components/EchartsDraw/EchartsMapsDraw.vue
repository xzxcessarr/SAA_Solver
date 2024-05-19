<!-- 
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Echarts.

Author: cessarr
Date Created: 2024-05-19
License: MIT License

Description:
------------
此组件用于在Vue3框架下实现地图的显示和数据的动态更新。 
-->

<template>
  <div class="flex justify-center w-full">
    <div class="w-full lg:max-w-6xl mx-auto p-2">
      <div class="h-96 border-2 border-gray-800 shadow-md">
        <div ref="chartRef" class="w-full h-full"></div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue';
import axios from 'axios';
import { useECharts } from '@/hooks/useEchartsMaps';
import { useEchartsStore } from '@/store/echartsStore';

const echartsParams = useEchartsStore()

// const props = defineProps({
// IS: Number
// });

const chartRef = ref<HTMLElement | null>(null);
const coordinates = ref<number[][]>([]);
// const coordinates = computed(() => echartsStore.coordinates);

// function handleUpdateCoordinates(newCoordinates) {
//   echartsStore.updateCoordinates(newCoordinates);
// }

const { cleanup } = useECharts(chartRef, coordinates);

async function fetchCoordinates(numCities) {
  try {
      const response = await axios.get('/api/get-distance-matrix', {
          params: { num_cities: numCities }
      });
      coordinates.value = response.data.coordinates;
      // console.log(coordinates)
      // handleUpdateCoordinates(response.data.coordinates);
  } catch (error) {
      console.error('Failed to fetch coordinates:', error);
  }
}

onMounted(() => {
  fetchCoordinates(echartsParams.params.IS); 
});

watch(() => echartsParams.params.IS, (newIS) => {
  fetchCoordinates(newIS);
});

onUnmounted(() => {
  cleanup();
});
</script>