<template>
  <el-form @submit.prevent="saveAllCosts" class="flex flex-wrap">

    <div class="flex w-screen justify-center">
      <div class="flex flex-col w-1/2 p-4">
        <!-- 设施成本输入 -->
        <el-form-item label="Small Facility CF">
          <el-input-number v-model="smallFacilityCF"></el-input-number>
        </el-form-item>
        <el-form-item label="Small Facility U">
          <el-input-number v-model="smallFacilityU"></el-input-number>
        </el-form-item>
        <el-form-item label="Medium Facility CF">
          <el-input-number v-model="mediumFacilityCF"></el-input-number>
        </el-form-item>
        <el-form-item label="Medium Facility U">
          <el-input-number v-model="mediumFacilityU"></el-input-number>
        </el-form-item>
        <el-form-item label="Large Facility CF">
          <el-input-number v-model="largeFacilityCF"></el-input-number>
        </el-form-item>
        <el-form-item label="Large Facility U">
          <el-input-number v-model="largeFacilityU"></el-input-number>
        </el-form-item>

        <!-- 水资源成本输入 -->
        <el-form-item label="Water V">
          <el-input-number v-model="waterV" :step="0.00001"></el-input-number>
        </el-form-item>
        <el-form-item label="Water CP">
          <el-input-number v-model="waterCP" :step="0.00001"></el-input-number>
        </el-form-item>
        <el-form-item label="Water CT">
          <el-input-number v-model="waterCT" :step="0.00001"></el-input-number>
        </el-form-item>
        <el-form-item label="Water CH">
          <el-input-number v-model="waterCH" :step="0.00001"></el-input-number>
        </el-form-item>
        <el-form-item label="Water G">
          <el-input-number v-model="waterG" :step="0.00001"></el-input-number>
        </el-form-item>
      </div>

      <div class="flex flex-col w-1/2 p-4">
        <!-- 食物成本输入 -->
        <el-form-item label="Food V">
          <el-input-number v-model="foodV" :step="0.00001"></el-input-number>
        </el-form-item>
        <el-form-item label="Food CP">
          <el-input-number v-model="foodCP" :step="0.00001"></el-input-number>
        </el-form-item>
        <el-form-item label="Food CT">
          <el-input-number v-model="foodCT" :step="0.00001"></el-input-number>
        </el-form-item>
        <el-form-item label="Food CH">
          <el-input-number v-model="foodCH" :step="0.00001"></el-input-number>
        </el-form-item>
        <el-form-item label="Food G">
          <el-input-number v-model="foodG" :step="0.00001"></el-input-number>
        </el-form-item>

        <!-- 药物成本输入 -->
        <el-form-item label="Medicine V">
          <el-input-number v-model="medicineV" :step="0.00001"></el-input-number>
        </el-form-item>
        <el-form-item label="Medicine CP">
          <el-input-number v-model="medicineCP" :step="0.00001"></el-input-number>
        </el-form-item>
        <el-form-item label="Medicine CT">
          <el-input-number v-model="medicineCT" :step="0.00001"></el-input-number>
        </el-form-item>
        <el-form-item label="Medicine CH">
          <el-input-number v-model="medicineCH" :step="0.00001"></el-input-number>
        </el-form-item>
        <el-form-item label="Medicine G">
          <el-input-number v-model="medicineG" :step="0.00001"></el-input-number>
        </el-form-item>
      </div>
    </div>
    <div class="flex items-center justify-center">
      <el-button type="primary" native-type="submit">Save All Costs</el-button>
    </div>
  </el-form>
</template>


<script>
import { defineComponent, ref } from 'vue';
import axios from 'axios';

export default defineComponent({
  setup() {
    // 设施成本数据 with default values
    const smallFacilityCF = ref(19600);
    const smallFacilityU = ref(36400);
    const mediumFacilityCF = ref(188400);
    const mediumFacilityU = ref(408200);
    const largeFacilityCF = ref(300000);
    const largeFacilityU = ref(780000);

    // 水资源成本数据 with default values
    const waterV = ref(144.6);
    const waterCP = ref(647.7);
    const waterCT = ref(0.3);
    const waterCH = ref(129.54);
    const waterG = ref(6477);

    // 食物成本数据 with default values
    const foodV = ref(83.33);
    const foodCP = ref(5420);
    const foodCT = ref(0.04);
    const foodCH = ref(1084);
    const foodG = ref(54200);

    // 药物成本数据 with default values
    const medicineV = ref(1.16);
    const medicineCP = ref(140);
    const medicineCT = ref(0.00058);
    const medicineCH = ref(28);
    const medicineG = ref(1400);

    // 提交所有成本数据
    const saveAllCosts = async () => {
      try {
        const response = await axios.post('/api/save_facility_and_resource_cost', {
          small_facility_cf: smallFacilityCF.value,
          small_facility_u: smallFacilityU.value,
          medium_facility_cf: mediumFacilityCF.value,
          medium_facility_u: mediumFacilityU.value,
          large_facility_cf: largeFacilityCF.value,
          large_facility_u: largeFacilityU.value,
          water_v: waterV.value,
          water_cp: waterCP.value,
          water_ct: waterCT.value,
          water_ch: waterCH.value,
          water_g: waterG.value,
          food_v: foodV.value,
          food_cp: foodCP.value,
          food_ct: foodCT.value,
          food_ch: foodCH.value,
          food_g: foodG.value,
          medicine_v: medicineV.value,
          medicine_cp: medicineCP.value,
          medicine_ct: medicineCT.value,
          medicine_ch: medicineCH.value,
          medicine_g: medicineG.value,
        });
        console.log(response.data);
        ElMessage.success('设置成本数据成功！');
      } catch (error) {
        console.error(error);
      }
    };

    return {
      smallFacilityCF,
      smallFacilityU,
      mediumFacilityCF,
      mediumFacilityU,
      largeFacilityCF,
      largeFacilityU,
      waterV,
      waterCP,
      waterCT,
      waterCH,
      waterG,
      foodV,
      foodCP,
      foodCT,
      foodCH,
      foodG,
      medicineV,
      medicineCP,
      medicineCT,
      medicineCH,
      medicineG,
      saveAllCosts,
    };
  },
});
</script>