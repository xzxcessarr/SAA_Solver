/**
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Echarts.

Author: cessarr
Date Created: 2024-05-19
License: MIT License

Description:
------------
此组件用于在Vue3框架下实现地图的显示和数据的动态更新。 
*/
import { ref, type Ref, watchEffect } from "vue";
import * as echarts from "echarts";

export function useECharts(
    chartDomRef: Ref<HTMLElement | null>,
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

    const randomColor = () => {
        return `#${Math.floor(Math.random() * 16777215).toString(16)}`;
    };

    const initChart = () => {
        if (chartDomRef.value && !chartInstance) {
            chartInstance = echarts.init(chartDomRef.value);
        }
    };

    const createGraph = () => {
        // const nodes = coordinates.value.map((coord, index) => ({
        //     name: `城市 ${index + 1}`,
        //     x: coord[0],
        //     y: coord[1],
        //     itemStyle: {
        //         color: randomColor(),
        //     },
        //     fixed: true,
        // }));

        const nodes = coordinates.value.map((coord, index) => {
            // console.log(coord)
            return {
                name: `城市 ${index + 1}`,
                x: coord[0],
                y: coord[1],
                itemStyle: {
                    color: randomColor(),
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
            backgroundColor: {
                type: 'pattern',
                image: document.createElement('canvas'),
                repeat: 'repeat'
            },
            series: [
                {
                    type: "graph",
                    layout: "none",
                    roam: true,
                    label: { show: true },
                    data: nodes,
                    links: links,
                },
            ],
        };

        // 设置背景网格
        const canvas = option.backgroundColor.image as HTMLCanvasElement;
        canvas.width = canvas.height = 1000; // 增大画布大小
        const ctx = canvas.getContext('2d');
        if (ctx) {
            ctx.strokeStyle = '#f0f0f0'; // 设置细线颜色
            ctx.lineWidth = 0.5; // 设置线宽为更细
            for (let i = 0; i < 1000; i += 10) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, 1000);
                ctx.moveTo(0, i);
                ctx.lineTo(1000, i);
                ctx.stroke();
            }
        }

        chartInstance?.setOption(option);
    };

    // 监控coordinates变化并重新创建图表
    watchEffect(() => {
        initChart();
        createGraph();
    });


    const cleanup = () => {
        if (chartInstance) {
            chartInstance.dispose();
            chartInstance = null;
        }
    };

    return { initChart, createGraph, cleanup };
}