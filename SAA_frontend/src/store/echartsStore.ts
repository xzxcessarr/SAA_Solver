// stores/echartsStore.js
import { defineStore } from 'pinia';

export const useEchartsStore = defineStore('echarts', {
  state: () => ({
    params: { IS: 20, NS: 100, Raw_data_flag:true }
  }),
  actions: {
    updateEchartsParams(newParams) {
      this.$patch({
        params: newParams
      });
    }
  }
});