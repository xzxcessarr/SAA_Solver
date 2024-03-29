import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

def apply_pca(demand, n_components=0.99):
    """
    应用PCA进行降维。
    
    参数:
    data -- 待降维的数据，应为二维NumPy数组。
    n_components -- 保留的成分数或解释的方差比例。默认为0.95，即保留95%的方差。
    
    返回:
    pca_result -- PCA降维后的数据。
    """
    pca = PCA(n_components=n_components)
    pca_demand = pca.fit_transform(demand)
    return pca_demand

def apply_tsne(data, n_components=3, perplexity=30.0, random_state=0):
    """
    应用t-SNE进行降维。
    
    参数:
    data -- 待降维的数据，应为二维NumPy数组。
    n_components -- 降维后的维数。t-SNE通常用于将数据降至2维或3维以便可视化。
    perplexity -- t-SNE的复杂度参数，建议取值在5到50之间。默认为30。
    random_state -- 随机种子用于可重复性。默认为0。
    
    返回:
    tsne_result -- t-SNE降维后的数据。
    """
    tsne = TSNE(n_components=n_components, perplexity=perplexity, random_state=random_state)
    tsne_demand = tsne.fit_transform(demand)
    return tsne_demand