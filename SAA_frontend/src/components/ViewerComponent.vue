<!-- <template>
  <div>
    <el-row justify="space-evenly">
      <div class="flex flex-nowrap overflow-x-auto space-x-2.5 py-2.5">
        <photo-provider>
          <photo-consumer v-for="src in clusterImages" :key="src" :src="src">
            <img :src="src" class="w-48 h-auto cursor-pointer object-cover flex-shrink-0 shadow-lg">
          </photo-consumer>
        </photo-provider>
      </div>
    </el-row>
    <el-row justify="space-evenly">
      <div class="flex flex-nowrap overflow-x-auto space-x-2.5 py-2.5">
        <photo-provider>
          <photo-consumer v-for="src in sampleImages" :key="src" :src="src">
            <img :src="src" class="w-48 h-auto cursor-pointer object-cover flex-shrink-0 shadow-lg">
          </photo-consumer>
        </photo-provider>
      </div>
    </el-row>
  </div>
</template>


<script lang="ts">
import { defineComponent, onMounted, ref, type Ref, watch } from 'vue';
import axios from 'axios';

export default defineComponent({
  name: 'ViewerComponent',
  props: {
    dirName: {
      type: String,
      default: 'Default',
    },
  },
  setup(props) {
    const sampleImages: Ref<string[]> = ref([]);
    const clusterImages: Ref<string[]> = ref([]);

    // 获取图片列表并更新
    const fetchImages = async () => {
      try {
        const sampleResponse = await axios.get(`/api/get_sample_images?dir_name=${props.dirName}`);
        sampleImages.value = sampleResponse.data.sample_images;

        const clusterResponse = await axios.get(`/api/get_cluster_images?dir_name=${props.dirName}`);
        clusterImages.value = clusterResponse.data.cluster_images;
        console.log(sampleImages.value)
      } catch (error) {
        console.error('An error occurred while fetching images:', error);
      }
    };  

    // 每当 dirName 更改时，重新获取图像列表
    watch(() => props.dirName, fetchImages, { immediate: true });

    return {
      sampleImages,
      clusterImages,
      fetchImages,
    };
  },
});
</script> -->

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
