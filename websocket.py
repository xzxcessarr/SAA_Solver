import os,subprocess
from pywinpty import PtyProcess
import asyncio
from fastapi import  WebSocket

async def run_command_with_pty(command: str, websocket: WebSocket):
    # 使用 pywinpty 创建伪终端
    proc = PtyProcess.spawn(command)

    try:
        while True:
            output = proc.read(1024)
            if output:
                await websocket.send_text(output)
            else:
                break
    finally:
        proc.terminate()

    # 发送命令执行完成的消息
    await websocket.send_text("Command execution completed.")

    # 检查进程退出代码
    exit_code = proc.exitstatus
    if exit_code != 0:
        await websocket.send_text(f"Command exited with return code {exit_code}")
        
def read_from_master(master_fd, websocket):
    while True:
        output = os.read(master_fd, 1024)
        if output:
            asyncio.ensure_future(websocket.send_text(output.decode()))
        else:
            break