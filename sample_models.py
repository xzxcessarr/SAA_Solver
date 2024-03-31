import numpy as np

# # 需要的输入数据
# demand = ...  # 需求数据，假设是一个NumPy数组
# cluster_labels = ...  # KMeans聚类的结果标签数组
# cluster_num = ...  # 分层抽样的层数
# IS = ...  # 需求数据的维度

# # 分层随机抽样
# stratified_sample_indices = stratified_random_sampling(demand, cluster_labels, cluster_num, IS)

# # 简单随机抽样
# simple_sample_indices = simple_random_sampling(cluster_labels)

# # 基于抽样索引获取需求数据样本
# stratified_demand_sample = demand[stratified_sample_indices, :]
# simple_demand_sample = demand[simple_sample_indices, :]

def stratified_random_sampling(demand, cluster_labels, cluster_num, IS):
    #Stratified random sampling
    sample = []

    standard = np.zeros((cluster_num, 1))
    temp_num = np.zeros((cluster_num, 1))
    for i in np.unique(cluster_labels):
        cluster_each = np.argwhere(cluster_labels == i)
        cluster_each = cluster_each.reshape(1, -1).squeeze(0).tolist()
        demand_sample = np.zeros((len(cluster_each), IS))
        for s in range(len(cluster_each)):
            for j in range(IS):
                demand_sample[s, j] = demand[int(cluster_each[s]), j]
        # determine scenario number for each sample by standard deviation
        mean_sample = np.mean(demand_sample, axis=0)
        temp_std = 0
        # calculate standard deviation
        standard[i] = np.sqrt(sum(sum(np.square(demand_sample - mean_sample.T))) / len(cluster_each))
        temp_num[i] = standard[i] * len(cluster_each)

    for i in np.unique(cluster_labels):
        cluster_each = np.argwhere(cluster_labels == i)
        cluster_each = cluster_each.reshape(1, -1).squeeze(0).tolist()
        pick_num = np.rint(cluster_num * len(cluster_each) * standard[i] / sum(temp_num))
        pick_num = pick_num.astype(np.int32)[0]

        if pick_num == 0:
            continue
        elif pick_num == 1:
            temp = np.random.choice(len(cluster_each), 1, replace=False)
            sample.append(cluster_each[temp[0]])
        else:
            temp = np.random.choice(len(cluster_each), pick_num, replace=False)
            for j in range(pick_num):
                sample.append(cluster_each[temp[j]])
    return sample, "Stratified"
    
def simple_random_sampling(cluster_labels):
    # randomly select one from each group
    sample = []
    
    for i in np.unique(cluster_labels):
        cluster_each = np.argwhere(cluster_labels == i)
        cluster_each = cluster_each.reshape(1, -1).squeeze(0).tolist()
        temp = np.random.choice(len(cluster_each), 1, replace=False)
        sample.append(cluster_each[temp[0]]) 
    return sample, "Simple"

class SampleGenerator:
    def __init__(self, method, params):
        self.method = method
        self.params = params

    def generate(self, data, labels, cluster_num):
        if self.method == 'Simple':
            return simple_random_sampling(labels)
        elif self.method == 'Stratified':
            return stratified_random_sampling(data, labels, cluster_num, **self.params)
        else:
            raise ValueError('未知的样本生成方法: {}'.format(self.method))