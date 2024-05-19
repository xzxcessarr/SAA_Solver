<!-- 
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Data Upload.

Author: cessarr
Date Created: 2024-05-19
License: MIT License

Description:
------------
此组件用于上传用户的Excel文件，需要参照模板文件编写数据。 
-->
<template>
  <div class="mt-5 max-w-6xl mx-auto p-5">
    <div class="border border-gray-200 rounded shadow">
      <div class="p-4">
        <span>上传并预览Excel文件</span>
        <hr class="my-2">
        <el-upload
          ref="uploadRef"
          class="upload-excel mt-5"
          :action="'/api/upload-data-files'"
          :headers="{'Authorization': 'Bearer ' + authToken}"
          :on-success="handleSuccess"
          :on-error="handleError"
          :before-upload="beforeUpload"
          :on-preview="handlePreview"
          :on-remove="handleRemove"
          :file-list="fileList"
          :auto-upload="false"
          multiple
          accept=".xls, .xlsx"
        >
          <el-button type="warning">选择文件</el-button>
          <div slot="tip" class="text-sm text-gray-600 mt-1">只支持.xls和.xlsx文件</div>
        </el-upload>
        <el-button @click="submitUpload" type="success" class="mt-2">确认上传</el-button>
        <el-button type="primary" @click="downloadDefaultData" class="mt-2">下载默认数据结构</el-button>
      </div>
      <el-drawer
        v-model="drawerVisible"
        title="预览数据"
        size="50%"
        :before-close="handleDrawerClose"
      >
        <el-select v-model="selectedSheet" @change="fetchSheetData" class="w-full mt-2">
          <el-option v-for="sheet in sheetNames" :key="sheet" :label="sheet" :value="sheet" />
        </el-select>
        <el-table v-loading="loading" :data="excelData" class="w-full">
          <el-table-column v-for="header in headers" :key="header" :prop="header" :label="header" />
        </el-table>
      </el-drawer>
    </div>
  </div>
</template>
<script>
import { ref, reactive } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';

export default {
  setup() {
    const uploadRef = ref(null);
    const drawerVisible = ref(false);
    const excelData = ref([]);
    const headers = ref([]);
    const sheetNames = ref([]);
    const selectedSheet = ref('');
    const fileList = ref([]);
    const loading = ref(false);
    const authToken = ref('your_token_here'); // Adjust based on your auth method

    const beforeUpload = file => {
      const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || file.type === 'application/vnd.ms-excel';
      if (!isExcel) {
        ElMessage.error('只能上传Excel文件!');
        return false;
      }
      return true;
    };

    const handlePreview = file => {
      console.log('Preview file:', file);
    };

    const handleRemove = (file, fileList) => {
      console.log('Removed file:', file);
    };

    const handleSuccess = (response, file) => {
      ElMessage.success('文件上传成功！');
      drawerVisible.value = true;
      sheetNames.value = response.sheetNames; // Assume API response contains sheet names
      selectedSheet.value = sheetNames.value[0];
      fetchSheetData();
    };

    const handleError = error => {
      console.error('Upload error:', error);
      ElMessage.error('文件上传失败！');
    };

    const submitUpload = () => {
      if (uploadRef.value) {
        uploadRef.value.submit();
      }
    };

    const fetchSheetData = async () => {
      if (!selectedSheet.value) return;
      loading.value = true;
      try {
        const response = await axios.get(`/api/get-sheet-data?sheetName=${selectedSheet.value}`);
        excelData.value = response.data.data;
        headers.value = response.data.headers;
      } catch (error) {
        console.error('Error fetching sheet data:', error);
        ElMessage.error('获取数据失败！');
      } finally {
        loading.value = false;
      }
   };

   const downloadDefaultData = async () => {
      try {
        const response = await axios.get(`/api/download-excel?file_type=${'reference'}`, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', '参考原始数据.xlsx')
        document.body.appendChild(link)
        link.click()
      } catch (error) {
        ElMessage.error('下载失败')
      }
    }

    const handleDrawerClose = () => {
      drawerVisible.value = false;
    };

    return {
      uploadRef,
      drawerVisible,
      excelData,
      headers,
      sheetNames,
      selectedSheet,
      fileList,
      loading,
      beforeUpload,
      handlePreview,
      handleRemove,
      handleSuccess,
      handleError,
      submitUpload,
      fetchSheetData,
      handleDrawerClose,
      downloadDefaultData,
      authToken
    };
  }
};
</script>
