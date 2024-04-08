<template>
    <div ref="terminalContainer" class="terminal"></div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';

const terminalContainer = ref(null);
let terminal = null;
let ws = null;

onMounted(() => {
    terminal = new Terminal({
        cursorBlink: true,
        scrollback: 1000,
        disableStdin: true, // 禁用输入
        convertEol: true,
    });
    const fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);

    if (terminalContainer.value) {
        terminal.open(terminalContainer.value);
        terminal.writeln('监控终端中...');
        fitAddon.fit();
    }

    ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => {
        // WebSocket 连接打开后的操作，如果需要的话
    };

    ws.onmessage = (event) => {
        // 直接将后端传回的数据写到终端
        terminal.write(event.data);
    };
});

onUnmounted(() => {
    if (ws) {
        ws.close();
    }
    if (terminal) {
        terminal.dispose();
    }
});
</script>

<style scoped>
.terminal {
    width: 100%;
    height: 400px;
    background-color: black;
    color: white; /* 设置文本颜色为白色 */
    overflow: auto; /* 如果内容超出容器大小，则显示滚动条 */
    padding: 10px; /* 添加一些内边距 */
}
</style>