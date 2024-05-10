<template>
  <div class="form-container">
    <el-form :model="formData" class="mx-auto max-w-6xl">
      <div class="flex justify-between mb-2">
        <div class="w-1/5 mx-2">
          <el-form-item label="城市数量:">
            <el-input-number v-model="formData.IS" :min="1" placeholder="请输入" />
          </el-form-item>
        </div>
        <div class="w-1/5 mx-2">
          <el-form-item label="场景数量:">
            <el-input-number v-model="formData.NS" :min="1" placeholder="请输入" />
          </el-form-item>
        </div>
        <div class="w-3/10 mx-2">
          <el-form-item label="两阶段样本数:">
            <el-input-number v-model="formData.MS" :min="1" :max="formData.NS" placeholder="请输入" />
          </el-form-item>
        </div>
        <div class="w-3/10 mx-2">
          <el-form-item label="样本场景个数:">
            <el-input-number v-model="formData.SS_SAA" :min="1" :max="getMaxSS_SAA" placeholder="请输入" />
          </el-form-item>
        </div>
      </div>

      <div class="flex justify-between mb-2">
        <div class="w-full">
          <el-form-item label="数据处理方法:" class="w-full">
            <el-select v-model="formData.data_process_methods" multiple placeholder="请选择">
              <el-option v-for="item in data_process_options" :key="item.value" :label="item.label"
                :value="item.value"></el-option>
            </el-select>
          </el-form-item>
        </div>
      </div>

      <div class="flex justify-between mb-2">
        <div class="w-full">
          <el-form-item label="场景聚类方法:" class="w-full">
            <el-select v-model="formData.cluster_methods" multiple placeholder="请选择">
              <el-option v-for="item in cluster_options" :key="item.value" :label="item.label"
                :value="item.value"></el-option>
            </el-select>
          </el-form-item>
        </div>
      </div>

      <div class="flex justify-between mb-2">
        <div class="w-3/8">
          <el-form-item label="样本生成方法:">
            <el-select v-model="formData.sample_generate_methods" multiple placeholder="请选择">
              <el-option v-for="item in sample_generate_options" :key="item.value" :label="item.label"
                :value="item.value"></el-option>
            </el-select>
          </el-form-item>
        </div>
        <div class="w-3/8">
          <el-form-item label="可视化维度:">
            <el-select v-model="formData.graph_methods" multiple placeholder="请选择">
              <el-option v-for="item in graph_options" :key="item.value" :label="item.label"
                :value="item.value"></el-option>
            </el-select>
          </el-form-item>
        </div>
        <div class="w-1/5">
          <el-form-item label="最大尝试次数:">
            <el-input-number v-model="formData.max_attempts" :min="1"></el-input-number>
          </el-form-item>
        </div>
        <div class="w-1/6">
          <el-form-item label="计算次数:">
            <el-input-number v-model="formData.calculate_epoch" :min="1"></el-input-number>
          </el-form-item>
        </div>
      </div>

      <div class="flex justify-evenly w-full mb-4">
        <el-button type="primary" @click="sendParameters">提交</el-button>
        <el-button type="success" @click="calculateGurobiOpt">Gurobi求解器精确值求解</el-button>
        <el-button type="info" @click="runSolver">SAA算法近似求解</el-button>
      </div>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import axios from 'axios';
import { useResultsStore } from '@/store/resultsStore';
import { useImagesStore } from '@/store/graphsStore';
import { useEchartsStore } from '@/store/echartsStore';
import { useParameterStore } from '@/store/parameterStore';



defineProps([])

// const emit = defineEmits(['parameters-updated']);

const resultsStore = useResultsStore();
const imagesStore = useImagesStore();
const echartsStore = useEchartsStore();
const parameterStore = useParameterStore();

// const formData = ref({
//   IS: 20,
//   NS: 100,
//   MS: 10,
//   SS_SAA: 10,
//   data_process_methods: ['truncated_svd'],
//   cluster_methods: ['som'],
//   sample_generate_methods: ['Stratified', 'Simple'],
//   graph_methods: ['3d', '2d'],
//   max_attempts: 2,
//   calculate_epoch: 1
// });
const formData = ref(parameterStore.$state);

const gurobiOpt = ref(null);

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

const graph_options = [
  { value: '2d', label: '2D' },
  { value: '3d', label: '3D' },
];

