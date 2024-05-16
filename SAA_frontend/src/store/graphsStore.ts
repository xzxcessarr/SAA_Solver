import { defineStore } from 'pinia';
import axios from 'axios';

export const useImagesStore = defineStore('images', {
  state: () => ({
    imagesByDir: {} as Record<string, { sampleImages: string[], clusterImages: string[] }>,
  }),
  
  actions: {
    async fetchImages(dirName: string = 'Default') {
      try {
        const sampleResponse = await axios.get(`/api/get_sample_images?dir_name=${dirName}`);
        const clusterResponse = await axios.get(`/api/get_cluster_images?dir_name=${dirName}`);

        this.imagesByDir[dirName] = {
          sampleImages: sampleResponse.data.sample_images,
          clusterImages: clusterResponse.data.cluster_images,
        };
      } catch (error) {
        console.error('Error fetching images:', error);
      }
    }
  }
});