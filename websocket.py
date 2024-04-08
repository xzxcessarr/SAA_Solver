import os,subprocess
from winpty import PtyProcess
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

# # 存储每个 WebSocket 连接的伪终端
# pty_processes = {}

# async def monitor_pty_output(websocket_id: str, websocket: WebSocket):
#     if websocket_id not in pty_processes:
#         # 创建一个新的伪终端，并运行一个需要监控的长期运行的命令，例如 'top'
#         pty_processes[websocket_id] = PtyProcess.spawn('uvicorn')

#     proc = pty_processes[websocket_id]

#     try:
#         while True:
#             output = proc.read(1024)
#             if output:
#                 await websocket.send_text(output)
#             else:
#                 # 没有输出时等待一小段时间再次尝试读取
#                 await asyncio.sleep(0.1)
#     except Exception as e:
#         # 发生异常，可能是伪终端关闭了
#         await websocket.send_text(f"Error: {str(e)}")

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     websocket_id = str(id(websocket))  # 为每个 WebSocket 连接生成一个唯一标识符
#     try:
#         # 直接开始监控伪终端输出，不接收任何来自前端的指令
#         await monitor_pty_output(websocket_id, websocket)
#     except WebSocketDisconnect:
#         # 客户端断开连接
#         print(f"WebSocket connection closed")
#     finally:
#         # 清理工作：当 WebSocket 关闭时，结束伪终端进程
#         proc = pty_processes.pop(websocket_id, None)
#         if proc:
#             proc.terminate()
#         await websocket.close()