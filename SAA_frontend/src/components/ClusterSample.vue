<template>
  <div class="cluster-sample">
    <div v-for="(imgUrl, index) in displayedImgUrls" :key="index" class="image-wrapper">
      <el-image
        :src="imgUrl"
        fit="cover"
        :preview-src-list="displayedImgUrls"
        :initial-index="index"
        :hide-on-click-modal="true"
        :close-on-press-escape="true"
      >
        <template #placeholder>
          <div class="image-slot">
            <el-icon><icon-picture /></el-icon>
          </div>
        </template>
        <template #error>
          <div class="image-slot">
            <el-icon><icon-picture /></el-icon>
          </div>
        </template>
      </el-image>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElImage } from 'element-plus';
import { Picture as IconPicture } from '@element-plus/icons-vue';
import defaultImg from '@/assets/爱丽丝之神-02.jpg';

const defaultImgUrls = [
  defaultImg,
  defaultImg,
  defaultImg,
  defaultImg,
];

const onlineImgUrls = [
  'https://gitee.com/swjtuai/agvc/raw/agvc-test/test1-230810.png',
  'https://gitee.com/swjtuai/agvc/raw/agvc-test/test2-230810.png',

  'https://gitee.com/swjtuai/agvc/raw/agvc-test/test1-230810.png',
  'https://gitee.com/swjtuai/agvc/raw/agvc-test/test2-230810.png',
];

const displayedImgUrls = ref<string[]>([...defaultImgUrls, ...onlineImgUrls]);

// const fetchImages = async () => {
//   try {
//     const response = await axios.get('/solver-callback');
//     const sampleImages = [
//       `${response.data.graphs_sample_save_directory}/sample_image1.png`,
//       `${response.data.graphs_sample_save_directory}/sample_image2.png`,
//     ];
//     const clusterImages = [
//       `${response.data.graphs_cluster_save_directory}/cluster_image1.png`,
//       `${response.data.graphs_cluster_save_directory}/cluster_image2.png`,
//     ];
//     imgUrls.value = [...sampleImages, ...clusterImages];
//   } catch (error) {
//     console.error('Error fetching images:', error);
//   }
// };

// onMounted(() => {
//   fetchImages();
// });

// watch(imgUrls, (newUrls) => {
//   if (newUrls.length > 0) {
//     displayedImgUrls.value = newUrls;
//   }
// });
</script>

<style scoped>
.cluster-sample {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: center;
}

.image-wrapper {
  width: 200px;
  height: 200px;
  border: 1px solid #ccc;
  padding: 10px;
  box-sizing: border-box;
}

.image-wrapper .el-image {
  width: 100%;
  height: 100%;
}

.image-slot {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
  color: #909399;
  font-size: 30px;
}
</style>