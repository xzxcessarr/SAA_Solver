# -*- coding: utf-8 -*-

from main import solver  # Assuming the solver function's file is named "main.py"

# Define the parameters
data_process_methods = ['pca', 'truncated_svd', 'none']
cluster_methods = [
    'kmeans', 'spectral', 'gmm', 'som'
]
sample_generate_methods = ['Stratified', 'Simple']
dim_reduction_methods = ['2d', '3d']

# Iterate over each combination of parameters and call the solver function
for data_process in data_process_methods:
    for cluster in cluster_methods:
        # for sample_generate in sample_generate_methods:
            # for dim_reduction in dim_reduction_methods:
                # Call the solver function with the current combination of parameters
            # print(f"Executing combination: Data Processing={data_process}, Clustering={cluster}, Sampling={sample_generate}, Dimensionality Reduction={dim_reduction}")
        print(f"Executing combination: Data Processing={data_process}, Clustering={cluster}, Sampling=Stratified")
        try:
            solver(
                data_process,
                cluster,
                "Stratified",
                '3d'
            )
        except Exception as e:
            print(f"An error occurred while executing the solver with parameters: {e}")