<!-- <template>
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
        <el-button type="primary" @click="submitForm">提交</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElForm, ElFormItem, ElSelect, ElOption, ElInputNumber, ElButton } from 'element-plus';
import axios from 'axios';
import {type IS_option_list} from '@/interfaces/index'

const emit = defineEmits(['formSubmitted']);

const formData = ref({
  IS: '',
  NS: '',
  MS: '',
  SS_SAA: '',
  data_process_methods: [] as string[],
  cluster_methods: [] as string[],
  sample_generate_methods: [] as string[],
  dim_reduction_methods: [] as string[],
  max_attempts: 2,
});

const IS_options:IS_option_list = [
  { value: '20', label: 'IS=20' },
  { value: '40', label: 'IS=40' },
];

const NS_options = [
  { value: '100', label: 'NS=100' },
  { value: '200', label: 'NS=200' },
  { value: '500', label: 'NS=500' },
];

const MS_options = [
  { value: '10', label: 'MS=10' },
];

const SS_SAA_options = [
  { value: '10', label: 'SS_SAA=10' },
  { value: '20', label: 'SS_SAA=20' },
  { value: '25', label: 'SS_SAA=25' },
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

const submitForm = async () => {
  try {
    // 发送参数到服务器
    await axios.post('/parameters', formData.value);

    // 触发formSubmitted事件,通知父组件表单已提交
    emit('formSubmitted');
  } catch (error) {
    console.error('Error:', error);
  }
};
</script> -->

<template>
  <div class="config-select-container">
    <!-- 行内排列的表单字段 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-form-item label="IS:">
          <el-select v-model="formData.IS" placeholder="请选择IS">
            <!-- 这里添加选项 -->
            <el-option
              v-for="item in ISOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="6">
        <el-form-item label="NS:">
          <el-select v-model="formData.NS" placeholder="请选择NS">
            <!-- 这里添加选项 -->
            <el-option
              v-for="item in NSOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="6">
        <el-form-item label="MS:">
          <el-select v-model="formData.MS" placeholder="请选择MS">
            <!-- 这里添加选项 -->
            <el-option
              v-for="item in MSOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
      </el-col>
      <el-col :span="6">
        <el-form-item label="SS_SAA:">
          <el-select v-model="formData.SS_SAA" placeholder="请选择SS_SAA">
            <!-- 这里添加选项 -->
            <el-option
              v-for="item in SS_SAAOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
      </el-col>
    </el-row>
    <!-- 图片选择的方法 -->
    <method-selector label="数据处理方法" v-model="formData.dataProcessingMethod" :options="dataProcessingOptions"></method-selector>
    <method-selector label="聚类方法" v-model="formData.clusteringMethod" :options="clusteringOptions"></method-selector>
    <method-selector label="样本生成方法" v-model="formData.sampleGenerationMethod" :options="sampleGenerationOptions"></method-selector>
    <!-- 最大尝试次数的表单字段 -->
    <el-form-item label="最大尝试次数:">
      <el-input-number v-model="formData.maxAttempts" :min="1"></el-input-number>
    </el-form-item>
    <!-- 提交按钮 -->
    <el-form-item>
      <el-button type="primary" @click="submitForm">提交</el-button>
    </el-form-item>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import MethodSelector from './MethodSelect.vue';

// 假设这些选项是您希望用户从中选择的
const ISOptions = [{ value: 'option1', label: '选项1' }, /* ...更多选项 */];
const NSOptions = [{ value: 'option2', label: '选项2' }, /* ...更多选项 */];
const MSOptions = [{ value: 'option3', label: '选项3' }, /* ...更多选项 */];
const SS_SAAOptions = [{ value: 'option4', label: '选项4' }, /* ...更多选项 */];

// 方法选择器的选项
const dataProcessingOptions = [{ imageUrl: 'url1', text: '处理方法1' }, /* ...更多选项 */];
const clusteringOptions = [{ imageUrl: 'url2', text: '聚类方法1' }, /* ...更多选项 */];
const sampleGenerationOptions = [{ imageUrl: 'url3', text: '生成方法1' }, /* ...更多选项 */];

const formData = reactive({
  IS: '',
  NS: '',
  MS: '',
  SS_SAA: '',
  dataProcessingMethod: '',
  clusteringMethod: '',
  sampleGenerationMethod: '',
  maxAttempts: 1
});

const submitForm = () => {
  // 提交表单的逻辑
  console.log('Form submitted:', formData);
};
</script>

<style scoped>
.config-select-container {
  /* 样式定义 */
  max-width: 960px;
  margin: 0 auto;
}

.el-form-item {
  margin-bottom: 20px;
}

.el-row {
  margin-bottom: 20px;
}
</style>