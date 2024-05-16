<template>

    <div class="flex w-96">
        <el-form @submit.prevent="generateScenario">
            <el-form-item label="Number of Cities">
                <el-input-number v-model="numCities" :min="1"></el-input-number>
            </el-form-item>
            <el-form-item label="Minimum Distance">
                <el-input-number v-model="minDistance" :min="1"></el-input-number>
            </el-form-item>
            <el-form-item label="Maximum Distance">
                <el-input-number v-model="maxDistance" :min="1"></el-input-number>
            </el-form-item>
            <el-form-item label="Minimum Population">
                <el-input-number v-model="minPopulation" :min="1"></el-input-number>
            </el-form-item>
            <el-form-item label="Maximum Population">
                <el-input-number v-model="maxPopulation" :min="1"></el-input-number>
            </el-form-item>
            <el-form-item label="Number of Scenarios">
                <el-input-number v-model="numScenarios" :min="1"></el-input-number>
            </el-form-item>
            <el-form-item label="Realistic Scenarios">
                <el-switch v-model="realistic"></el-switch>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" native-type="submit">Generate Scenario</el-button>
            </el-form-item>
        </el-form>
    </div>
</template>

<script>
import { defineComponent, ref } from 'vue';
import axios from 'axios';

export default defineComponent({
    setup() {
        const numCities = ref(20);
        const minDistance = ref(1000);
        const maxDistance = ref(10000);
        const minPopulation = ref(1000);
        const maxPopulation = ref(10000);
        const numScenarios = ref(100);
        const realistic = ref(false);

        const generateScenario = async () => {
            try {
                const response = await axios.post('/api/generate_scenario', {
                    num_cities: numCities.value,
                    min_distance: minDistance.value,
                    max_distance: maxDistance.value,
                    min_population: minPopulation.value,
                    max_population: maxPopulation.value,
                    num_scenarios: numScenarios.value,
                    realistic: realistic.value,
                });
                ElMessage.success('生成情景数据成功！');
                console.log(response.data);
            } catch (error) {
                console.error(error);
            }
        };

        return {
            numCities,
            minDistance,
            maxDistance,
            minPopulation,
            maxPopulation,
            numScenarios,
            realistic,
            generateScenario,
        };
    },
});
</script>