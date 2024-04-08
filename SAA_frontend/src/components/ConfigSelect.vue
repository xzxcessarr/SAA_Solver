<template>
  <div class="form-container">
    <el-form :model="formData" label-width="150px">
      <el-form-item label="IS:">
        <el-select v-model="formData.IS" placeholder="请选择">
          <el-option v-for="item in IS_options" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="NS:">
        <el-select v-model="formData.NS" placeholder="请选择">
          <el-option v-for="item in NS_options" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="MS:">
        <el-select v-model="formData.MS" placeholder="请选择">
          <el-option v-for="item in MS_options" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="SS_SAA:">
        <el-select v-model="formData.SS_SAA" placeholder="请选择">
          <el-option v-for="item in SS_SAA_options" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="数据处理方法:">
        <el-select v-model="formData.data_process_methods" multiple placeholder="请选择">
          <el-option v-for="item in data_process_options" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="聚类方法:">
        <el-select v-model="formData.cluster_methods" multiple placeholder="请选择">
          <el-option v-for="item in cluster_options" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="样本生成方法:">
        <el-select v-model="formData.sample_generate_methods" multiple placeholder="请选择">
          <el-option v-for="item in sample_generate_options" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="降维方法:">
        <el-select v-model="formData.dim_reduction_methods" multiple placeholder="请选择">
          <el-option v-for="item in dim_reduction_options" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="最大尝试次数:">
        <el-input-number v-model="formData.max_attempts" :min="1"></el-input-number>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="sendParameters">提交</el-button>
        <el-button type="primary" @click="runSolver">计算</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import {type IS_option_list} from '@/interfaces/index'

const emit = defineEmits(['formSubmitted']);

const formData = ref({
  IS: 20,
  NS: 100,
  MS: 10,
  SS_SAA: 10,
  data_process_methods: ['pca'],
  cluster_methods: ['kmeans'],
  sample_generate_methods: ['Stratified'],
  dim_reduction_methods: ['2d'],
  max_attempts: 2
});

const IS_options:IS_option_list = [
  { value: 20, label: 'IS=20' },
  { value: 40, label: 'IS=40' },
];

const NS_options = [
  { value: 100, label: 'NS=100' },
  { value: 200, label: 'NS=200' },
  { value: 500, label: 'NS=500' },
];

const MS_options = [
  { value: 10, label: 'MS=10' },
];

const SS_SAA_options = [
  { value: 10, label: 'SS_SAA=10' },
  { value: 20, label: 'SS_SAA=20' },
  { value: 25, label: 'SS_SAA=25' },
];

const data_process_options = [
  { value: 'pca', label: 'PCA' },
  { value: 'truncated_svd', label: 'Truncated SVD' },
  { value: 'none', label: 'None' },
];

const cluster_options = [
  { value: 'kmeans', label: 'K-Means' },
  { value: 'spectral', label: 'Spectral Clustering' },
  { value: 'gmm', label: 'Gaussian Mixture Model' },
  { value: 'som', label: 'Self-Organizing Map' },
];

const sample_generate_options = [
  { value: 'Stratified', label: 'Stratified' },
  { value: 'Simple', label: 'Simple' },
];

const dim_reduction_options = [
  { value: '2d', label: '2D' },
  { value: '3d', label: '3D' },
];

// 发送参数的方法
const sendParameters = async () => {
  try {
    console.log('Sending the following data to the server:', formData.value);
    const response = await axios.post('http://localhost:8000/parameters', formData.value);
    console.log('Server response:', response);
  } catch (error) {
    console.error('Error sending parameters:', error.response.data);
  }
};

// 文件上传的方法
const uploadFiles = async (inputFile) => {
  const formData = new FormData();
  formData.append('input_file', inputFile);

  try {
    const response = await axios.post('http://localhost:8000/data-files', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    console.log(response.data);
  } catch (error) {
    console.error(error);
  }
};

// 运行solver的方法
const runSolver = async () => {
  try {
    const response = await axios.post('http://localhost:8000/run-solver');
    console.log(response.data);
  } catch (error) {
    console.error(error);
  }
};
</script>