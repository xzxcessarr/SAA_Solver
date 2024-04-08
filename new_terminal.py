import subprocess
import shlex
from fastapi import WebSocket

async def run_some_command(command: str, websocket: WebSocket):
    try:
        print(f"Received command: {command}")
        args = shlex.split(command)
        print(f"Parsed arguments: {args}")
        process = subprocess.Popen(
            args,
            bufsize=1,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            universal_newlines=True,
            shell=True  # 使用 shell 执行命令
        )

        # 循环读取输出
        while True:
            output = process.stdout.readline()
            if output:
                await websocket.send_text(output+ '\n')
            else:
                # 输出结束，检查进程是否结束
                if process.poll() is not None:
                    break

        # 命令执行完成后发送结束信号
        await websocket.send_text("Command execution completed.")

        # 检查进程是否成功退出
        if process.returncode != 0:
            await websocket.send_text(f"Command exited with return code {process.returncode}")
    except Exception as e:
        print(f"Error: {e}")  # 日志：打印错误信息
        await websocket.send_text(f"Error: {str(e)}")