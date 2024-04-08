<template>
  <div class="form-container">
    <el-form :model="formData" label-width="150px">
      <el-row>
        <el-col :span="6">
          <el-form-item label="城市数量:">
        <el-select v-model="formData.IS" placeholder="请选择">
          <el-option v-for="item in IS_options" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="场景数量:">
        <el-select v-model="formData.NS" placeholder="请选择">
          <el-option v-for="item in NS_options" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>

      </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="两阶段样本数:">
        <el-input-number v-model="formData.MS" :min="1" :max="formData.NS" placeholder="请输入" />
      </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="样本场景个数:">
        <el-input-number v-model="formData.SS_SAA" :min="1" :max="getMaxSS_SAA" placeholder="请输入" />
      </el-form-item>
        </el-col>
      </el-row>
  <el-form-item label="数据处理方法:">
        <el-select v-model="formData.data_process_methods" multiple placeholder="请选择">
          <el-option v-for="item in data_process_options" :key="item.value" :label="item.label"
            :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="聚类方法:">
        <el-select v-model="formData.cluster_methods" multiple placeholder="请选择">
          <el-option v-for="item in cluster_options" :key="item.value" :label="item.label"
            :value="item.value"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="样本生成方法:">
        <el-select v-model="formData.sample_generate_methods" multiple placeholder="请选择">
          <el-option v-for="item in sample_generate_options" :key="item.value" :label="item.label"
            :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="可视化维度:">
        <el-select v-model="formData.dim_reduction_methods" multiple placeholder="请选择">
          <el-option v-for="item in dim_reduction_options" :key="item.value" :label="item.label"
            :value="item.value"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="最大尝试次数:">
        <el-input-number v-model="formData.max_attempts" :min="1"></el-input-number>
      </el-form-item>
        <el-button type="primary" @click="sendParameters">提交</el-button>
        <el-button type="primary" @click="runSolver">计算</el-button>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed,watch} from 'vue';
import axios from 'axios';
import { type IS_option_list } from '@/interfaces/index'

const emit = defineEmits(['formSubmitted']);

const formData = ref({
  IS: 20,
  NS: 100,
  MS: 10,
  SS_SAA: 10,
  data_process_methods: ['truncated_svd'],
  cluster_methods: ['som'],
  sample_generate_methods: ['Stratified'],
  dim_reduction_methods: ['3d'],
  max_attempts: 2
});

const IS_options: IS_option_list = [
  { value: 20, label: 'IS=20' },
  { value: 40, label: 'IS=40' },
];

const NS_options = [
  { value: 100, label: 'NS=100' },
  { value: 200, label: 'NS=200' },
  { value: 500, label: 'NS=500' },
];

const data_process_options = [
  { value: 'pca', label: '(稠密)PCA' },
  { value: 'truncated_svd', label: '(稀疏)Truncated SVD' },
  { value: 'factor_analysis', label: 'Factor Analysis' },
  // { value: 'tsne', label: 't-SNE' }, // t-SNE 仅用于可视化降维，不推荐用于聚类前的降维
  { value: 'none', label: 'None' },
];

const cluster_options = [
  { value: 'som', label: '(精度最优)Self-Organizing Map' },
  { value: 'kmeans', label: '(时间最优)K-Means++' },
  { value: 'spectral', label: '(小样本推荐)Spectral Clustering' },
  { value: 'gmm', label: '(大算例配合SVD)Gaussian Mixture Model' },
  { value: 'optics', label: 'OPTICS' },
  { value: 'meanshift', label: 'Mean Shift' },
  { value: 'dbscan', label: 'DBSCAN' },
  { value: 'agglomerative', label: 'Agglomerative Clustering' },
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

const getMaxSS_SAA = computed(() => {
  return formData.value.NS / formData.value.MS || formData.value.NS;
});

// Watchers to make sure MS * SS_SAA <= NS
watch(() => formData.value.MS, (newMS) => {
  if (newMS * formData.value.SS_SAA > formData.value.NS) {
    formData.value.SS_SAA = null;
  }
});

watch(() => formData.value.SS_SAA, (newSS_SAA) => {
  if (newSS_SAA * formData.value.MS > formData.value.NS) {
    formData.value.MS = null;
  }
});
</script>

<style scoped>
/* 自定义多选框的样式 */
.el-checkbox__input {
  /* 放大多选框 */
  transform: scale(1.5);
  /* 增加外间距，以防止元素紧挨在一起 */
  margin-right: 5px;
}

/* 可能需要调整标签与多选框的垂直对齐方式 */
.el-checkbox__label {
  line-height: 1.5em;
  /* 调整这个值以垂直居中文本 */
}

/* 如果使用的是 el-select 多选框，可能还需要调整 el-select 的样式 */
.el-select .el-input__inner {
  height: auto;
  /* 调整输入框的高度 */
  min-height: 36px;
  /* 设置最小高度以适应放大的多选框 */
}
</style>