<template>
  <div class="flex justify-center p-4">
    <el-scrollbar class="h-96 w-full bg-white text-black border border-black overflow-y-auto">
      <pre class="p-4 whitespace-pre-wrap break-words">{{ formattedLogs }}</pre>
    </el-scrollbar>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue';
import { ElScrollbar } from 'element-plus';

const logs = ref([]);
const maxLogCount = 10000;  // 设定最大显示日志条数

const ws = new WebSocket('ws://localhost:8000/ws/logs');
ws.onopen = function() {
    console.log('WebSocket connection established');
};

ws.onerror = function(event) {
    console.error('WebSocket Error:', event);
};

ws.onmessage = function(event) {
    console.log('WebSocket message received:', event.data);
};

ws.onclose = function(event) {
    console.log('WebSocket is closed now.', event);
};

ws.onmessage = function (event) {
  logs.value.push(event.data);
  if (logs.value.length > maxLogCount) {
    logs.value.shift();  // 移除最旧的日志以维持日志数组长度
  }
  // 确保滚动到最新的日志
  nextTick(() => {
    const scrollContainer = document.querySelector('.el-scrollbar__wrap');
    scrollContainer.scrollTop = scrollContainer.scrollHeight;
  });
};

const formattedLogs = computed(() => {
  return logs.value.join('\n');
});

onMounted(() => {
  ws.onopen = () => console.log('WebSocket connected.');
  ws.onerror = (error) => console.log('WebSocket Error: ' + error);
});

onUnmounted(() => {
  ws.close();
});
</script>