// 发送参数的方法
const sendParameters = async () => {
  try {
    updateParameters()
    console.log('Sending the following data to the server:', formData.value);
    const response = await axios.post('/api/send-parameters', formData.value);
    console.log('Server response:', response);
    ElMessage.success('参数更新成功！');
    parameterStore.updateParameters(formData.value);  // 更新 Pinia 存储
  } catch (error) {
    console.error('Error sending parameters:', error.response.data);
  }
};

const loading = ref(false);
// 定义一个变量来保存下一个通知的垂直偏移量
const notificationOffset = ref(0);

const runSolver = async () => {
  // let loadingInstance = ElLoading.service({
  //   lock: true,
  //   text: '正在使用SAA计算，请稍候...',
  //   background: 'rgba(255, 255, 255, 0.7)',
  // });

  try {
    notificationOffset.value = 0;
    ElMessage.success('已调用SAA求解该算例！可打开日志模块查看实时计算日志');
    const response = await axios.post('/api/run-solver');
    console.log(response.data);
    // 将结果存储到 Pinia
    response.data.results.forEach((result: any) => {
      resultsStore.addSAAResult({
        IS: formData.value.IS,
        NS: formData.value.NS,
        Vx: result.Vx,
        Vy: result.Vy,
        script_name: result.script_name,
        opt_f: result.opt_f,
        elapsed_time: result.elapsed_time,
      });
      imagesStore.fetchImages(result.graphs_dir_name);
    });
    response.data.results.forEach((result: any) => {
      ElNotification({
        title: `求解完成 - ${result.script_name} - Epoch: ${result.epoch}`,  // 添加epoch信息
        message: `计算时间：${result.elapsed_time}秒，与精确解的差别：${result.gap}，求得解值：${result.opt_f}`,
        type: 'success',
        duration: 0, // 设置为0则不会自动关闭
        showClose: true, // 显示关闭按钮
        position: 'top-left',
        offset: notificationOffset.value,
      });
      // 增加偏移量以避免下一个通知重叠
      notificationOffset.value += 150;
    });
  } catch (error) {
    ElNotification({
      title: '错误',
      message: 'SAA方法求解过程中发生错误',
      type: 'error',
      duration: 0, // 设置为0则不会自动关闭
      showClose: true, // 显示关闭按钮
      position: 'top-left',
      offset: notificationOffset.value,
    });
    // 增加偏移量以避免下一个通知重叠
    notificationOffset.value += 150;
    console.error(error);
  } finally {
    // loadingInstance.close();
  }
};

const calculateGurobiOpt = async () => {
  // let loadingInstance = ElLoading.service({
  //   lock: true,
  //   text: '正在计算精确解，请稍候...',
  //   background: 'rgba(255, 255, 255, 0.7)',
  // });

  try {
    ElMessage.success('已调用Gurobi求解该算例！可打开日志模块查看实时计算日志');
    const response = await axios.post('/api/calculate-gurobi-opt');
    console.log(response.data);
    const result = response.data.results[0]
    // 将结果存储到 Pinia
    resultsStore.addGurobiResult({
      IS: formData.value.IS,
      NS: formData.value.NS,
      Vx: result.Vx,
      Vy: result.Vy,
      script_name: result.script_name,
      opt_f: result.opt_f,
      elapsed_time: result.elapsed_time,
    });
    ElNotification({
      title: '精确算法求解结果',
      message: `求得解值：${result.opt_f}，求解时间：${result.elapsed_time}秒`,
      type: 'success',
      duration: 0, // 设置为0则不会自动关闭
      showClose: true, // 显示关闭按钮
      position: 'top-left',
      offset: 0,
    });
  } catch (error) {
    ElNotification({
      title: '错误',
      message: '精确算法求解过程中发生错误',
      type: 'error',
      duration: 0, // 设置为0则不会自动关闭
      showClose: true, // 显示关闭按钮
      position: 'top-left',
      offset: 0,
    });
    console.error(error);
  } finally {
    // loadingInstance.close();
  }
};

const updateParameters = () => {
  // emit('parameters-updated', { IS: formData.value.IS, NS: formData.value.NS });
  echartsStore.updateEchartsParams( { IS: formData.value.IS, NS: formData.value.NS });
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
