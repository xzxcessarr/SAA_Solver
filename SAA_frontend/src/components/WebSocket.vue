<template>
    <div ref="terminalContainer" class="terminal"></div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { AttachAddon } from 'xterm-addon-attach';

const terminalContainer = ref(null);
let terminal = null;
let ws = null;

onMounted(() => {
    terminal = new Terminal({
        cursorBlink: true,    // 光标闪烁
        scrollback: 1000,     // 滚动历史记录的最大行数
        disableStdin: false,  // 不禁用标准输入
        convertEol: true,     // 当输出没有换行符时，强制进行换行
        // 您可以添加更多配置项来满足您的需求
    });
    const fitAddon = new FitAddon();

    terminal.loadAddon(fitAddon);

    if (terminalContainer.value) {
        terminal.open(terminalContainer.value);
        terminal.writeln('Hello from xterm.js')
        fitAddon.fit();
    }

    // 建立WebSocket连接
    ws = new WebSocket('ws://localhost:8000/ws');
    const attachAddon = new AttachAddon(ws);
    terminal.loadAddon(attachAddon);

    ws.onopen = () => {
        // ws.send('echo "Welcome to the WebSocket terminal!"');
    };

    ws.onmessage = (event) => {
        terminal.write(event.data);  // 将收到的数据输出到xterm终端
    };

    // 监听xterm终端的输入，并通过WebSocket发送到服务器
    let commandBuffer = '';

    terminal.onData((data) => {
        if (data === '\n') { // 如果按下了回车键（注意：根据您的终端配置，可能是 '\n'）
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(commandBuffer);
                commandBuffer = ''; // 清空命令缓冲区
            }
        } else {
            commandBuffer += data; // 将输入的数据添加到命令缓冲区
        }
    });
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
    /* 根据需要调整大小 */
}
</style>