# -*- coding: utf-8 -*-
"""
Configuration and data reading method for the two-stage SP model
"""

import pandas as pd
import numpy as np
import os

# Parameters
IS = 20  # Set of locations
AS = 3  # Set of item types
LS = 3  # Set of size categories
NS = 100  # Scenario样本总量
SS_SAA = 10  # Scenario number of samples单个样本容量
MS = 10  # Sample number样本数量
Water = 1
Food = 0.25
Medicine = 0.125
Input_file = 'input/data.xlsx'
Output_file = 'result.xlsx'
Graphs_sample_save_directory = "./Graphs"

# 检查目录是否存在，如果不存在则创建
if not os.path.exists(Graphs_sample_save_directory):
    os.makedirs(Graphs_sample_save_directory)


def read_data(filename=Input_file):
    """
    Reads data from an Excel file and returns parameters and data arrays.

    Parameters:
        filename (str): Name of the Excel file.

    Returns:
        tuple: CF, U, H, V, CP, CH, G, CT, D, pr, demand
    """
    scenario_sheet_name = f'scenario_{IS}'
    probability_column_name = f'w{NS // 100}'

    scenario_data = pd.read_excel(filename, scenario_sheet_name)
    main_data = pd.read_excel(filename, 'main_data', header=None)

    # probability
    pr = scenario_data[probability_column_name].to_numpy()

    # demand
    demand = scenario_data.iloc[:NS, 1:IS + 1].to_numpy()
    demand = np.rint(demand * 0.03)
    Dr = np.empty((NS, IS, AS))
    Dr[:, :, 0] = scenario_data.iloc[:NS, 1:IS + 1].to_numpy()
    Dr[:, :, 1] = np.rint((Dr[:, :, 0] * Food))
    Dr[:, :, 2] = np.rint((Dr[:, :, 0] * Medicine))

    # Fixed cost, Storage capacity, volume of items
    CF = main_data.loc[1, 1:3].to_numpy()
    U = main_data.loc[2, 1:3].to_numpy()

    # Distance
    H = main_data.loc[8:(7 + IS), 1:].to_numpy()

    # volume of items
    V = main_data.loc[1, 6:8].to_numpy()
    # Unit procurement price
    CP = main_data.loc[2, 6:8].to_numpy()
    # Unit transportation cost
    CT = main_data.loc[3, 6:8].to_numpy()
    # Unit holding cost
    CH = main_data.loc[4, 6:8].to_numpy()
    # Unit penalty cost
    G = main_data.loc[5, 6:8].to_numpy()

    D = np.zeros((NS, AS, IS))
    for j in range(IS):
        for a in range(AS):
            for s in range(NS):
                D[s, a, j] = np.rint(Dr[s, j, a] * 0.03)

    return CF, U, H, V, CP, CH, G, CT, D, pr, demand
