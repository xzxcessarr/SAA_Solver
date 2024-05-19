<template>
  <div class="app-container flex justify-center flex-col w-full">
    <el-header class="px-5 py-3 h-8 w-full content-center">
      <!-- 使用单选按钮组来替代步骤导航 -->
      <el-radio-group v-model="step" class="flex justify-center">
        <el-radio-button :label="1" class="step-button">数据选择</el-radio-button>
        <el-radio-button :label="2" class="step-button">参数设置</el-radio-button>
        <el-radio-button :label="3" class="step-button">计算结果</el-radio-button>
      </el-radio-group>
    </el-header>

    <!-- 主内容区域 -->
    <el-container class="flex w-full h-full">
      <el-main class="flex-grow h-full w-full">
        <router-view />
        <div v-show="showLogs" class="mt-4">
          <LogsWebSocket />
        </div>
      </el-main>
    </el-container>

    <!-- 控制面板和日志 -->
    <el-footer class="px-5 py-3 h-12">
      <div class="flex justify-center items-center space-x-4">
        <el-row >
          <el-switch v-model="showLogs" active-text="显示日志" inactive-text="隐藏日志"></el-switch>
        </el-row>
      </div>
    </el-footer>
    <p v-if="step < 4" class="text-center w-full mx-auto">&copy; 2024 SAA_Solver</p>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import emitter from '@/utils/emitter';
import LogsWebSocket from '@/components/LogsWebSocket.vue';

const step = ref(2);
const showLogs = ref(false);
const router = useRouter();


watch(step, (newValue) => {
  switch (newValue) {
    case 1:
      router.push({ name: 'DataConfig' });
      break;
    case 2:
      router.push({ name: 'ConfigSolver' });
      break;
    case 3:
      router.push({ name: 'ResultPage' });
      break;
  }
});


onMounted(() => {
  // 监听事件发射器的事件
  emitter.on('goToParameterSetup', () => {
    step.value = 2;
    router.push({ name: 'ConfigSolver' });
  });
});
</script>
