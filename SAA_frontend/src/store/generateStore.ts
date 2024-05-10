import { defineStore } from 'pinia';

export const useDataStore = defineStore('dataStore', {
  state: () => ({
    costParams: {},
    scenarioParams: {},
  }),
  actions: {
    setCostParams(params) {
      this.costParams = params;
    },
    setScenarioParams(params) {
      this.scenarioParams = params;
    },
  },
});