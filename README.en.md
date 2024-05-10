1. # SAA-Solver

   This code is open-sourced under the MIT license and is mainly implemented with reference to the following two papers:

   [1] Shaolong Hu, Zhijie Sasha Dong, Rui Dai. A machine learning based sample average approximation for supplier selection with option contract in humanitarian relief. Transportation Research Part E: Logistics and Transportation Review. 2024, Volume 186: 103531.

   [2]胡少龙,范婷睿.基于机器学习的样本均值近似算法求解应急物资配置问题[J].管理现代化,2022,42(3):32-38.

   

   ## System Framework Diagram

   ![系统原理图](https://gitee.com/cessarr/SAA_Solver/blob/master/系统原理图.jpg)

   

   ## Specific Code Description

   To start the front-end, use Node.js version 18 or above, and use yarn or npm to download the required component libraries. Then start the service with `yarn dev` or `npm run dev`.

   To start the back-end, first create a Python virtual environment and `pip install -r requirements.txt` to download the required Python library components. Then use `uvicorn fastapiTest:app --host 0.0.0.0 --reload` to start. This is the method of starting with uvicorn.

   After starting the above, please pay attention to the port occupancy situation. If occupied, directly modify the front-end and back-end ports.

   For the Redis database, it is recommended to use at least Redis version 5. Install and start with `redis-server` using the default port. The relevant creation logic has been debugged and three Redis data storage and read-load interfaces are provided. Pay attention to the corresponding logic one by one. If you don't want to use it, please comment out the `read_data_from_redis` interface in the `two_stage_sp_model` and `solver` functions of the `solver_model` script, and uncomment the original `read_data`.

   

   ### Back-end Code File Description

   fastapiTest.py

   This is the main entry and core control module of the system, built on the FastAPI framework. It defines a series of API interfaces for receiving front-end requests and calling corresponding service modules for processing. The main functions include:

   Data upload and processing: Provides data file upload interface and calls the data_generator module to generate simulation data.

   Algorithm parameter selection: Provides interfaces for the front-end to select data processing, clustering, sampling and other algorithms, and passes them to the solver_model module for optimization execution.

   Result display: Provides interfaces for the front-end to query and download optimization results, and calls the plugins module for visualization rendering.

   Log management: Provides WebSocket interface to push back-end computation logs to the front-end in real time.

   Configuration management: Defines and manages the system's global configuration, such as clustering parameters, data processing parameters, etc., and provides interfaces for the front-end to modify and reset the configuration.

   BaseModel.py

   This file defines multiple Pydantic model classes for interface data validation and serialization. For example, CostData is used for facility and resource cost data, ScenarioData is used for scenario generation parameters, ParameterModel is used for algorithm parameters, etc. These models specify the data format of parameters passed in from the front-end and results returned by the back-end, improving the robustness and maintainability of the system.

   data_generator.py

   This file is mainly used to generate simulation data, including distance matrix, city population, affected population, etc. It provides a series of data generation functions that can dynamically generate data sets of different scales and distributions based on parameters passed in from the front-end (such as number of cities, distance range, population range, etc.). The generated data can be directly saved as Excel files.

   data_preprocess.py

   This file mainly includes data preprocessing and dimensionality reduction functions. It provides four dimensionality reduction methods: PCA, TruncatedSVD, FactorAnalysis, and t-SNE. Among them, t-SNE is mainly used for data visualization and is not recommended for dimensionality reduction before clustering. The file defines a DataProcessor class, which is initialized by specifying the dimensionality reduction method and parameters, and provides an apply_reduction method to perform dimensionality reduction operations.

   config.py

   This file is used to store the default configuration of the system, including model parameters, algorithm selection, data processing parameters, etc. It organizes parameters in the form of Python dictionaries and provides parameter descriptions for easy understanding and modification by users. The file also provides some suggestions and considerations for the selection of different dimensionality reduction methods and clustering methods.

   clustering_param_analyzer.py

   This file provides automatic selection of clustering parameters. It defines the analyze_clustering_params function, which uses grid search and cross-validation to select the optimal parameter combination for a given clustering method and dataset. The function returns the best parameters and recommended parameter ranges.

   cluster_models.py

   This file implements various clustering algorithms such as K-means, spectral clustering, DBSCAN, etc. It defines a unified ClusteringMethod class that encapsulates different clustering methods for the solver_model module to call. Each clustering algorithm has a corresponding function that accepts data and parameters and returns cluster labels and method names.

   sample_method.py

   This file implements two methods of stratified random sampling and simple random sampling for extracting representative samples from clustering results. It defines a SampleGenerator class that encapsulates the sampling methods for solver_model to call. The file also provides a stratified_random_sampling function for performing stratified sampling.

   plugins.py

   This file provides some auxiliary functions, such as reading data from Excel, saving results to Excel, caching data to Redis, plotting clustering results, etc. It defines a series of utility functions, such as read_data, append_df_to_excel, plot_cluster, etc., for other modules to call, improving code reusability.

   solve_models.py

   This file implements the main optimization solving logic. It defines solving functions such as getsol, renew, etc., for solving SAA sample problems and original problems. The file uses the Gurobi optimizer to solve the two-stage stochastic programming model. At the same time, the file also defines a solver function as a unified entry point for the algorithm module, calling data processing, cluster analysis, sample generation and other modules to coordinate the execution of each module.

   

   ### Frontend Code File Description

   App.vue

   This is the main component of the application, which defines the layout and navigation logic for the entire app. It uses Element Plus layout components (such as el-header, el-main, etc.) to build the page structure. At the top, there is a radio button group (el-radio-group) used for navigating between different pages (data selection, parameter settings, calculation results). The main content area uses the <router-view> component from Vue Router to dynamically render different page components. At the bottom, there is a control panel for showing/hiding the log component (LogsWebSocket.vue).

   This component also uses Vue's Composition API and TypeScript. The ref function is used to create reactive data (such as step and showLogs), and the watch function is used to monitor changes in step and update the route accordingly. The useRouter hook is used to access the Vue Router instance. The use of this Composition API makes the code more modular and reusable.

   LogsWebSocket.vue

   This component is responsible for establishing a WebSocket connection with the backend, receiving log data pushed by the server, and displaying it on the page in real-time. It uses Vue's Composition API (such as ref, onMounted, onUnmounted, etc.) to manage the component's lifecycle and state.

   logs is a piece of reactive data used to store the received logs. maxLogCount defines the maximum number of log entries. When this number is exceeded, old logs are removed to maintain performance. The component establishes a WebSocket connection when mounted and closes the connection when unmounted, reflecting the use of Vue lifecycle hooks.

   This component also uses the computed function to create a computed property formattedLogs, which automatically converts the logs array into a formatted string for display. The watchEffect function is used to monitor changes in logs and automatically scroll to the latest log, reflecting Vue's reactivity and side effect tracking mechanism.

   graphsStore.ts

   This is a state store created using the Pinia library, used to manage the image data in the application. Pinia is a state management library designed specifically for Vue. It is written in TypeScript, supports Vue's Composition API, and has good type inference.

   imagesByDir is the main state stored. It is a mapping with directory names as keys and objects containing sample image and clustered image URLs as values. fetchImages is an action method used to fetch image URLs from the server for a specified directory and update the state.

   This state store showcases how to use Pinia to manage global state and how to use TypeScript in Pinia for type safety. It also demonstrates how to define asynchronous actions in Pinia and how to use axios to send HTTP requests in actions.

   generateStore.ts

   This is another state store created using Pinia, used to manage the form data of the data generation page. It defines two states (costParams and scenarioParams) and two mutations (setCostParams and setScenarioParams) for updating these states.

   This state store demonstrates how to use Pinia to manage local state, such as form data. By importing and using this state store in components, data can be easily shared and synchronized between different form components.

   echartsStore.ts

   This is also a state store created using Pinia, used to manage the parameters of the ECharts component. It defines a state named params and a mutation named updateEchartsParams.

   This state store can be imported and used by ECharts-related components, thus realizing centralized management and dynamic updating of parameters. When ECharts parameters need to be updated, the component only needs to call the updateEchartsParams mutation, without directly modifying the state, which conforms to Pinia's best practices.

   distanceStore.ts

   This is a Pinia state store for managing distance data. It defines a state named coordinates, representing a set of two-dimensional coordinates, and an action named updateCoordinates for updating this state.

   This state store uses TypeScript interfaces to define the type of the state, providing good type checking and autocomplete support. In components that need to use distance data, this state store can be imported, and the updateCoordinates action can be called to update the data.

   DataConfig.vue

   This is the main component of the data selection page. It provides two ways to select data: generating data and uploading data. When generating data is selected, the page displays a step-by-step form guiding the user to fill in cost data and scenario data. When uploading data is selected, the page displays a file upload component (UploadExcel.vue).

   This component uses Vue's conditional rendering (v-if) to control the display of different views. It also uses Vue Router's programmatic navigation (useRouter and router.push) to handle page jumps. Additionally, it demonstrates how to import and use other components (such as CostForm.vue and ScenarioForm.vue) in a Vue component.

   ConfigSolver.vue

   This is the main component of the parameter setting page. It allows users to configure various parameters of the solver, such as the number of cities, number of scenarios, number of samples, etc. These parameters are collected and managed through a reactive form (el-form).

   This component also contains several child components, such as ConfigSelect.vue, EchartsScatterDraw.vue, etc., used to render parameter selectors and ECharts graphs. It demonstrates how to use Element Plus form components (such as el-form-item, el-input-number, etc.) in a Vue component to build interactive forms.

   Furthermore, this component defines several methods (such as sendParameters, runSolver, etc.) to handle form submission and solver invocation. These methods use the axios library to send HTTP requests and use Element Plus message components (ElMessage) to display feedback.

   ConfigSelect.vue

   This is a parameter selector component used to configure various algorithm parameters, such as data processing methods, clustering methods, sample generation methods, etc. These parameters are set through dropdown selectors (el-select) and number input boxes (el-input-number).

   This component uses Vue's v-model directive to implement two-way binding between form controls and component states. It also uses the watch function to monitor changes in certain states and update other states accordingly to ensure data consistency.

   When submitting parameters, this component calls the sendParameters method passed down from the parent component (ConfigSolver.vue). This demonstrates one of the ways components communicate in Vue: passing data and methods through props.

   ClusterParamsAnalyzer.vue

   This is a clustering parameter analyzer component used to analyze and recommend the best parameters for different clustering methods. It allows users to select data processing methods and provides a collapsible form (el-collapse) for each clustering method to set and analyze parameters.

   This component uses axios to send HTTP requests and uses Element Plus message components (ElMessage) to display analysis results. When displaying results, it uses Vue's render function (h) to dynamically create message content, demonstrating another powerful feature of Vue.

   Moreover, this component also demonstrates how to use the Pinia state store in a Vue component. By importing useParameterStore, the component can access and modify the global parameter state, realizing data sharing between components.
