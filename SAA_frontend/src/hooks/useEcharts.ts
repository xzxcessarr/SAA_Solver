// useECharts.ts
import { onMounted, onUnmounted, ref, watch } from "vue";
import type {Ref} from "vue"
import * as echarts from "echarts/core";
import { ScatterChart } from "echarts/charts";
import {
  TitleComponent,
  TooltipComponent,
  AxisPointerComponent,
  GridComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  TitleComponent,
  TooltipComponent,
  AxisPointerComponent,
  GridComponent,
  ScatterChart,
  CanvasRenderer,
]);

export function useECharts(chartRef: Ref<HTMLElement | null>, chartData: Ref<any[]>) {
    let chartInstance: echarts.ECharts | null = null;
  
    const updateChart = () => {
      if (!chartRef.value) {
        // 如果DOM元素还没有挂载，直接返回
        return;
      }
  
      if (chartInstance === null) {
        // 初始化echarts实例
        chartInstance = echarts.init(chartRef.value);
      }
    const option = {
      title: {
        text: "Master Painter Color Choices Throughout History",
        subtext: "Data From Plot.ly",
        left: "right",
      },
      xAxis: {
        type: "value",
        splitLine: {
          show: false,
        },
        scale: true,
        splitNumber: 5,
        max: "dataMax",
        axisLabel: {
          formatter: function (val: number) {
            return val + "s";
          },
        },
      },
      yAxis: {
        type: "value",
        min: 0,
        max: 360,
        interval: 60,
        name: "Hue",
        splitLine: {
          show: false,
        },
      },
      series: [
        {
          name: "scatter",
          type: "scatter",
          symbolSize: function (val: number, param: any) {
            // 注意这里使用 chartData.value 来访问数据
            return (
              chartData.value[0].marker.size[param.dataIndex] /
              chartData.value[0].marker.sizeref
            );
          },
          itemStyle: {
            color: function (param: any) {
              // 同上，使用 chartData.value
              return chartData.value[0].marker.color[param.dataIndex];
            },
          },
          data: chartData.value[0].x.map(function (x: number, idx: number) {
            // 同上，使用 chartData.value
            return [+x, +chartData.value[0].y[idx]];
          }),
        },
      ],
    };

    chartInstance.setOption(option);
  };

  onMounted(() => {
    window.addEventListener("resize", () => {
      chartInstance?.resize();
    });
    updateChart();
  });

  onUnmounted(() => {
    window.removeEventListener("resize", () => {
      chartInstance?.resize();
    });
    chartInstance?.dispose();
  });

  watch(chartData, (newData, oldData) => {
    // 当 chartData 发生变化时更新图表
    updateChart();
  });

  return {
    updateChart,
  };
}