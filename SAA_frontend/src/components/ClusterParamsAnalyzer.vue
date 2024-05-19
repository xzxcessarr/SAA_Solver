<!-- 
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Parameter Analysis.

Author: cessarr
Date Created: 2024-05-19
License: MIT License

Description:
------------
此组件用于分析最优参数，后端接口暂未完善，请勿直接调用。 
-->
<template>
  <div class="config-form flex flex-col items-center justify-center p-5">
    <!-- <h2 class="text-xl font-bold mb-4">Configuration Parameters</h2> -->
    <el-form :model="configData" class="w-full max-w-xl">

      <el-form-item label="Data Processor Method">
        <el-select v-model="dataProcessorMethod" placeholder="Select a method">
          <el-option v-for="method in dataProcessorMethods" :key="method.value" :label="method.label"
            :value="method.value"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="variance_ratio">
        <el-input-number v-model="configData.variance_ratio" :step="0.01"></el-input-number>
      </el-form-item>

      <el-form-item>
        <el-collapse v-model="activeNames">
          <el-collapse-item :title="key" :name="key" v-for="(value, key) in configData.CLUSTER_PARAMS" :key="key">
            <el-form-item :label="param" v-for="(paramValue, param) in value" :key="param">
              <el-input v-model.number="configData.CLUSTER_PARAMS[key][param]"></el-input>
            </el-form-item>
            <el-button type="primary" @click="analyzeBestParams(key)">Analyze</el-button>
          </el-collapse-item>
        </el-collapse>
      </el-form-item>

      <el-form-item label="GRAPH_PROCESS_METHOD">
        <el-select v-model="configData.GRAPH_PROCESS_METHOD" placeholder="请选择">
          <el-option label="T-SNE可视化聚类" value="tsne"></el-option>
          <el-option label="PCB可视化聚类" value="pca"></el-option>
        </el-select>
      </el-form-item>

      <!-- <el-form-item label="n_clusters">
        <el-input-number v-model="configData.n_clusters"></el-input-number>
      </el-form-item> -->

      <el-form-item label="Water_index">
        <el-input-number v-model="configData.Water_index"></el-input-number>
      </el-form-item>

      <el-form-item label="Food_index">
        <el-input-number v-model="configData.Food_index" :step="0.01"></el-input-number>
      </el-form-item>

      <el-form-item label="Medicine_index">
        <el-input-number v-model="configData.Medicine_index" :step="0.01"></el-input-number>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="updateConfig">Update Config</el-button>
        <el-button @click="resetConfig">Reset Config</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';
import { useParameterStore } from '@/store/parameterStore';
import 'element-plus/dist/index.css';

// 使用 ParameterStore
const parameterStore = useParameterStore();

// 定义响应式数据
const configData = ref({
  CLUSTER_PARAMS: {},
  GRAPH_PROCESS_METHOD: '',
  Water_index: 0,
  Food_index: 0,
  Medicine_index: 0,
  variance_ratio: 0,
});

const activeNames = ref([]);
const dataProcessorMethod = ref('truncated_svd');

const dataProcessorMethods = ref([
  { value: 'pca', label: 'PCA' },
  { value: 'truncated_svd', label: 'Truncated SVD' },
  { value: 'factor_analysis', label: 'Factor Analysis' },
  { value: 'none', label: 'None' },
]);

// 定义异步函数
const getConfig = async () => {
  try {
    const response = await axios.get('/api/get-config');
    configData.value = response.data;
  } catch (error) {
    console.error('Error fetching config:', error);
  }
};

const updateConfig = async () => {
  try {
    console.log(configData.value);
    await axios.post('/api/update-config', configData.value);
    ElMessage.success('Configuration updated successfully');
  } catch (error) {
    console.error('Error updating config:', error);
    ElMessage.error('Failed to update configuration');
  }
};

const resetConfig = async () => {
  try {
    await axios.post('/api/reset-config');
    const response = await axios.get('/api/get-config');
    configData.value = response.data;
    ElMessage.success('Configuration reset successfully');
  } catch (error) {
    console.error('Error resetting config:', error);
    ElMessage.error('Failed to reset configuration');
  }
};

const analyzeBestParams = async (clusterMethod: string) => {
  try {
    const response = await axios.get('/api/analyze-clustering-params', {
      params: {
        cluster_method: clusterMethod,
        data_processor_method: dataProcessorMethod.value,
        IS: parameterStore.IS,
        NS: parameterStore.NS,
      },
    });
    const bestParams = response.data.best_params;
    const bestParamsRange = response.data.best_params_range;

    // Construct a VNode message
    const messageContent = [
      h('p', null, `Recommended parameters for ${clusterMethod}: `),
      ...Object.entries(bestParamsRange).map(([key, range]) =>
        h('p', { style: 'margin-bottom: 5px;' }, [
          `${key}: `,
          h('span', { style: 'font-weight: bold;' }, range),
          ` (Current Best: ${bestParams[key]})`
        ])
      )
    ];

    ElMessage({
      message: h('div', null, messageContent),
      type: 'success',
      duration: 10000,
      showClose: true,
    });
  } catch (error) {
    console.error('Error analyzing best parameters:', error);
    ElMessage.error('Failed to analyze best parameters, Please check whether you have submitted the calculation example parameters');
  }
};


onMounted(getConfig);

</script>
