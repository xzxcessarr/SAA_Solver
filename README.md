# SAA-Solver求解器

本代码遵循MIT协议开源，主要参考下面两篇论文实现：

[1]Shaolong Hu, Zhijie Sasha Dong, Rui Dai. A machine learning based sample average approximation for supplier selection with option contract in humanitarian relief. Transportation Research Part E: Logistics and Transportation Review. 2024, Volume 186: 103531.

[2]胡少龙,范婷睿.基于机器学习的样本均值近似算法求解应急物资配置问题[J].管理现代化,2022,42(3):32-38.



## 系统框架图

![系统原理图](https://raw.githubusercontent.com/xzxcessarr/SAA_Solver/main/%E7%B3%BB%E7%BB%9F%E5%8E%9F%E7%90%86%E5%9B%BE.jpg)



## 具体代码说明

前端启动方法为使用至少18及以上版本的nodejs，并使用yarn或npm下载所需的组件库，之后通过`yarn dev`或`npm run dev`启动服务即可

后端启动方法为首先创建python虚拟环境后`pip install -r requirements.txt`下载所需的python库组件，然后使用`uvicorn fastapiTest:app --host 0.0.0.0 --reload`启动即可，这是使用uvicorn启动的方法

上面启动后都请注意检查端口占用情况，如果占用了直接修改前后端的端口即可

Redis数据库推荐使用至少Redis5的版本，默认端口安装启动`redis-server`即可，相关创建逻辑均已调试好并提供了三种Redis数据存储与读取加载接口，注意一一对应的逻辑，如果不想使用请注释掉`solver_model`脚本中的`two_stage_sp_model`和`solver`函数内部的`read_data_from_redis`接口，解除`read_data`的原有注释即可



### 后端代码文件说明

fastapiTest.py

这是系统的主入口和核心控制模块，基于FastAPI框架构建。它定义了一系列的API接口，用于接收前端的请求并调用相应的服务模块进行处理。主要功能包括:

数据上传与处理:提供数据文件上传接口，并调用data_generator模块生成模拟数据。

算法参数选择:提供接口供前端选择数据处理、聚类、抽样等算法，并传递给solver_model模块执行优化。

结果展示:提供接口供前端查询和下载优化结果，并调用plugins模块进行可视化渲染。

日志管理:提供WebSocket接口，实时推送后端计算日志到前端。

配置管理:定义并管理系统的全局配置，如聚类参数、数据处理参数等，并提供接口供前端修改和重置配置。

BaseModel.py

这个文件定义了多个Pydantic模型类，用于接口数据的校验和序列化。如CostData用于设施和资源成本数据，ScenarioData用于场景生成参数，ParameterModel用于算法参数等。这些模型规定了前端传入参数和后端返回结果的数据格式，提高了系统的健壮性和可维护性。

data_generator.py

这个文件主要用于生成模拟数据，包括距离矩阵、城市人口、受灾人口等。它提供了一系列的数据生成函数，可以根据前端传入的参数(如城市数量、距离范围、人口范围等)动态生成不同规模和分布的数据集。生成的数据可以直接保存为Excel文件。

data_preprocess.py

这个文件主要包含数据预处理和降维的功能。它提供了四种降维方法:PCA、TruncatedSVD、FactorAnalysis和t-SNE。其中，t-SNE主要用于数据可视化，不推荐用于聚类前的降维。文件中定义了一个DataProcessor类，通过指定降维方法和参数来初始化，并提供apply_reduction方法来执行降维操作。

config.py

这个文件用于存储系统的默认配置，包括模型参数、算法选择、数据处理参数等。它使用Python字典的形式组织参数，并提供了参数说明，方便用户理解和修改。文件中还对不同的降维方法、聚类方法的选择提供了一些建议和考虑因素。

clustering_param_analyzer.py

这个文件提供了聚类参数的自动选择功能。它定义了analyze_clustering_params函数，对给定的聚类方法和数据集，使用网格搜索和交叉验证选择最优参数组合。函数返回最佳参数和推荐的参数范围。

cluster_models.py

这个文件实现了多种聚类算法，如K-means、谱聚类、DBSCAN等。它定义了统一的ClusteringMethod类，封装了不同的聚类方法，供solver_model模块调用。每种聚类算法都有对应的函数，接受数据和参数，返回聚类标签和方法名称。

sample_method.py

这个文件实现了分层随机抽样和简单随机抽样两种方法，用于从聚类结果中抽取代表性样本。它定义了SampleGenerator类，封装了抽样方法，供solver_model调用。文件中还提供了stratified_random_sampling函数，用于执行分层抽样。

plugins.py

这个文件提供了一些辅助功能，如从Excel读取数据、将结果保存到Excel、将数据缓存到Redis、绘制聚类结果图等。它定义了一系列工具函数，如read_data、append_df_to_excel、plot_cluster等，供其他模块调用，提高了代码的复用性。

solve_models.py

这个文件实现了主要的优化求解逻辑。它定义了getsol、renew等求解函数，用于求解SAA样本问题和原始问题。文件中使用了Gurobi优化器，求解了两阶段随机规划模型。同时，文件还定义了solver函数，作为算法模块的统一入口，调用数据处理、聚类分析、样本生成等模块，协调各模块的执行。

 

### 前端代码文件说明
App.vue

这是应用的主组件，定义了整个应用的布局和导航逻辑。它使用了Element Plus的布局组件(如el-header、el-main等)来构建页面结构。在顶部，有一个单选按钮组(el-radio-group)用于在不同的页面(数据选择、参数设置、计算结果)之间导航。主内容区域使用了Vue Router的<router-view>组件来动态渲染不同的页面组件。底部有一个控制面板，用于显示/隐藏日志组件(LogsWebSocket.vue)。

该组件还使用了Vue的组合式API和TypeScript。ref函数用于创建响应式数据(如step和showLogs)，watch函数用于监视step的变化并相应地更新路由。useRouter钩子用于访问Vue Router实例。这种组合式API的使用使得代码更加模块化和可重用。

LogsWebSocket.vue

这个组件负责与后端建立WebSocket连接，接收服务器推送的日志数据，并实时显示在页面上。它使用了Vue的组合式API(如ref、onMounted、onUnmounted等)来管理组件的生命周期和状态。

logs是一个响应式数据，用于存储接收到的日志。maxLogCount定义了最大的日志条数，超过这个数量时，旧的日志会被移除以维持性能。组件在mounted时建立WebSocket连接，并在unmounted时关闭连接，这体现了Vue生命周期钩子的使用。

这个组件还使用了computed函数来创建一个计算属性formattedLogs，它会自动将logs数组转化为格式化的字符串以便显示。watchEffect函数用于监视logs的变化，并自动滚动到最新的日志，这体现了Vue的响应式和副作用追踪机制。

graphsStore.ts

这是一个使用Pinia库创建的状态存储，用于管理应用中的图像数据。Pinia是一个专为Vue设计的状态管理库，它使用TypeScript编写，支持Vue的组合式API，并具有良好的类型推断。

imagesByDir是存储的主要状态，它是一个以目录名为键，以包含样本图像和聚类图像URL的对象为值的映射。fetchImages是一个action方法，用于从服务器获取指定目录下的图像URL并更新状态。

这个状态存储展示了如何使用Pinia来管理全局状态，以及如何在Pinia中使用TypeScript来获得类型安全。它还展示了如何在Pinia中定义异步action，并在action中使用axios发送HTTP请求。

generateStore.ts

这是另一个使用Pinia创建的状态存储，用于管理数据生成页面的表单数据。它定义了两个状态(costParams和scenarioParams)和两个mutation(setCostParams和setScenarioParams)，用于更新这些状态。

这个状态存储展示了如何使用Pinia来管理局部状态，如表单数据。通过在组件中引入和使用这个状态存储，可以方便地在不同的表单组件之间共享和同步数据。

echartsStore.ts

这也是一个使用Pinia创建的状态存储，用于管理ECharts组件的参数。它定义了一个名为params的状态和一个名为updateEchartsParams的mutation。

这个状态存储可以被ECharts相关的组件引入和使用，从而实现参数的集中管理和动态更新。当需要更新ECharts参数时，组件只需要调用updateEchartsParams mutation即可，无需直接修改状态，这符合Pinia的最佳实践。

distanceStore.ts

这是一个用于管理距离数据的Pinia状态存储。它定义了一个名为coordinates的状态，表示一组二维坐标；还定义了一个名为updateCoordinates的action，用于更新这个状态。

这个状态存储使用了TypeScript的接口来定义状态的类型，这提供了良好的类型检查和自动完成支持。在需要使用距离数据的组件中，可以引入这个状态存储，并调用updateCoordinates action来更新数据。

DataConfig.vue

这是数据选择页面的主要组件。它提供了两种数据选择方式:生成数据和上传数据。当选择生成数据时，页面会显示一个分步表单，引导用户填写成本数据和场景数据；当选择上传数据时，页面会显示一个文件上传组件(UploadExcel.vue)。

这个组件使用了Vue的条件渲染(v-if)来控制不同视图的显示。它还使用了Vue Router的编程式导航(useRouter和router.push)来处理页面跳转。此外，它还展示了如何在Vue组件中引入和使用其他组件(如CostForm.vue和ScenarioForm.vue)。

ConfigSolver.vue

这是参数设置页面的主要组件。它允许用户配置求解器的各种参数，如城市数量、场景数量、样本数量等。这些参数通过一个响应式的表单(el-form)来收集和管理。

这个组件还包含了几个子组件，如ConfigSelect.vue、EchartsScatterDraw.vue等，用于渲染参数选择器和ECharts图表。它展示了如何在Vue组件中使用Element Plus的表单组件(如el-form-item、el-input-number等)来构建交互式表单。

此外，这个组件还定义了几个方法(如sendParameters、runSolver等)来处理表单提交和求解器调用。这些方法使用了axios库来发送HTTP请求，并使用Element Plus的消息组件(ElMessage)来显示反馈。

ConfigSelect.vue

这是一个参数选择器组件，用于配置各种算法参数，如数据处理方法、聚类方法、样本生成方法等。这些参数通过下拉选择器(el-select)和数字输入框(el-input-number)来设置。

这个组件使用了Vue的v-model指令来实现表单控件和组件状态之间的双向绑定。它还使用了watch函数来监视某些状态的变化，并相应地更新其他状态，以保证数据的一致性。

在提交参数时，这个组件会调用父组件(ConfigSolver.vue)传递下来的sendParameters方法。这展示了Vue组件之间的通信方式之一:通过props传递数据和方法。

ClusterParamsAnalyzer.vue

这是一个聚类参数分析器组件，用于分析和推荐不同聚类方法的最佳参数。它允许用户选择数据处理方法，并为每种聚类方法提供了一个可折叠的表单(el-collapse)，用于设置和分析参数。

这个组件使用了axios来发送HTTP请求，并使用Element Plus的消息组件(ElMessage)来显示分析结果。在显示结果时，它使用了Vue的渲染函数(h)来动态创建消息内容，这展示了Vue的另一个强大功能。

此外，这个组件还展示了如何在Vue组件中使用Pinia状态存储。通过引入useParameterStore，组件可以访问和修改全局的参数状态，实现组件之间的数据共享。

 