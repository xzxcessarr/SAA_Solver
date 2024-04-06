<template>
  <div>
    <el-form-item :label="label">
      <div class="method-grid">
        <div v-for="method in methods" :key="method.value" class="method-item" @click="selectMethod(method)">
          <img :src="method.imageUrl" alt="" class="method-image">
          <p class="method-text">{{ method.text }}</p>
        </div>
      </div>
    </el-form-item>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  label: String,
  value: String
});

const emits = defineEmits(['update:value']);

const methods = [
  {
    value: 'method1',
    imageUrl: '/src/assets/爱丽丝之神-02.jpg',
    text: '方法1'
  },
  {
    value: 'method2',
    imageUrl: '/src/assets/爱丽丝之神-02.jpg',
    text: '方法2'
  },
  // 更多方法...
];

const selectMethod = (method) => {
  emits('update:value', method.value);
  // 此处应该有跳转逻辑，使页面跳转到显示方法详细信息的地方
};

</script>

<style scoped>
.method-grid {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
}
.method-item {
  cursor: pointer;
  text-align: center;
  margin: 10px;
}
```css
.method-image {
  width: 100px; /* 根据需要调整图片大小 */
  height: auto;
}
.method-text {
  margin-top: 8px;
  font-size: 14px; /* 根据需要调整文字大小 */
}
</style>