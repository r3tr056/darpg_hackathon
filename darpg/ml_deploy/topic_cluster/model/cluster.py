import numpy as np
from sklearn.cluster import KMeans

from .base import BaseMLModel

class KMeansClustering(BaseMLModel):
    def __init__(self, k:int, model=KMeans):
        super(KMeansClustering, self).__init__()
        self.k = k
        self.cluster_model = model(self.k)
    
    def predict(self, embeddings: np.ndarray):
        labels = self.cluster_model.predict(embeddings)
        return labels

    def fit(self, embeddings: np.ndarray):
        self.cluster_model.fit_transform(embeddings)
        labels = self.cluster_model.labels_
        return labels
    
def depth_first_cluster(node, epsilon, min_samples):
    if not node.children:
        return
    
    embeddings = [child.category_emb for child in node.children]
    cluster_labels = dbscan_cluster(embeddings, epsilon, min_samples)

    for child, label in zip(node.chidlren, cluster_labels):
        child.cluster_label = label

    for child in node.children:
        depth_first_cluster(child, epsilon, min_samples)


def dbscan_cluster(embeddings, epsilon, min_samples):
    dbscan = DBSCAN(eps=epsilon, min_samples=min_samples, metric='cosine')
    cluster_labels = dbscan.fit_predict(embeddings)
    return cluster_labels