<!-- 
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Cluster and Sample View.

Author: cessarr
Date Created: 2024-05-19
License: MIT License

Description:
------------
此组件用于查看抽样和聚类数据点数据。 
-->

<template>
  <div>
    <el-select v-model="currentDir" placeholder="请选择目录" @change="updateImages">
      <el-option
        v-for="dir in Object.keys(imagesStore.imagesByDir)"
        :key="dir"
        :label="dir"
        :value="dir">
      </el-option>
    </el-select>

    <!-- 群集图片行 -->
    <el-row justify="space-evenly">
      <div class="flex flex-nowrap overflow-x-auto space-x-2.5 py-2.5">
        <photo-provider>
          <photo-consumer v-for="src in currentClusterImages" :key="src" :src="src">
            <img :src="src" class="w-48 h-auto cursor-pointer object-cover flex-shrink-0 shadow-lg">
          </photo-consumer>
        </photo-provider>
      </div>
    </el-row>

    <!-- 样本图片行 -->
    <el-row justify="space-evenly">
      <div class="flex flex-nowrap overflow-x-auto space-x-2.5 py-2.5">
        <photo-provider>
          <photo-consumer v-for="src in currentSampleImages" :key="src" :src="src">
            <img :src="src" class="w-48 h-auto cursor-pointer object-cover flex-shrink-0 shadow-lg">
          </photo-consumer>
        </photo-provider>
      </div>
    </el-row>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, watch, onMounted, computed } from 'vue';
import { useImagesStore } from '@/store/graphsStore';

export default defineComponent({
  name: 'ViewerComponent',
  setup() {
    const imagesStore = useImagesStore();
    const currentDir = ref('Default');

    // 组件挂载时获取初始图片
    onMounted(() => {
      if (!imagesStore.imagesByDir[currentDir.value]) {
        imagesStore.fetchImages(currentDir.value);
      }
    });

    const updateImages = () => {
      imagesStore.fetchImages(currentDir.value);
    };

    // 使用 watchEffect 监听 currentDir 的变化
    watch(currentDir, () => {
      if (!imagesStore.imagesByDir[currentDir.value]) {
        updateImages();
      }
    });

    // 创建计算属性以便实时更新图片
    const currentClusterImages = computed(() => imagesStore.imagesByDir[currentDir.value]?.clusterImages || []);
    const currentSampleImages = computed(() => imagesStore.imagesByDir[currentDir.value]?.sampleImages || []);

    return {
      currentDir,
      imagesStore,
      currentClusterImages,
      currentSampleImages,
      updateImages,
    };
  },
});
</script>
