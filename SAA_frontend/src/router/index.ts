import { createRouter, createWebHistory } from 'vue-router'
import ResultPage from '../views/ResultPage.vue'
import DataConfig from '../views/DataConfig.vue'
import ConfigSolver from '../views/ConfigSolver.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect:'/config_solver'
    },
    {
      path: '/data-config',
      name: 'DataConfig',
      component: DataConfig
    },
    {
      path: '/config_solver',
      name: 'ConfigSolver',
      component: ConfigSolver,
    },
    {
      path: '/result',
      name: 'ResultPage',
      component: ResultPage
    },
  ]
})

export default router
