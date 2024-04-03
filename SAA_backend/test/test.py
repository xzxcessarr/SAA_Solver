from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Tuple
import os
from main import two_stage_sp_model, solver

app = FastAPI()

class ParameterModel(BaseModel):
    IS_NS_MS_SS_SAA_combinations: List[Tuple[int, int, int, int]]
    data_process_methods: List[str]
    cluster_methods: List[str]
    sample_generate_methods: List[str]
    dim_reduction_methods: List[str]
    max_attempts: int

@app.post("/parameters")
async def receive_parameters(parameters: ParameterModel):
    global IS_NS_MS_SS_SAA_combinations, data_process_methods, cluster_methods, sample_generate_methods, dim_reduction_methods, max_attempts
    IS_NS_MS_SS_SAA_combinations = parameters.IS_NS_MS_SS_SAA_combinations
    data_process_methods = parameters.data_process_methods
    cluster_methods = parameters.cluster_methods
    sample_generate_methods = parameters.sample_generate_methods
    dim_reduction_methods = parameters.dim_reduction_methods
    max_attempts = parameters.max_attempts
    return {"message": "Parameters received successfully"}

@app.post("/data-files")
async def receive_data_files(input_file: UploadFile = File(...), output_file: str = "result.xlsx"):
    global Input_file, Output_file
    Input_file = input_file.filename
    Output_file = output_file
    
    # Save the uploaded input file
    with open(Input_file, "wb") as file:
        file.write(await input_file.read())
    
    return {"message": "Data files received successfully"}

@app.post("/run-solver")
async def run_solver():
    global graphs_sample_save_directory, graphs_cluster_save_directory
    
    for IS, NS, MS, SS_SAA in IS_NS_MS_SS_SAA_combinations:
        print(f"计算参数组合: IS={IS}, NS={NS}, MS={MS}, SS_SAA={SS_SAA}")
        
        # 先计算gurobi_opt
        gurobi_opt = two_stage_sp_model(
            IS_init=IS, 
            NS_init=NS, 
            Input_file=Input_file,
            Output_file=Output_file
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
                        result = solver(
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
                            Input_file=Input_file,
                            Output_file=Output_file,
                            gurobi_opt=gurobi_opt
                        )
                        break
                    except Exception as e:
                        attempt += 1
                        print(f"An error occurred while executing the solver with parameters: {e}")
                        
    return {"message": "Solver execution completed", "result": result}

@app.get("/solver-callback")
async def solver_callback():
    return {
        "message": "Solver execution completed",
        "graphs_sample_save_directory": graphs_sample_save_directory,
        "graphs_cluster_save_directory": graphs_cluster_save_directory
    }