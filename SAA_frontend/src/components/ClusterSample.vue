<template>
  <div class="cluster-sample">
    <photo-provider>
      <photo-consumer v-for="src in imageUrls" :intro="src" :key="src" :src="src">
        <img :src="src" class="view-box">
      </photo-consumer>
    </photo-provider>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
// 确保引入v-viewer组件
import 'viewerjs/dist/viewer.css';
import VueViewer from 'v-viewer';

export default defineComponent({
  name: 'ViewerComponent',
  setup() {
    const imageUrls = ref([
      // 这里放置图片URL
      '/src/assets/爱丽丝之神-02.jpg',
      '/src/assets/爱丽丝之神-02.jpg',
      '/src/assets/爱丽丝之神-02.jpg',
    ]);

    return {
      imageUrls
    };
  },
});
</script>

<style scoped>
.cluster-sample {
  display: flex;
  flex-wrap: wrap; /* 允许内容换行 */
  gap: 10px;       /* 图片之间的间隔 */
}

.view-box {
  width: 100px;    /* 设置缩略图的宽度 */
  height: auto;    /* 高度自动，保持图片比例 */
  cursor: pointer; /* 鼠标悬停时显示手型指针 */
  object-fit: cover;
}

</style>