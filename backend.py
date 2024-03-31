# -*- coding: utf-8 -*-
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from main import solver  # 假设main.py中包含了solver函数
import shutil
from tempfile import NamedTemporaryFile

app = FastAPI()

@app.post("/solve/")
async def solve(data_process: str = Form(...), cluster: str = Form(...),
                sample_generate: str = Form("Stratified"), 
                dim_reduction: str = Form("3d")):
    if data_process not in data_process_methods or \
       cluster not in cluster_methods or \
       sample_generate not in sample_generate_methods or \
       dim_reduction not in dim_reduction_methods:
        raise HTTPException(status_code=400, detail="Invalid method specified")

    try:
        # 假设solver函数返回计算结果和图片路径
        result, image_path = solver(data_process, cluster, sample_generate, dim_reduction)
        # 创建临时文件以安全地传输图片
        with NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            shutil.copy(image_path, tmp.name)
            tmp_image_path = tmp.name
        
        return {
            "result": result,  # 计算结果
            "image": tmp_image_path  # 图片文件的路径
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 用于发送图片文件的额外路由
@app.get("/images/{image_path}")
async def get_image(image_path: str):
    return FileResponse(path=image_path)