import numpy as np
from sklearn.decomposition import TruncatedSVD

def apply_pca(demand, n_components=0.99):
    from sklearn.decomposition import PCA
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
    return pca_demand, pca.n_components_

def apply_tsne(demand, n_components=2, perplexity=30.0, random_state=0):
    from sklearn.manifold import TSNE
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

def apply_truncated_svd(data, n_components=0.99):
    from sklearn.decomposition import TruncatedSVD
    """
    应用TruncatedSVD进行降维。
    
    参数:
    data -- 待降维的数据，应为二维NumPy数组或类似数组的数据结构。
    n_components -- 保留的方差比例。默认为0.99，即保留99%的方差。
    
    返回:
    svd_result -- TruncatedSVD降维后的数据。
    n_components -- 选择的成分数。
    """
    if not 0 < n_components <= 1:
        raise ValueError("n_components must be a float in the range (0, 1].")
    
    # 初始化TruncatedSVD，这里我们先指定一个较大的n_components
    svd = TruncatedSVD(n_components=min(data.shape)-1)
    svd.fit(data)
    
    # 计算累积可解释方差
    cumulative_variance = np.cumsum(svd.explained_variance_ratio_)
    # 找到超过阈值的成分数
    n_components_selected = np.argmax(cumulative_variance >= n_components) + 1
    
    # 使用找到的成分数重新拟合TruncatedSVD
    svd = TruncatedSVD(n_components=n_components_selected)
    svd_result = svd.fit_transform(data)
    
    return svd_result, n_components_selected

