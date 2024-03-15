import os
import umap

from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from typing import List

import numpy as np

from .autoencoder import AutoEncoder
from .embedding import BERTEmbedding
from .cluster import KMeansClustering
from .lda_model import LDATopicModel
from .topic_mapper import TopicMapper


class TopicClassifier:
    def __init__(self, k=10, bert_embedding_model='bert-base-uncased', dropout=0.3):
        super(TopicClassifier, self).__init__()

        self.seed_topic_list = []

        self.embedding_model = BERTEmbedding(bert_embedding_model)
        self.cluster_model = KMeansClustering(k=k)
        self.umap_model = umap.UMAP()

        self.k = k
        self.num_top_terms = 5

        # LDA stuff
        self.dictionary = None
        self.corpus = None
        self.lda_model = None

        self.topics = []
        self.topic_mapping = TopicMapper(self.topics)


    def vectorize(self, sentences, tokenized_texts):
        vec_lda = self.vectorize(sentences, tokenized_texts, method='LDA')
        vec_bert = self.vectorize(sentences, tokenized_texts, method='BERT')
        vec_ldabert = np.c_[vec_lda * self.gamma, vec_bert]
        self.vec['LDA_BERT_FULL'] = vec_ldabert
        if not self.ae_model:
            self.ae_model = AutoEncoder()
            self.ae_model.fit(vec_ldabert)
        vec = self.ae_model.predict(vec_ldabert)
        return vec

    def _guided_topic_modelling(self, embeddings: np.ndarray):
        """
        Apply guided topic modelling

        Transform the seeded topic to embeddings using the same embedder used for generating document embeddings -> Apply Cosine similarity b/w the embeddings and set labels for documents that are more similar to one of the topic than others.
        """
        seed_topic_list = [" ".join(seed_topic) for seed_topic in self.seed_topic_list]
        topic_embeddings = self.embedding_model.predict(seed_topic_list)
        topic_embeddings = np.vstack([topic_embeddings, embeddings.mean(axis=0)])

        sim_matrix = cosine_similarity(embeddings, topic_embeddings)
        y = [np.argmax(sim_matrix[index]) for index in range(sim_matrix.shape[0])]
        y = [val if val != len(seed_topic_list) else -1 for val in y]

        for seed_topic in range(len(seed_topic_list)):
            indices = [index for index, topic in enumerate(y) if topic == seed_topic]
            embeddings[indices] = np.average([embeddings[indices], topic_embeddings[seed_topic]], weights=[3,1])
        
        return y, embeddings
    
        
    def _cluster_embeddings(self, embeddings):
        """ Cluster reduces embeddingsto find topics """
        self.cluster_model.fit(embeddings)
        cluster_labels = self.cluster_model.cluster_model.labels_
        self.topics = cluster_labels
        self.topic_sizes = len(self.topics)
        return cluster_labels

    def _calculate_ctfidf_representation(sentences, cluster_lables):
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(sentences)

        ctfifg_repr = np.zeros((len(set(cluster_lables)), tfidf_matrix.shape[1]))
        for i, label in enumerate(set(cluster_lables)):
            cluster_indices = np.where(cluster_lables == label)[0]
            cluster_tfidf = tfidf_matrix[cluster_indices].mean(axis=0)
            ctfifg_repr[i] = cluster_tfidf

        return ctfifg_repr

    def _extract_topics(self, ctfidf_representation, num_topics):
        vectorizer = TfidfVectorizer()
        ctfidf_cluster_matrix = vectorizer.fit_transform(ctfidf_representation)

        km = KMeans(n_clusters=num_topics, random_state=42)
        km.fit(ctfidf_cluster_matrix)

        terms = vectorizer.get_feature_names_out()
        sorted_centroids = km.cluster_centers_.argsort()[:, ::-1]

        topics = []
        for i in range(num_topics):
            topic_str = " ".join([terms[ind] for ind in sorted_centroids[i, :self.num_top_terms]])
            topics.append(topic_str)

        self.topics = topics
        return topics

    def _extract_good_docs(self, ctfidf, sentences, topics, nr_samples=500, nr_repr_docs=5, diversity=None):
        pass

    def _reduce_dims(self, embeddings, y=None):
        """ Reduce dimensionality of embeddings using UMAP and train a UMAP model """
        try:
            y = np.array(y) if y is not None else None
            self.umap_model.fit(embeddings, y=y)
        except TypeError:
            self.umap_model.fit(embeddings)

        umap_embeddings = self.umap_model.transform(embeddings)
        return np.nan_to_num(umap_embeddings)
    
    def _map_probablities(self, probabs, original_topics):
        mappings = self.topic_mapping_.get_mappings(original_topics)
        if probabs is not None:
            if len(probabs.shape) == 2:
                mapped_probabs = np.zeros((probabs.shape[0], len(set(mappings.values())) - self._outliers))
                for from_topic, to_topic in mappings.items():
                    if to_topic != -1 and from_topic != -1:
                        mapped_probabs[:, to_topic] += probabs[:, from_topic]
                return mapped_probabs
        return probabs
    
    def _map_predictions(self, predictions):
        mappings = self.topic_mapping_.get_mappings(original_topics=True)
        mapped_predictions = [mappings[prediction] if prediction in mappings else -1 for prediction in predictions]
        return mapped_predictions
    
    def _create_fit_result(self):
        """
        Get information about the documents on which the topic model was trained on
        """
        if df is not None:
            document_info = df.copy()
            document_info["Document"] = sentences
            document_info["Topic"] = self.topics_
        else:
            document_info = pd.DataFrame({"Document": sentences, "Topic": self.topics_})

        topic_info = self.get_topic_info()
        sentence_info = pdf
    
    def fit_transform(self, sentences, embeddings):
        if embeddings is None:
            embeddings = self.embedding_model.predict(sentences)
        
        umap_embeddings = self._reduce_dims(embeddings)
        cluster_labels = self._cluster_embeddings(umap_embeddings, sentences)
        ctfidf_repr = self._calculate_ctfidf_representation(sentences, cluster_labels)
        topics = self._extract_topics(ctfidf_repr, self.k)

        summary_df = self._create_fit_result(sentences, topics)
        return summary_df

    def fit_lda_model(self, sentences: List[str], embeddings: np.ndarray = None, y=None, method='LDA'):
        if not self.lda_model:
            self.lda_model = LDATopicModel(self.k)
        if not embeddings:
            embeddings = self.embedding_model.predict(sentences)
        self.lda_model.fit(embeddings)
        return self.lda_model.predict()