<template>
  <div class="chart-container">
    <div ref="chartRef" :style="{ width: '100%', height: '400px' }"></div>
    <button @click="changeEcharts">更新</button>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { useECharts } from '@/hooks/useEcharts';

const chartRef = ref<HTMLElement | null>(null);

const chartDataRaw = [
  {
    x: [1, 50, 5, 0],
    y: [1, 1, 5, 5],
    marker: {
      color: ['#0f0', '#ff0', '#f00', '#00f'],
      size: [20, 50, 35, 10],
      sizeref: 0.2,
    },
  },
];

const chartData = ref(chartDataRaw);

// 使用自定义钩子
const { updateChart } = useECharts(chartRef, chartData);

function changeEcharts() {
  chartData.value = [
    {
      x: [10, 50, 50, 10],
      y: [1, 1, 5, 5],
      marker: {
        color: ['#0f0', '#ff0', '#f00', '#00f'],
        size: [20, 50, 35, 10],
        sizeref: 0.2,
      },
    },
  ];
  updateChart()
}

</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 400px;
}
</style>