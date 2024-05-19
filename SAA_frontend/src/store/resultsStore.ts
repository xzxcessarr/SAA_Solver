import { defineStore } from 'pinia';

interface Result {
  IS: number;
  NS: number;
  Vx: number[][];
  Vy: number[][];
  script_name: string;
  opt_f: number;
  elapsed_time: number;
}

export const useResultsStore = defineStore('results', {
  state: () => ({
    saaResults: [] as Result[],
    gurobiResults: [] as Result[],
  }),
  actions: {
    addSAAResult(newResult: Result) {
      this.saaResults.push(newResult);
    },
    addGurobiResult(newResult: Result) {
      this.gurobiResults.push(newResult);
    },
  },
  getters: {
    allResults(): Result[] {
      return [...this.saaResults, ...this.gurobiResults];
    },
  },
});