<template>
    <div class="flex flex-col items-center justify-center p-4">
        <!-- 条件渲染步骤导航，仅在选择生成数据时显示 -->
        <div class="flex space-x-4 justify-center mt-4">
            <el-button @click="useDefaultData" type="primary" round>默认数据</el-button>
            <el-button @click="toggleGenerateData" type="info" round>生成数据</el-button>
            <el-button @click="toggleUploadData" type="warning" round>上传数据</el-button>
        </div>
        <div v-if="showGenerateData" class="w-full p-4">
            <!-- 步骤导航，更改为水平布局 -->
            <el-steps :active="activeStep" direction="horizontal" class="justify-center">
                <el-step title="成本数据"></el-step>
                <el-step title="情景数据"></el-step>
                <el-step title="完成"></el-step>
            </el-steps>
            <div class="mt-4 flex justify-center space-x-2">
                <el-button v-if="activeStep > 0" @click="prevStep" type="success" round>
                    上一步
                </el-button>
                <el-button v-if="activeStep < 2" @click="nextStep" type="primary" round>
                    下一步
                </el-button>
            </div>
        </div>

        <div class="w-full">
            <div class="flex flex-1 items-center justify-center mt-6">

                <div class="w-full flex flex-col items-center justify-center mt-6">
                    <!-- 生成数据视图 -->
                    <div v-if="showGenerateData" class="w-full max-w-4xl">
                        <div v-if="activeStep === 0" class="mt-4">
                            <CostForm />
                        </div>
                        <div v-if="activeStep === 1" class="mt-4">
                            <ScenarioForm />
                        </div>
                        <div v-if="activeStep === 2" class="mt-4">
                            <el-row>
                                <el-result icon="success" title="生成成功" sub-title="生成算例成功，系统已设置数据为生成数据"></el-result>
                            </el-row>
                            <el-row class="flex justify-center space-x-4 mt-4">
                                <el-button @click="downloadGeneratedData" type="primary" round>
                                    下载生成的Excel
                                </el-button>
                                <el-button @click="goToParameterSetup" type="success" round>
                                    计算参数设置
                                </el-button>
                            </el-row>
                        </div>
                    </div>

                    <!-- 上传数据视图 -->
                    <div v-if="showUploadData" class="w-full max-w-4xl mt-6 flex flex-col items-center">
                        <logs-web-socket />
                        <el-button @click="goToParameterSetup" type="success" round class="mt-4">
                            计算参数设置
                        </el-button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import CostForm from '@/components/GenerateData/CostForm.vue';
import ScenarioForm from '@/components/GenerateData/ScenarioForm.vue';
import LogsWebSocket from '@/components/UploadExcel.vue';
import emitter from '@/utils/emitter';
import axios from 'axios';

const router = useRouter();
const showGenerateData = ref(false);
const showUploadData = ref(false);
const activeStep = ref(0);

const goToParameterSetup = async () => {
    router.push('/config_solver');
    emitter.emit('goToParameterSetup');
};

const useDefaultData = async () => {
    const response = await axios.get('/api/reset_raw_data');
    console.log(response.data.message);
    goToParameterSetup();
}

const toggleGenerateData = () => {
    showGenerateData.value = !showGenerateData.value;
    if (showGenerateData.value) {
        // Reset steps when toggling on
        activeStep.value = 0;
    }
};

const toggleUploadData = () => {
    showUploadData.value = !showUploadData.value;
};

const nextStep = () => {
    if (activeStep.value < 2) {
        activeStep.value++;
    }
};

const prevStep = () => {
    if (activeStep.value > 0) {
        activeStep.value--;
    }
};


const downloadGeneratedData = async () => {
    try {
        const response = await axios.get(`/api/download-excel?file_type=${'generate'}`, { responseType: 'blob' });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', '生成数据.xlsx');
        document.body.appendChild(link);
        link.click();
    } catch (error) {
        console.error('Error downloading the file:', error);
    }
};

</script>