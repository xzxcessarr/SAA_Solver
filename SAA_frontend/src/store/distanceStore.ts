import { defineStore } from 'pinia';

interface DistanceState {
  coordinates: number[][];
}

export const useDistanceStore = defineStore({
  id: 'echarts',
  state: (): DistanceState => ({
    coordinates: []
  }),
  actions: {
    // 更新存储的坐标数据
    updateCoordinates(newCoordinates: number[][]) {
      this.coordinates = newCoordinates;
    }
  }
});