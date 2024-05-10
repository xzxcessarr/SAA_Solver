import { defineStore } from 'pinia';

export const useParameterStore = defineStore('parameter', {
  state: () => ({
    IS: 20,
    NS: 100,
    MS: 10,
    SS_SAA: 10,
    data_process_methods: ['truncated_svd'],
    cluster_methods: ['som'],
    sample_generate_methods: ['Stratified', 'Simple'],
    graph_methods: ['3d', '2d'],
    max_attempts: 2,
    calculate_epoch: 1
  }),
  actions: {
    updateParameters(newParameters) {
      this.$patch(newParameters);
    }
  }
});