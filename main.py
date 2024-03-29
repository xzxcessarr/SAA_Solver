# -*- coding: utf-8 -*-
# 文件名: main.py

from cluster_models.Stratified_SpectralClustering import stratified_spectral_clustering

def main():
    filename = '/input/data.xlsx'  # 数据文件名称
    # 调用子函数
    costs, Vx, Vy, elapsed_time = stratified_spectral_clustering()
    # 在这里可以处理返回的结果，例如打印或保存到文件等

if __name__ == "__main__":
    main()