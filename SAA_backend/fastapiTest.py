# -*- coding: utf-8 -*-
"""
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Fastapi.

Author: cessarr
Date Created: 2024-04-20
License: MIT License

Description:
------------
此部分为fastapi后端路由模块，调用请参考具体路由实现
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from threading import Thread
from sklearn.manifold import MDS
from datetime import datetime
from solver_model import *
from data_generator import *
from clustering_param_analyzer import *
from BaseModel import *
import config
import os, asyncio, logging, shutil, openpyxl
import pandas as pd

app = FastAPI()

# 配置日志
# logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


default_sample_save_directory ='../SAA_frontend/Graphs/Default/Samples'
default_cluster_save_directory ='../SAA_frontend/Graphs/Default/Clusters'

Save_data_path='data/'
Raw_data_path='data/raw_data.xlsx'
Output_data_path='result.xlsx'
Generate_data_path='./data/generated_data.xlsx'
Upload_data_path = 'data/upload_data.xlsx'
Reference_data_path = 'data/reference_data.xlsx'
Input_data_path=Raw_data_path

current_config = {
    "CLUSTER_PARAMS": config.CLUSTER_PARAMS,
    "GRAPH_PROCESS_METHOD": config.GRAPH_PROCESS_METHOD,
    # "n_clusters": config.n_clusters,
    "Water_index": config.Water_index,
    "Food_index": config.Food_index,
    "Medicine_index": config.Medicine_index,
    "variance_ratio": config.variance_ratio
}

Raw_data_flag=True
GRAPH_CONFIG=config.GRAPH_CONFIG
DATA_PROCESS_PARAMS=config.DATA_PROCESS_PARAMS



# Set up CORS middleware
origins = [
    "http://localhost:5173",  # Vue.js front-end address
    "http://192.168.31.234:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 在服务启动时创建日志文件
@app.on_event("startup")
def setup_logging():
    store_data_to_redis(Input_data_path, 20, True)
    # 确保 LOG 文件夹存在
    log_directory = "LOG"
    os.makedirs(log_directory, exist_ok=True)
    
    # 创建基于当前时间的日志文件名
    log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_app.log"
    full_log_path = os.path.join(log_directory, log_filename)
    
    
    # 配置基本的日志设置，包括文件名、日志级别和格式
    if not os.path.exists(full_log_path):
        logging.basicConfig(filename=full_log_path, level=logging.INFO, format='%(message)s')

    # 将日志文件名存储在应用状态中，以便其他部分可以使用
    app.state.log_filename = full_log_path

    # 记录启动信息
    logging.info("Application startup: Logging setup complete.")
    
    # 配置日志以追加模式
    logging.basicConfig(filename=log_filename, filemode='a', level=logging.INFO, format='%(message)s', encoding='utf-8')
    logging.info(f'You are using the raw data')
    
@app.get("/get-config")
async def get_config():
    """
    返回当前配置
    """

    logging.info(f'Current parameters of config:')
    # 遍历字典并打印每个配置项
    # for key, value in current_config.items():
    #     logging.info(f'{key} value : {value}')

    for key, value in current_config.items():
        if key in ['DATA_PROCESS_PARAMS', 'CLUSTER_PARAMS'] and isinstance(value, dict):
            logging.info(f'{key}:')
            for sub_key, sub_value in value.items():
                logging.info(f'  {sub_key} : {sub_value}')
        else:
            logging.info(f'{key} value : {value}')
    logging.info('--------------------------------------------')
    return current_config

def update_graph_config(new_method):
    """
    更新图形处理方法并重新配置 GRAPH_CONFIG
    """
    # 更新 GRAPH_CONFIG 中的方法
    for dimension in GRAPH_CONFIG:
        GRAPH_CONFIG[dimension]['method'] = new_method

def update_data_process_params(variance_ratio):
    """
    根据新的 variance_ratio 更新 DATA_PROCESS_PARAMS 中的配置
    """
    
    # 检查 variance_ratio 是否为浮点数且不大于 1
    if not isinstance(variance_ratio, float) or variance_ratio > 1:
        raise ValueError("variance_ratio must be a float and not greater than 1.")
    
    # 更新 'n_components' 和 'variance_ratio_threshold' 参数
    DATA_PROCESS_PARAMS['pca']['n_components'] = variance_ratio
    DATA_PROCESS_PARAMS['truncated_svd']['n_components'] = variance_ratio
    DATA_PROCESS_PARAMS['factor_analysis']['variance_ratio_threshold'] = variance_ratio

@app.post("/update-config")
async def update_config(request: ConfigUpdateRequest):
    """
    更新配置并重新加载
    """
    # 更新全局变量
    current_config['CLUSTER_PARAMS'] = request.CLUSTER_PARAMS
    current_config['GRAPH_PROCESS_METHOD'] = request.GRAPH_PROCESS_METHOD
    # current_config['n_clusters'] = request.n_clusters
    current_config['Water_index'] = request.Water_index
    current_config['Food_index'] = request.Food_index
    current_config['Medicine_index'] = request.Medicine_index
    current_config['variance_ratio'] = request.variance_ratio

    update_graph_config(current_config['GRAPH_PROCESS_METHOD'])
    update_data_process_params(current_config['variance_ratio'])
    # 这里可以根据需要调用其他函数来应用更改
    # 例如，你可能需要重新运行模型或者更新依赖的对象
    # ...

    return {"message": "Configuration updated successfully"}

@app.post("/reset-config")
async def reset_config():
    """
    重置配置到默认值
    """
    current_config['CLUSTER_PARAMS'] = config.CLUSTER_PARAMS
    current_config['GRAPH_PROCESS_METHOD'] = config.GRAPH_PROCESS_METHOD
    # current_config['n_clusters'] = config.n_clusters
    current_config['Water_index'] = config.Water_index
    current_config['Food_index'] = config.Food_index
    current_config['Medicine_index'] = config.Medicine_index
    current_config['variance_ratio'] = config.variance_ratio

    update_graph_config(current_config['GRAPH_PROCESS_METHOD'])
    update_data_process_params(current_config['variance_ratio'])

    return {"message": "Configuration reset successfully"}

@app.get("/analyze-clustering-params")
async def analyze_params(cluster_method: str, data_processor_method: str, IS: int, NS: int):
    best_params, best_params_range = analyze_clustering_params(
        cluster_method, 
        IS, 
        NS, 
        config.AS, 
        current_config['Food_index'], 
        current_config['Medicine_index'], 
        Raw_data_flag, 
        Input_data_path, 
        current_config['CLUSTER_PARAMS'][cluster_method], 
        app.state.log_filename,
        data_processor_method,
        current_config['variance_ratio']
    )
    print(f"best_params: {best_params}, best_params_range: {best_params_range}")
    return JSONResponse(content={"best_params": best_params, "best_params_range": best_params_range})

@app.post("/send-parameters")
async def receive_parameters(request: Request, parameters: ParameterModel):
    # # try:
    body = await request.json()
    # # print(json.dumps(body, indent=2))
    # 解构前端发送的参数
    global IS,NS,MS,SS_SAA, data_process_methods, cluster_methods, sample_generate_methods, graph_methods, max_attempts, calculate_epoch
    IS=parameters.IS
    NS=parameters.NS
    MS=parameters.MS
    SS_SAA=parameters.SS_SAA
    calculate_epoch=parameters.calculate_epoch
    data_process_methods = parameters.data_process_methods
    cluster_methods = parameters.cluster_methods
    sample_generate_methods = parameters.sample_generate_methods
    graph_methods = parameters.graph_methods
    max_attempts = parameters.max_attempts
    
    store_data_to_redis(Input_data_path, IS, Raw_data_flag)
    # 打印基本参数信息
    logging.info('You have updated the parameters:')
    logging.info('--------------------------------------------')
    logging.info(f'Cities: {IS}, Scenario: {NS}')

    # 打印数组形式的参数信息
    logging.info('Data processing methods: {}'.format(', '.join(data_process_methods)))
    logging.info('Clustering methods: {}'.format(', '.join(cluster_methods)))
    logging.info('Sample generation methods: {}'.format(', '.join(sample_generate_methods)))
    logging.info('Graph methods: {}'.format(', '.join(graph_methods)))
    # 其他相关日志，如果需要
    logging.info(f'Max gurobi solve attempts: {max_attempts}, Calculate epoch: {calculate_epoch}')
    logging.info('--------------------------------------------')
    await get_distance_matrix(IS)
    return {"message": "Parameters received successfully"}


ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
# 检查文件类型是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/upload-data-files")
async def upload_data_files(file: UploadFile = File(...)):
    global Input_data_path, Raw_data_flag
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported file type.")
    try:
        with open(Upload_data_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        Input_data_path = Upload_data_path
        Raw_data_flag = False
        # Extract sheet names to return to the client
        workbook = openpyxl.load_workbook(Upload_data_path)
        sheet_names = workbook.sheetnames
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    return {"message": "File uploaded successfully!", "sheetNames": sheet_names}

@app.get("/get-sheet-data")
async def get_sheet_data(sheetName: str):
    """Return data from the specified Excel sheet."""
    try:
        workbook = openpyxl.load_workbook(Input_data_path)
        worksheet = workbook[sheetName]
        data = []
        headers = [cell.value for cell in worksheet[1]]
        for row in worksheet.iter_rows(min_row=2, values_only=True):
            data.append(dict(zip(headers, row)))
        return {"data": data, "headers": headers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-excel")
async def download_excel(file_type: str = 'reference'):
    # 根据file_type参数选择文件路径
    if file_type.lower() == 'reference':
        file_path = Reference_data_path
        file_name = 'reference_data.xlsx'
    elif file_type.lower() == 'generate':
        file_path = Generate_data_path
        file_name = 'generate_data.xlsx'
    elif file_type.lower() == 'raw':
        file_path = Raw_data_path
        file_name = 'raw_data.xlsx'
    elif file_type.lower() == 'result':
        file_path = Output_data_path
        file_name = 'result.xlsx'
    else:
        # 如果参数不匹配任何已知类型，返回一个404错误
        raise HTTPException(status_code=404, detail="File type not found")

    # 返回所选文件的FileResponse对象
    return FileResponse(path=file_path, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=file_name)

@app.get("/reset_raw_data")
async def reset_raw_data():
    global Raw_data_flag, Input_data_path
    Raw_data_flag = True
    Input_data_path = Raw_data_path
    return JSONResponse(content={"message": "reset to raw data success"})

@app.post("/get_echarts_data")
async def get_echarts_data(request: EchartsDataRequest):
    global Raw_data_flag, Input_data_path
    print(Input_data_path)
    try:
        print(request.cities, request.scenes)
        if Raw_data_flag:
            if request.cities <= 20:
                scenario_sheet_name = 'scenario_20'
            else:
                scenario_sheet_name = 'scenario_40'
        else:
            logging.info(f'You are using the new data')
            scenario_sheet_name = 'scenario'

        # Assuming 'Input_data_path' is predefined somewhere
        df = pd.read_excel(Input_data_path, sheet_name=scenario_sheet_name)
        selected_data = df.iloc[:request.scenes]  # 选择前scenes行

        echarts_data = []
        for index, row in selected_data.iterrows():
            for city in range(1, request.cities + 1):
                value = row.iloc[int(city)]
                if value and value > 0:
                    if Raw_data_flag:
                        # Scale the value by 0.03 and round it
                        value = round(value * 0.03)
                    echarts_data.append({'x': city, 'y': index + 1, 'size': value})

        # print(echarts_data)
        return JSONResponse(content={"data": echarts_data})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate-gurobi-opt")
async def calculate_gurobi_opt():
    global gurobi_opt
    logging.info(f'You are using the Gurobi for solving')
    
    gurobi_opt, gurobi_elapsed_time, Vx, Vy = two_stage_sp_model(
        IS_init=IS, 
        NS_init=NS, 
        Input_file=Input_data_path,
        Output_file=Output_data_path,
        Raw_data_flag=Raw_data_flag,
        log_filename=app.state.log_filename,
        max_attempts=max_attempts,
        AS_init=config.AS,
        LS_init=config.LS, 
        Food_index=current_config['Food_index'], 
        Medicine_index=current_config['Medicine_index']
    )
    logging.info(f'Gurobi solved! the result is {gurobi_opt}')
    
    # 包装成与 run_solver 相同的格式
    result = {
        "script_name": "Gurobi",
        "opt_f": gurobi_opt,
        "elapsed_time": gurobi_elapsed_time,
        "Vx": Vx.tolist(),
        "Vy": Vy.tolist(),
    }
    return {"message": "求解完毕", "results": [result]}  # 将结果包装成列表

# 为图片目录服务静态文件
app.mount("/static", StaticFiles(directory="../SAA_frontend/Graphs"), name="static")

# 存储目录名称和对应的路径
graphs_directories = {
    'Default': {
        'sample': default_sample_save_directory,
        'cluster': default_cluster_save_directory
    }
}

@app.post("/run-solver")
async def run_solver():
    results = []
    logging.info(f'You are using the SAA for solving')
    
    for epoch in range(calculate_epoch):
    # for IS, NS, MS, SS_SAA in IS_NS_MS_SS_SAA_combinations:
        print(f"计算参数组合: IS={IS}, NS={NS}, MS={MS}, SS_SAA={SS_SAA}, Epoch={epoch}")
        logging.info('--------------------------------------------')
        logging.info(f"计算参数组合: IS={IS}, NS={NS}, MS={MS}, SS_SAA={SS_SAA}, Epoch={epoch}")
        logging.info('--------------------------------------------')

        # 创建图表保存文件夹的名称，包含当前尝试的编号
        graphs_dir_name = f"Graphs_IS={IS}_NS={NS}_MS={MS}_SS_SAA={SS_SAA}_Epoch={epoch}"
        graphs_directory = os.path.join('../SAA_frontend/Graphs', graphs_dir_name)
        
        try:
            for data_process in data_process_methods:
                for cluster in cluster_methods:
                    for sample_generate in sample_generate_methods:
                        for graph_method in graph_methods:
                            method_dir_name = f"{data_process}_{cluster}_{sample_generate}_{graph_method}"
                            method_directory = os.path.join(graphs_directory, method_dir_name)
                            
                            # 在每个方法组合目录下创建 'Samples' 和 'Clusters' 子目录
                            sample_directory = os.path.join(method_directory, 'Samples')
                            cluster_directory = os.path.join(method_directory, 'Clusters')
                            os.makedirs(sample_directory, exist_ok=True)
                            os.makedirs(cluster_directory, exist_ok=True)

                            # 更新graphs_directories字典
                            dir_key = f"{graphs_dir_name}/{method_dir_name}"
                            graphs_directories[dir_key] = {
                                'sample': sample_directory,
                                'cluster': cluster_directory
                            }

                            graphs_store_name = f"{graphs_dir_name}/{method_dir_name}"
                            # Call the solver function with the current combination of parameters
                        # print(f"Executing combination: Data Processing={data_process}, Clustering={cluster}, Sampling={sample_generate}, Dimensionality Reduction={dim_reduction}")
                            print(f"Executing combination: Data Processing={data_process}, Clustering={cluster}, Sampling={sample_generate}, Dimensionality Reduction={graph_method}")
                            logging.info(f"Executing combination: Data Processing={data_process}, Clustering={cluster}, Sampling={sample_generate}, Dimensionality Reduction={graph_method}")
                            try:
                                script_name, opt_f, elapsed_time, gap, Vx, Vy, Output_file = solver(
                                    DATA_PROCESS_METHOD=data_process,
                                    CLUSTER_METHOD=cluster,
                                    SAMPLE_GENERATE_METHOD=sample_generate,
                                    GRAPH_METHOD=graph_method,
                                    IS=IS,
                                    NS=NS,
                                    MS=MS,
                                    SS_SAA=SS_SAA,
                                    Graphs_sample_save_directory=sample_directory,
                                    Graphs_cluster_save_directory=cluster_directory,
                                    Input_file=Input_data_path,
                                    Output_file=Output_data_path,
                                    gurobi_opt=gurobi_opt,
                                    Raw_data_flag=Raw_data_flag,
                                    log_filename=app.state.log_filename,
                                    max_attempts=max_attempts, 
                                    AS=config.AS,
                                    LS=config.LS, 
                                    DATA_PROCESS_PARAMS=DATA_PROCESS_PARAMS, 
                                    GRAPH_CONFIG=GRAPH_CONFIG,
                                    Food_index=current_config['Food_index'],
                                    Medicine_index=current_config['Medicine_index'],
                                    CLUSTER_PARAMS=current_config['CLUSTER_PARAMS']
                                )
                                # 将每一次的执行结果存储到一个字典中
                                result = SolverResult(
                                    script_name= script_name,
                                    opt_f= opt_f,
                                    elapsed_time= elapsed_time,
                                    gap = gap,
                                    Vx = Vx.tolist(),
                                    Vy = Vy.tolist(),
                                    epoch = epoch,
                                    graphs_dir_name = graphs_store_name
                                    # "data_process": data_process,
                                    # "cluster": cluster,
                                    # "sample_generate": sample_generate,
                                    # "graph_method": graph_method
                                )
                                # 将结果字典添加到结果列表中
                                results.append(result)
                                break
                            except Exception as e:
                                print(f"An error occurred while executing the solver with parameters: {e}")
        
        except Exception as e:
            # 发生错误时返回错误信息
            return JSONResponse(content={"message": "求解失败", "error": str(e)}, status_code=500)
                # 使用FastAPI的jsonable_encoder确保数据可以被正确序列化
        
    json_compatible_results = jsonable_encoder(results)
    return {"message": "求解完毕", "results": json_compatible_results}

@app.get("/get-distance-matrix")
async def get_distance_matrix(num_cities: int):
    try:
        df = pd.read_excel(Input_data_path, f'distance', index_col=0)
        matrix = df.iloc[:num_cities, :num_cities].values
        mds = MDS(n_components=2, dissimilarity='precomputed', random_state=1)
        coords = mds.fit_transform(matrix)  # 使用MDS生成二维坐标
        return JSONResponse(content={"coordinates": coords.tolist()})
    except Exception as e:
        return JSONResponse(content={"message": "Error processing the matrix", "error": str(e)}, status_code=500)

@app.get("/get_sample_images")
async def get_sample_images(dir_name: str = 'Default'):
    if dir_name not in graphs_directories:
        raise HTTPException(status_code=404, detail="Directory not found")
    sample_images = os.listdir(graphs_directories[dir_name]['sample'])
    return {
        "sample_images": [
            f"/Graphs/{dir_name}/Samples/{img}" for img in sample_images
        ]
    }

@app.get("/get_cluster_images")
async def get_cluster_images(dir_name: str = 'Default'):
    if dir_name not in graphs_directories:
        raise HTTPException(status_code=404, detail="Directory not found")
    cluster_images = os.listdir(graphs_directories[dir_name]['cluster'])
    return {
        "cluster_images": [
            f"/Graphs/{dir_name}/Clusters/{img}" for img in cluster_images
        ]
    }

@app.post("/save_facility_and_resource_cost")
async def save_facility_cost(data: CostData):
    facility_cost_data = {
        'small': {'CF': data.small_facility_cf, 'U': data.small_facility_u},
        'medium': {'CF': data.medium_facility_cf, 'U': data.medium_facility_u},
        'large': {'CF': data.large_facility_cf, 'U': data.large_facility_u}
    }

    # Create resource cost data structure
    resource_cost_data = {
        'water': {'V': data.water_v, 'CP': data.water_cp, 'CT': data.water_ct, 'CH': data.water_ch, 'G': data.water_g},
        'food': {'V': data.food_v, 'CP': data.food_cp, 'CT': data.food_ct, 'CH': data.food_ch, 'G': data.food_g},
        'medical': {'V': data.medicine_v, 'CP': data.medicine_cp, 'CT': data.medicine_ct, 'CH': data.medicine_ch, 'G': data.medicine_g}
    }

    # 打印数据
    print("Facility Cost Data:", facility_cost_data)
    print("Resource Cost Data:", resource_cost_data)

    # 记录数据
    logging.info('--------------------------------------------')
    logging.info(f'New Facility Cost: {facility_cost_data}')
    logging.info(f'New Resource Cost: {resource_cost_data}')
    logging.info('--------------------------------------------')
    df_facility_cost = pd.DataFrame(facility_cost_data)
    df_resource_cost = pd.DataFrame(resource_cost_data)
    # Save to Excel file
    with pd.ExcelWriter(Generate_data_path) as writer:
        df_facility_cost.to_excel(writer, sheet_name='facility_cost')
        df_resource_cost.to_excel(writer, sheet_name='resource_cost')
    return {"message": "Facility&Resource Cost data saved successfully"}

@app.post("/generate_scenario")
async def generate_scenario(data: ScenarioData):
    global Raw_data_flag, Input_data_path
    # Create city names for columns and rows
    city_names = [f'City_{i}' for i in range(data.num_cities)]
    scenario_names = [f'Scenario_{s}' for s in range(data.num_scenarios)]
    
# 使用 print 打印信息
    print(f"Number of cities: {data.num_cities}")
    print(f"Minimum distance: {data.min_distance} km")
    print(f"Maximum distance: {data.max_distance} km")
    print(f"Minimum population: {data.min_population}")
    print(f"Maximum population: {data.max_population}")
    print(f"Number of scenarios: {data.num_scenarios}")
    print(f"Realistic: {data.realistic}")

    # 使用 logging 记录相同的信息
    logging.info('--------------------------------------------')
    logging.info(f"Number of cities: {data.num_cities}")
    logging.info(f"Minimum distance: {data.min_distance} km")
    logging.info(f"Maximum distance: {data.max_distance} km")
    logging.info(f"Minimum population: {data.min_population}")
    logging.info(f"Maximum population: {data.max_population}")
    logging.info(f"Number of scenarios: {data.num_scenarios}")
    logging.info(f"Realistic: {data.realistic}")
    logging.info('--------------------------------------------')

    distance_matrix = generate_distance_matrix(data.num_cities, data.min_distance, data.max_distance)
    population = generate_population(data.num_cities, data.min_population, data.max_population)
    affected_population = calculate_affected_population(data.num_cities, data.num_scenarios, population, distance_matrix, data.realistic)

    # 保存至 Excel 文件
    with pd.ExcelWriter(Generate_data_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        pd.DataFrame(distance_matrix, index=city_names, columns=city_names).to_excel(writer, sheet_name='distance', index=True)
        pd.DataFrame(population, index=city_names, columns=['population']).to_excel(writer, sheet_name='population', index=True)
        pd.DataFrame(affected_population, index=scenario_names, columns=city_names).to_excel(writer, sheet_name='scenario', index=True)

    Raw_data_flag = False
    Input_data_path = Generate_data_path

    # return {"population": population, "affected_population": affected_population, "message": "New Scenario data saved successfully" }
    return {"message": "New Scenario data saved successfully" }

async def handle_log_file(websocket, log_file_path):
    try:
        with open(log_file_path, "r") as file:
            file.seek(0, os.SEEK_END)  # 移动到文件末尾
            while True:
                line = file.readline()
                if line:
                    await websocket.send_text(line)
                else:
                    # 如果没有新内容，稍作等待
                    await asyncio.sleep(0.1)
    except Exception as e:
        logging.error(f"log thread: {str(e)}")

def start_handle_log_file(websocket, log_file_path):
    asyncio.run(handle_log_file(websocket, log_file_path))

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    log_file_path = app.state.log_filename  # 确保这个路径已经正确设置

    # 创建并启动专门用于读取日志文件和发送WebSocket消息的线程
    log_thread = Thread(target=start_handle_log_file, args=(websocket, log_file_path))
    log_thread.start()

    try:
        # 主WebSocket线程保持开放状态，直到连接断开
        while True:
            await asyncio.sleep(1)  # 模拟等待，实际上不做任何事情，只是保持连接
    except WebSocketDisconnect:
        logging.info("WebSocket connection was closed by the client.")
    finally:
        await websocket.close()
        log_thread.join()


# 如果你希望建立一个可以直接运行的 FastAPI 应用，你还需要定义一个入口点
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)