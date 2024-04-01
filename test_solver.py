# -*- coding: utf-8 -*-

from main import solver  # Assuming the solver function's file is named "main.py"
import time

# Define the parameter sets
param_sets = [
    {'IS': 20, 'NS': 100, 'SS_SAA': 10, 'MS': 10},
    {'IS': 20, 'NS': 200, 'SS_SAA': 20, 'MS': 10},
    {'IS': 20, 'NS': 500, 'SS_SAA': 25, 'MS': 10},
    {'IS': 40, 'NS': 100, 'SS_SAA': 10, 'MS': 10},
]

# Define other parameters
data_process_methods = ['pca', 'truncated_svd', 'none']
cluster_methods = [
    'kmeans', 'spectral', 'gmm', 'som'
]

# Iterate over each set of parameters
for param_set in param_sets:
    # Update the configuration for the solver here
    # Assuming `config` is a dictionary-like object that the `solver` function uses
    config = param_set
    
    # Iterate over each combination of the remaining parameters and call the solver function
    for data_process in data_process_methods:
        for cluster in cluster_methods:
            print(f"Executing combination: Data Processing={data_process}, Clustering={cluster}, Sampling=Stratified with params: IS={config['IS']}, NS={config['NS']}, SS_SAA={config['SS_SAA']}, MS={config['MS']}")
            
            # Start timing this combination
            start_time = time.time()
            
            try:
                solver(
                    data_process,
                    cluster,
                    "Stratified",
                    '3d',
                    IS=config['IS'],
                    NS=config['NS'],
                    SS_SAA=config['SS_SAA'],
                    MS=config['MS']
                )
            except Exception as e:
                print(f"An error occurred while executing the solver with parameters: {e}")
            
            # Calculate the elapsed time
            elapsed_time = time.time() - start_time
            print(f"Elapsed time for this combination: {elapsed_time:.2f} seconds\n")