import { onMounted, onUnmounted, ref, watch, type Ref } from "vue";
import * as echarts from "echarts/core";
import { ScatterChart } from "echarts/charts";
import {
    TitleComponent,
    TooltipComponent,
    AxisPointerComponent,
    GridComponent,
    VisualMapComponent
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
    TitleComponent,
    TooltipComponent,
    AxisPointerComponent,
    GridComponent,
    ScatterChart,
    VisualMapComponent,
    CanvasRenderer,
]);

export function useECharts(
    chartRef: Ref<HTMLElement | null>,
    chartData: Ref<any[]>,
    scaleFactor: number = 0.2 // 新增缩放因子参数，默认值为0.1
) {
    let chartInstance: echarts.ECharts | null = null;

    const updateChart = () => {
        if (!chartRef.value || chartData.value.length === 0) {
            return;
        }

        if (chartInstance === null) {
            chartInstance = echarts.init(chartRef.value);
        }

        const option = {
            title: {
                text: "样本场景分布图",
                subtext: "气泡大小代表需求量",
                left: "center",
            },
            tooltip: {
                trigger: "item",
                formatter: (params) => {
                    return `城市: ${params.value[0]}<br/>场景: ${params.value[1]}<br/>需求: ${params.value[2]}`;
                }
            },
            visualMap: {
                min: Math.min(...chartData.value.map(d => d.size)),
                max: Math.max(...chartData.value.map(d => d.size)),
                dimension: 2,
                text: ['气泡大小：水需求单位（每单位/1000加仑）'],
                textGap: 5, // 调整文本与滑块之间的距离
                itemWidth: 30,
                itemHeight: 120,
                calculable: true,
                precision: 0.1,
                orient: 'horizontal', // 设置为水平方向
                align: 'auto', // 调整对齐方式，自动选择最佳对齐
                inRange: {
                    color: ['#00008b', '#ff0000'] // 蓝色到红色
                },
                textStyle: {
                    color: '#000' // 将文字颜色设置为黑色
                },
                bottom: 0 // 确保visualMap位于组件的底部
            },
            xAxis: {
                type: 'value',
                name: '城市',
                splitLine: { show: false },
                axisLabel: {
                    formatter: '城市{value}',
                    show: true,
                    rotate: 45
                }
            },
            yAxis: {
                type: 'value',
                name: '场景',
                splitLine: { show: false },
                axisLabel: {
                    formatter: '场景{value}',
                    show: true,
                    // rotate: 45
                }
            },
            series: [{
                name: '需求',
                type: 'scatter',
                data: chartData.value.map(item => [item.x, item.y, item.size]),
                symbolSize: function (value) {
                    return Math.sqrt(value[2]) * scaleFactor; // 使用缩放因子调整气泡大小
                }
            }]
        };

        chartInstance.setOption(option);
    };

    watch(chartData, updateChart, { deep: true });

    onMounted(() => {
        window.addEventListener("resize", () => {
            chartInstance?.resize();
        });
    });

    onUnmounted(() => {
        window.removeEventListener("resize", () => {
            chartInstance?.resize();
        });
        chartInstance?.dispose();
    });

    return {
        updateChart,
    };
}