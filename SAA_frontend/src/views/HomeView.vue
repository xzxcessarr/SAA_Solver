<template>
  <div class="app-container">
    <header class="app-header">
      <h1>数据分析与可视化</h1>
    </header>
    <main class="app-main">
      <el-form :model="formData" label-width="150px">
        <el-form-item label="IS_NS_MS_SS_SAA:">
          <el-select v-model="formData.IS_NS_MS_SS_SAA" multiple placeholder="请选择">
            <el-option v-for="item in IS_NS_MS_SS_SAA_options" :key="item.value" :label="item.label"
              :value="item.id"></el-option>
          </el-select>
        </el-form-item>
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
        <el-form-item label="降维方法:">
          <el-select v-model="formData.dim_reduction_methods" multiple placeholder="请选择">
            <el-option v-for="item in dim_reduction_options" :key="item.value" :label="item.label"
              :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="最大尝试次数:">
          <el-input-number v-model="formData.max_attempts" :min="1"></el-input-number>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm">提交</el-button>
        </el-form-item>
      </el-form>
      <div class="chart-container">
        <div id="chart"></div>
      </div>
      <div class="image-container">
        <img v-for="(imgUrl, index) in imgUrls" :key="index" :src="imgUrl" alt="Generated Image" />
      </div>
    </main>
    <footer class="app-footer">
      <p>&copy; 2023 数据分析与可视化. All rights reserved.</p>
    </footer>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { ElForm, ElFormItem, ElSelect, ElOption, ElInputNumber, ElButton } from 'element-plus';
import * as echarts from 'echarts';
import axios from 'axios';

export default defineComponent({
  name: 'App',
  components: {
    ElForm,
    ElFormItem,
    ElSelect,
    ElOption,
    ElInputNumber,
    ElButton,
  },
  setup() {
    const formData = ref({
      IS_NS_MS_SS_SAA: [] as string[],
      data_process_methods: [],
      cluster_methods: [],
      sample_generate_methods: [],
      dim_reduction_methods: [],
      max_attempts: 2,
    });

    const IS_NS_MS_SS_SAA_options = [
      { id: 'option1', value: [20, 100, 10, 10], label: 'IS=20, NS=100, MS=10, SS_SAA=10' },
      { id: 'option2', value: [20, 200, 10, 20], label: 'IS=20, NS=200, MS=10, SS_SAA=20' },
      { id: 'option3', value: [20, 500, 10, 25], label: 'IS=20, NS=500, MS=10, SS_SAA=25' },
      { id: 'option4', value: [40, 100, 10, 10], label: 'IS=40, NS=100, MS=10, SS_SAA=10' },
      { id: 'option5', value: [40, 200, 10, 20], label: 'IS=40, NS=200, MS=10, SS_SAA=20' },
      { id: 'option6', value: [40, 500, 10, 25], label: 'IS=40, NS=500, MS=10, SS_SAA=25' },
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

    const imgUrls = ref([]);

    const submitForm = async () => {
      formData.value.IS_NS_MS_SS_SAA = formData.value.IS_NS_MS_SS_SAA.map((selectedId) => {
        const selectedOption = IS_NS_MS_SS_SAA_options.find(option => option.id === selectedId);
        return selectedOption ? selectedOption.value : null;
      }).filter(v => v); // 过滤掉任何可能的null值
      try {
        console.log(formData.value)
        // 发送参数到服务器
        await axios.post('/parameters', formData.value);

        // 运行求解器
        const response = await axios.post('/run-solver');

        // 获取回调结果
        const callbackResponse = await axios.get('/solver-callback');
        imgUrls.value = [
          `${callbackResponse.data.graphs_sample_save_directory}/sample_image1.png`,
          `${callbackResponse.data.graphs_sample_save_directory}/sample_image2.png`,
          `${callbackResponse.data.graphs_cluster_save_directory}/cluster_image1.png`,
          `${callbackResponse.data.graphs_cluster_save_directory}/cluster_image2.png`,
        ];

        // 更新图表数据
        updateChart(response.data.result);
      } catch (error) {
        console.error('Error:', error);
      }
    };

    const updateChart = () => {
      if (!chartData.value) return;

      const chart = echarts.init(document.getElementById('chart') as HTMLElement);
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
              return chartData.value[0].marker.size[param.dataIndex] / chartData.value[0].marker.sizeref;
            },
            itemStyle: {
              color: function (param: any) {
                return chartData.value[0].marker.color[param.dataIndex];
              },
            },
            data: chartData.value[0].x.map(function (x: number, idx: number) {
              return [+x, +chartData.value[0].y[idx]];
            }),
          },
        ],
      };
      chart.setOption(option);
    };

    onMounted(() => {
      // 初始化ECharts实例
      const chart = echarts.init(document.getElementById('chart'));
    });

    return {
      formData,
      IS_NS_MS_SS_SAA_options,
      data_process_options,
      cluster_options,
      sample_generate_options,
      dim_reduction_options,
      imgUrls,
      submitForm,
    };
  },
});
</script>
