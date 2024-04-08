from fastapi import FastAPI, UploadFile, File, HTTPException, Request, WebSocket
from pydantic import BaseModel
from typing import List, Tuple
from fastapi.middleware.cors import CORSMiddleware
import os, json
from websocket import run_command_with_pty
from main import two_stage_sp_model, solver

app = FastAPI()

# Set up CORS middleware
origins = [
    "http://localhost:5173",  # Vue.js front-end address
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ParameterModel(BaseModel):
    IS: int
    NS: int
    MS: int
    SS_SAA: int
    data_process_methods: List[str]
    cluster_methods: List[str]
    sample_generate_methods: List[str]
    dim_reduction_methods: List[str]
    max_attempts: int


@app.post("/parameters")
async def receive_parameters(request: Request, parameters: ParameterModel):
    # try:
    body = await request.json()
    print(json.dumps(body, indent=2))
    # 解构前端发送的参数
    global IS,NS,MS,SS_SAA, data_process_methods, cluster_methods, sample_generate_methods, dim_reduction_methods, max_attempts
    IS=parameters.IS
    NS=parameters.NS
    MS=parameters.MS
    SS_SAA=parameters.SS_SAA
    data_process_methods = parameters.data_process_methods
    cluster_methods = parameters.cluster_methods
    sample_generate_methods = parameters.sample_generate_methods
    dim_reduction_methods = parameters.dim_reduction_methods
    max_attempts = parameters.max_attempts
    return {"message": "Parameters received successfully"}
    # except Exception as e:
    #     # 输出错误信息到控制台
    #     print(e)
    #     # 返回具体错误信息给前端
    #     raise HTTPException(status_code=422, detail=str(e))

@app.post("/data-files")
async def receive_data_files(input_file: UploadFile = File(...), output_file: str = "result.xlsx"):
    global Input_data, Output_data
    # Input_file = input_file.filename
    # Input_file = "input/data.xlsx"
    # Output_file = output_file
    Input_data='input/data.xlsx'
    Output_data='result.xlsx'
    
    # Save the uploaded input file
    with open(Input_data, "wb") as file:
        file.write(await Input_data.read())
    
    return {"message": "Data files received successfully"}

@app.post("/run-solver")
async def run_solver():
    global graphs_sample_save_directory, graphs_cluster_save_directory
    Input_data='input/data.xlsx'
    Output_data='result.xlsx'
    
    # for IS, NS, MS, SS_SAA in IS_NS_MS_SS_SAA_combinations:
    print(f"计算参数组合: IS={IS}, NS={NS}, MS={MS}, SS_SAA={SS_SAA}")
    
    # 先计算gurobi_opt
    gurobi_opt = two_stage_sp_model(
        IS_init=IS, 
        NS_init=NS, 
        Input_file=Input_data,
        Output_file=Output_data
    )
    print(f"gurobi_opt的计算结果是: {gurobi_opt}")
    
    # 创建图表保存文件夹的名称
    graphs_dir_name = f"Graphs_IS={IS}_NS={NS}_MS={MS}_SS_SAA={SS_SAA}"
    graphs_sample_save_directory = os.path.join('./Graphs', graphs_dir_name, 'Samples')
    graphs_cluster_save_directory = os.path.join('./Graphs', graphs_dir_name, 'Clusters')
    
    # 检查文件夹是否存在，如果不存在，则创建它们
    os.makedirs(graphs_sample_save_directory, exist_ok=True)
    os.makedirs(graphs_cluster_save_directory, exist_ok=True)
    
    for data_process in data_process_methods:
        for cluster in cluster_methods:
            # for sample_generate in sample_generate_methods:
                # for dim_reduction in dim_reduction_methods:
                    # Call the solver function with the current combination of parameters
                # print(f"Executing combination: Data Processing={data_process}, Clustering={cluster}, Sampling={sample_generate}, Dimensionality Reduction={dim_reduction}")
            print(f"Executing combination: Data Processing={data_process}, Clustering={cluster}, Sampling=Stratified")
            attempt = 0
            while attempt < max_attempts:
                try:
                    solver(
                        DATA_PROCESS_METHOD=data_process,
                        CLUSTER_METHOD=cluster,
                        SAMPLE_GENERATE_METHOD='Stratified',
                        GRAPH_METHOD='3d',
                        IS=IS,
                        NS=NS,
                        MS=MS,
                        SS_SAA=SS_SAA,
                        Graphs_sample_save_directory=graphs_sample_save_directory,
                        Graphs_cluster_save_directory=graphs_cluster_save_directory,
                        Input_file=Input_data,
                        Output_file=Output_data,
                        gurobi_opt=gurobi_opt
                    )
                    break
                except Exception as e:
                    attempt += 1
                    print(f"An error occurred while executing the solver with parameters: {e}")
                    
    # return {"message": "Solver execution completed", "result": result}

@app.get("/solver-callback")
async def solver_callback():
    return {
        "message": "Solver execution completed",
        "graphs_sample_save_directory": graphs_sample_save_directory,
        "graphs_cluster_save_directory": graphs_cluster_save_directory
    }

# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     try:
#         while True:
#             data = await websocket.receive_text()
#             # 执行从前端收到的命令
#             await run_some_command(data, websocket)
#     except Exception as e:
#         # 异常处理，例如客户端断开连接
#         print(f"WebSocket connection closed: {e}")
#         await websocket.close()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # 使用伪终端执行从前端收到的命令
            await run_command_with_pty(data, websocket)
    except Exception as e:
        # 异常处理，例如客户端断开连接
        print(f"WebSocket connection closed: {e}")
        await websocket.close()

# 如果你希望建立一个可以直接运行的 FastAPI 应用，你还需要定义一个入口点
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)