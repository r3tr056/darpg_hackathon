
import numpy as np
from ml_deploy.topic_cluster.search.tree_utils import TreeNode, create_tree
from scipy.spatial.distance import cosine

def find_node_by_category_code(root_node, category_code):
    if root_node.category_code == category_code:
        return root_node
        
    for child in root_node.children:
        found_node = find_node_by_category_code(child, category_code)
        if found_node:
            return found_node
        
def calculate_similarity(vec1, vec2):
    sim = 1 - cosine(vec1, vec2)
    return sim
    

class TopicMapper:
    """ Keep track of Topic Mappings """

    def __init__(self, topics: List[int]):
        base_topics = np.array(sorted(set(topics)))
        topics = base_topics.copy().reshape(-1, 1)
        self.mappings_ = np.hstack([topics.copy(), topics.copy()]).tolist()

    def get_mappings(self, original_topics: bool = True):
        if original_topics:
            mappings = np.array(self.mappings_)[:, [0, -1]]
            mappings = dict(zip(mappings[:, 0], mappings[:, 1]))
        else:
            mappings = np.array(self.mappings_)[:, [-3, -1]]
            mappings = dict(zip(mappings[:, 0], mappings[:, 1]))
        return mappings
    
    def add_mappings(self, mappings):
        for topics in self.mappings_:
            topic = topics[-1]
            if topic in mappings:
                topics.append(mappings[topic])
            else:
                topics.append(-1)

    def add_new_topics(self, mappings):
        length = len(self.mappings_[0])
        for key, value in mappings.items():
            to_append = [key] + ([None] * (length - 2)) + [value]
            self.mappings_.append(to_append)

    def _create_topic_model():
        pass

    def __init__(self):
        self.topic_tree = []

    def create_tree(self):
        self.topic_root = create_tree()

    def similarity_search(self, predicted_topics_embeddings, tree):
        stack = [(tree, 1.0, None)]
        best_similarity = -1
        best_match_node = None
        best_match_children = []

        while stack:
            node, parent_sim, parent_node = stack.pop()
            node_sim = calculate_similarity(document_embeddings, node.category_emb)
            combined_sim = node_sim * parent_sim

            if combined_sim > best_similarity:
                best_similarity = combined_sim
                best_match_node = node
                best_match_children = [child for child in node.children]

            for child in reversed(node.children):
                stack.append((child, node_sim, node))

        return best_similarity, best_match_node, best_match_children

    def search(self, document):
        document_embeddings = np.array(encoding_model.encode(self.category))
        best_sim, best_match_node, best_match_children = self.similarity_search(document_embeddings, self.topic_tree)
        return best_sim, best_match_node, best_match_children
    
    def determine_topic(self, document):
        best_topic, similarity = self.search(document, self.topic_trees[0])
        return best_topic, similarity
    

    
    def add_new_topic(parent_node, category, category_code, stage, org_code):
        
        new_node = TreeNode(category, category_code, stage, org_code)
        parent_node.add_child(new_node)