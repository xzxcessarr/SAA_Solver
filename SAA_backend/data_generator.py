# -*- coding: utf-8 -*-
"""
SAA_Solver
==========

This module is part of the SAA_Solver project and contains the implementation of Data Generator.

Author: cessarr
Date Created: 2024-04-20
License: MIT License

Description:
------------
此部分为算例数据生成模块
"""
import numpy as np

def generate_distance_matrix(num_cities, min_distance, max_distance):
    """
    生成随机距离矩阵。

    参数说明：
    - num_cities: 城市数量。
    - min_distance: 最小距离。
    - max_distance: 最大距离。

    功能描述：
    为指定数量的城市生成一个对称的距离矩阵，其中每个城市间的距离是随机确定的，介于最小距离和最大距离之间。
    矩阵中的[i][j]元素表示城市i与城市j之间的距离，且距离值是随机生成的整数。

    返回值：
    返回一个num_cities x num_cities的矩阵，表示所有城市之间的距离。
    """
    # 初始化距离矩阵
    distance_matrix = np.zeros((num_cities, num_cities))
    for i in range(num_cities):
        for j in range(i+1, num_cities):
            # 生成随机距离
            distance = np.rint(np.random.uniform(min_distance, max_distance))
            distance_matrix[i][j] = distance
            distance_matrix[j][i] = distance
    return distance_matrix

def generate_population(num_cities, min_population, max_population):
    """
    生成城市人口数。

    参数说明：
    - num_cities: 城市数量。
    - min_population: 最小人口数。
    - max_population: 最大人口数。

    功能描述：
    为指定数量的城市生成一个数组，其中每个元素表示一个城市的人口数。人口数是在最小人口数和最大人口数之间随机确定的。

    返回值：
    返回一个长度为num_cities的数组，每个元素表示一个城市的人口数。
    """
    populations = np.random.randint(min_population, max_population + 1, num_cities)
    return populations

def calculate_affected_population(num_cities, num_scenarios, populations, distance_matrix, realistic=True):
    """
    计算受影响的人口。

    参数说明：
    - num_cities: 城市数量。
    - num_scenarios: 场景数量。
    - populations: 各城市的人口数组。
    - distance_matrix: 城市间的距离矩阵。
    - realistic: 是否使用现实模型来计算受影响的人口。

    功能描述：
    根据不同的飓风登陆场景，计算每个场景下各个城市的受影响人口。可以选择使用基于距离和飓风等级的现实模型，或是使用不基于距离的简化模型。

    详细功能：
    - 如果realistic为True，使用距离矩阵和飓风等级来确定每个城市的受影响人口。距离越近和飓风等级越高的城市受影响越大。
    - 如果realistic为False，则随机生成受影响的城市和受影响程度。

    返回值：
    返回一个num_scenarios x num_cities的矩阵，每个元素表示在对应场景下一个城市的受影响人口。
    """
    W1, W2 = 0.5, 0.5
    hurricane_levels = [1, 2, 3, 4, 5]
    hurricane_probabilities = [0.4, 0.2, 0.2, 0.15, 0.05]
    level_distribution = np.random.choice(hurricane_levels, num_scenarios, p=hurricane_probabilities)
    landing_cities = np.random.randint(0, num_cities, num_scenarios)
    
    affected_populations = np.zeros((num_scenarios, num_cities))
    
    for s in range(num_scenarios):
        level = level_distribution[s]
        landing_city = landing_cities[s]
        
        if realistic:
            # Realistic approach: Use distance matrix
            for i in range(num_cities):
                distance = distance_matrix[landing_city, i]
                if distance <= 200:
                    DFi_s = 1
                elif distance <= 400:
                    DFi_s = 0.8
                elif distance <= 500:
                    DFi_s = 0.5
                else:
                    DFi_s = 0
                affected_populations[s, i] = np.rint(populations[i] * (W1 * DFi_s + W2 * (level / 5)))
        else:
            # Unrealistic approach: Randomly generate affected populations
            affected_cities = np.random.choice(num_cities, np.random.randint(1, num_cities), replace=False)
            for i in affected_cities:
                DFi_s = np.random.choice([0, 0.5, 0.8, 1], p=[0.25, 0.25, 0.25, 0.25])
                affected_populations[s, i] = np.rint(populations[i] * (W1 * DFi_s + W2 * (level / 5)))
    
    return affected_populations

# if __name__ == "__main__":
#     # Assumed parameters from the frontend
#     num_cities = 40
#     min_distance = 100
#     max_distance = 1000
#     num_scenarios = 500
#     min_population = 10000
#     max_population = 50000
#     facility_cost_data = {
#         'small': {'CF': 19600, 'U': 36400},
#         'medium': {'CF': 188400, 'U': 408200},
#         'large': {'CF': 300000, 'U': 780000}
#     }

#     resource_cost_data = {
#         'water': {'V': 144.6, 'CP': 647.7, 'CT': 0.3, 'CH': 129.54, 'G': 6477},
#         'food': {'V': 83.33, 'CP': 5420, 'CT': 0.04, 'CH': 1084, 'G': 54200},
#         'medical': {'V': 1.16, 'CP': 140, 'CT': 0.00058, 'CH': 28, 'G': 1400}
#     }

#     # Generate data
#     distance_matrix = generate_distance_matrix(num_cities, min_distance, max_distance)
#     populations = generate_population(num_cities, min_population, max_population)
#     affected_populations = calculate_affected_population(num_cities, num_scenarios, populations, distance_matrix, realistic=False)

#     # Create city names for columns and rows
#     city_names = [f'City_{i}' for i in range(num_cities)]
#     scenario_names = [f'Scenario_{s}' for s in range(num_scenarios)]

#     # Create DataFrames
#     df_distance = pd.DataFrame(distance_matrix, index=city_names, columns=city_names)
#     df_population = pd.DataFrame(populations, columns=['population'], index=city_names)
#     df_affected_population = pd.DataFrame(affected_populations, columns=city_names, index=scenario_names)
#     df_facility_cost = pd.DataFrame(facility_cost_data)
#     df_resource_cost = pd.DataFrame(resource_cost_data)

#     # Save to Excel file
#     with pd.ExcelWriter('generated_data.xlsx') as writer:
#         df_distance.to_excel(writer, sheet_name='distance')
#         df_population.to_excel(writer, sheet_name='population')
#         df_affected_population.to_excel(writer, sheet_name='scenario')
#         df_facility_cost.to_excel(writer, sheet_name='facility_cost')
#         df_resource_cost.to_excel(writer, sheet_name='resource_cost')

