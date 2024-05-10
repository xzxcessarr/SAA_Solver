import { ref, type Ref, watchEffect, type ComputedRef } from "vue";
import * as echarts from "echarts";

interface ResourceData {
    Vx: number[][]; // Format: [x, y, level] where level > 0 indicates a warehouse
    Vy: number[][]; // Format: [resource1, resource2, resource3] quantities stored
}

export function useECharts(
    chartDomRef: Ref<HTMLElement | null>,
    resourceData: ComputedRef<ResourceData>,
    coordinates: Ref<number[][]>
) {
    let chartInstance: echarts.ECharts | null = null;

    const calculateDistance = (x1: number, y1: number, x2: number, y2: number) => {
        return Math.sqrt(Math.pow((x2 - x1), 2) + Math.pow((y2 - y1), 2));
    };

    const getColorByDistance = (distance: number) => {
        const maxDistance = 2000;
        const hue = (1 - Math.min(distance / maxDistance, 1)) * 240;
        return `hsl(${hue}, 100%, 50%)`;
    };

    const getColorAndSizeByWarehouseLevel = (warehouseLevels: number[]) => {
        if (warehouseLevels[2] > 0) {
            return { color: 'green', size: 40, name:'大' }; // 有大仓库
        } else if (warehouseLevels[1] > 0) {
            return { color: 'yellow', size: 30, name:'中' }; // 有中仓库
        } else if (warehouseLevels[0] > 0) {
            return { color: 'red', size: 20, name:'小' }; // 有小仓库
        }
        return { color: '#ddd', size: 10, name:'无' }; // 没有仓库
    };

    const initChart = () => {
        if (chartDomRef.value && !chartInstance) {
            chartInstance = echarts.init(chartDomRef.value);
        }
    };

    const createGraph = () => {
        const nodes = coordinates.value.map((coord, index) => {
            const resources = resourceData.value.Vy[index];
            const warehouseLevels = resourceData.value.Vx[index];
            const warehouseConfig = getColorAndSizeByWarehouseLevel(warehouseLevels);
            // const totalResources = resources.reduce((a, b) => a + b, 0);
            // const isResourceAvailable = resources.some(resource => resource > 0);
            // console.log(coord)
            
            return {
                name: `城市 ${index + 1}`,
                x: coord[0],
                y: coord[1],
                value: resources,
                // draggable: true, 
                symbolSize: warehouseConfig.size,
                itemStyle: {
                    color: warehouseConfig.color,
                },
                tooltip: {
                    formatter: `城市 ${index + 1}:<br/>物资1: ${resources[0]}<br/>物资2: ${resources[1]}<br/>物资3: ${resources[2]}<br/>仓库等级: ${warehouseConfig.name}`
                },
                fixed: true,
            };
        });

        const links = [];
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const distance = calculateDistance(nodes[i].x, nodes[i].y, nodes[j].x, nodes[j].y);
                links.push({
                    source: i,
                    target: j,
                    label: {
                        show: false,
                        formatter: `城市 ${i + 1} 到 城市 ${j + 1} 的距离: {c}`,
                    },
                    value: distance.toFixed(0),
                    lineStyle: {
                        color: '#ddd', // 默认非常淡的颜色
                        width: 0.5,
                    },
                    emphasis: {
                        label: {
                            show: true,
                        },
                        lineStyle: {
                            color: getColorByDistance(distance),
                            width: 3,
                        }
                    }
                });
            }
        }
    
        const option: echarts.EChartsOption = {
            tooltip: {
                trigger: 'item',
                confine: true,
            },
            series: [
                {
                    type: "graph",
                    layout: "none",
                    // coordinateSystem: "cartesian2d",
                    roam: true,
                    label: { show: true },
                    data: nodes,
                    links: links,
                },
            ],

        };
    
        chartInstance?.setOption(option);
    };

    watchEffect(() => {
        if (coordinates.value.length > 0 && resourceData.value.Vx.length > 0 && resourceData.value.Vy.length > 0) {
            initChart();
            createGraph();
        }
    });

    const cleanup = () => {
        if (chartInstance) {
            chartInstance.dispose();
            chartInstance = null;
        }
    };

    return { initChart, createGraph, cleanup };
}