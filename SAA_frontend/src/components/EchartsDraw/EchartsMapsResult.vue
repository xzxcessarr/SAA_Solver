<template>
  <div class="flex justify-center w-full">
    <div class="w-full lg:max-w-6xl mx-auto p-2">
      <div class="h-96 border-2 border-gray-800 shadow-md">
        <div ref="chartRef" class="w-full h-full"></div>
      </div>
      <div class="mt-4">
        <label for="result-select" class="block text-sm font-medium text-gray-700">选择结果:</label>
        <select id="result-select" v-model="selectedResult" class="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
          <option v-for="(result, index) in allResults" :key="index" :value="result">
            {{ result.script_name }} - IS: {{ result.IS }}, NS: {{ result.NS }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, watchEffect, computed, onMounted, onUnmounted } from 'vue';
import { useECharts } from '@/hooks/useEchartsMapsResult';
import { useResultsStore } from '@/store/resultsStore';
import axios from 'axios';

const resultsStore = useResultsStore();

const allResults = computed(() => resultsStore.allResults);

const selectedResult = ref(allResults.value[0]);

const chartRef = ref<HTMLElement | null>(null);
const resourceData = computed(() => ({
  Vx: selectedResult.value?.Vx || [],
  Vy: selectedResult.value?.Vy || [],
}));

const coordinates = ref<number[][]>([]);

// Fetch coordinates
async function fetchCoordinates(numCities: number) {
  try {
    const response = await axios.get('/api/get-distance-matrix', {
      params: { num_cities: numCities }
    });
    coordinates.value = response.data.coordinates;
  } catch (error) {
    console.error('Failed to fetch coordinates:', error);
  }
}

const { initChart, createGraph, cleanup } = useECharts(chartRef, resourceData, coordinates);

// Ensure coordinates are fetched when selectedResult changes
watch(selectedResult, (newResult, oldResult) => {
  if (newResult.IS !== oldResult?.IS) {
    fetchCoordinates(newResult.IS);
  }
});

// Initialize ECharts instance and create graph when component is mounted
watchEffect(() => {
  initChart();
  if (coordinates.value.length > 0) {
    createGraph();
  }
});

onMounted(() => {
  if (selectedResult.value) {
    fetchCoordinates(selectedResult.value.IS);
  }
});

onUnmounted(() => {
  cleanup();
});
</script>