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
import { defineComponent, onMounted, ref } from 'vue';

export default defineComponent({
  name: 'ViewerComponent',
  setup() {
    const imageUrls = ref([
      // 这里放置图片URL
      '/src/assets/爱丽丝之神-02.jpg',
      '/src/assets/爱丽丝之神-02.jpg',
      '/src/assets/爱丽丝之神-02.jpg',
      '/src/assets/爱丽丝之神-02.jpg',
      '/src/assets/爱丽丝之神-02.jpg',
      '/src/assets/爱丽丝之神-02.jpg',
    ]);

    onMounted(() => {
    });

    return {
      imageUrls
    };
  },
});
</script>


<style scoped>
.cluster-sample {
  display: flex;
  flex-wrap: nowrap; /* 防止内容换行 */
  overflow-x: auto;  /* 当内容超出时，可以横向滚动 */
  gap: 10px;        /* 图片之间的间隔 */
  padding: 10px 0;  /* 上下的内边距 */
}

.view-box {
  width: 200px;    /* 设置缩略图的宽度 */
  height: auto;    /* 高度自动，保持图片比例 */
  cursor: pointer; /* 鼠标悬停时显示手型指针 */
  object-fit: cover;
  flex: 0 0 auto; /* flex-grow: 0, flex-shrink: 0, flex-basis: auto */
  height: 100%;   /* 图片高度填充父容器高度 */
  object-fit: cover; /* 或者使用 'contain' 以保持图片的比例 */
}

</style>