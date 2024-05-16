from pydantic import BaseModel
from typing import List, Dict, Any

class CostData(BaseModel):
    small_facility_cf: float
    small_facility_u: float
    medium_facility_cf: float
    medium_facility_u: float
    large_facility_cf: float
    large_facility_u: float
    water_v: float
    water_cp: float
    water_ct: float
    water_ch: float
    water_g: float
    food_v: float
    food_cp: float
    food_ct: float
    food_ch: float
    food_g: float
    medicine_v: float
    medicine_cp: float
    medicine_ct: float
    medicine_ch: float
    medicine_g: float

class ScenarioData(BaseModel):
    num_cities: int
    min_distance: float
    max_distance: float
    min_population: int
    max_population: int
    num_scenarios: int
    realistic: bool

# 定义请求模型
class EchartsDataRequest(BaseModel):
    cities: int
    scenes: int


class ParameterModel(BaseModel):
    IS: int
    NS: int
    MS: int
    SS_SAA: int
    data_process_methods: List[str]
    cluster_methods: List[str]
    sample_generate_methods: List[str]
    graph_methods: List[str]
    max_attempts: int
    calculate_epoch: int

# 创建 Pydantic 模型以确保所有数据都是可序列化的
class SolverResult(BaseModel):
    script_name: str
    opt_f: float
    elapsed_time: float
    gap: float
    Vx: List[List[int]]
    Vy: List[List[int]]
    epoch: int
    graphs_dir_name :str

# 定义一个模型来传递参数
class ConfigUpdateRequest(BaseModel):
    CLUSTER_PARAMS: Dict[str, Any]
    GRAPH_PROCESS_METHOD: str
    # 添加其他需要更新的参数
    # n_clusters: int
    Water_index: float
    Food_index: float
    Medicine_index: float
    variance_ratio: float

class AnalyzerParams(BaseModel):
    data_process_method: str
    cluster_method: str
