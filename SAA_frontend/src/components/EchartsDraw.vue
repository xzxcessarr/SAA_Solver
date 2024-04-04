<template>
  <div class="chart-container">
    <div ref="chartRef" :style="{ width: '100%', height: '400px' }"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as echarts from 'echarts/core';
import { ScatterChart } from 'echarts/charts';
import { TitleComponent, TooltipComponent, AxisPointerComponent, GridComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([TitleComponent, TooltipComponent, AxisPointerComponent, GridComponent, ScatterChart, CanvasRenderer]);

const props = defineProps<{
  formSubmitted: boolean;
}>();

const chartRef = ref<HTMLElement | null>(null);
let chart: echarts.ECharts | null = null;

const updateChart = () => {
  if (!chart) {
    return;
  }

  const chartData = [
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

  const option = {
    title: {
      text: 'Master Painter Color Choices Throughout History',
      subtext: 'Data From Plot.ly',
      left: 'right',
    },
    xAxis: {
      type: 'value',
      splitLine: {
        show: false,
      },
      scale: true,
      splitNumber: 5,
      max: 'dataMax',
      axisLabel: {
        formatter: function (val: number) {
          return val + 's';
        },
      },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 360,
      interval: 60,
      name: 'Hue',
      splitLine: {
        show: false,
      },
    },
    series: [
      {
        name: 'scatter',
        type: 'scatter',
        symbolSize: function (val: number, param: any) {
          return chartData[0].marker.size[param.dataIndex] / chartData[0].marker.sizeref;
        },
        itemStyle: {
          color: function (param: any) {
            return chartData[0].marker.color[param.dataIndex];
          },
        },
        data: chartData[0].x.map(function (x: number, idx: number) {
          return [+x, +chartData[0].y[idx]];
        }),
      },
    ],
  };

  chart.setOption(option);
};

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value);
    updateChart();

    window.addEventListener('resize', () => {
      if (chart) {
        chart.resize();
      }
    });
  }
});

watch(
  () => props.formSubmitted,
  (newVal) => {
    if (newVal) {
      updateChart();
    }
  }
);
</script>

<style scoped>
.chart-container {
  width: 200%;
  height: 500px;
}
</style>