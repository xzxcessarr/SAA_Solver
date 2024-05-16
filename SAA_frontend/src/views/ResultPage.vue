<template>
    <div class="flex justify-center mb-5 w-full max-w-6xl mx-auto">
        <EchartsMapsResult />
    </div>
    <el-button @click="downloadResult"  type="primary">下载计算结果</el-button>
    <div class="flex justify-center mb-5 w-full max-w-6xl mx-auto">
        <ViewerComponent />
    </div>
</template>

<script setup lang="ts">
import ViewerComponent from '@/components/ViewerComponent.vue';
import EchartsMapsResult from '@/components/EchartsDraw/EchartsMapsResult.vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';


const downloadResult = async () => {
    try {
        const response = await axios.get(`/api/download-excel?file_type=${'result'}`, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', '计算结果.xlsx')
        document.body.appendChild(link)
        link.click()
      } catch (error) {
        ElMessage.error('下载失败')
      }
    }

</script>