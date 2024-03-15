import pandas as pd
import numpy as np

from ml_deploy.apps import encoding_model

EXCEL_FILE = 'category_mapping.xlsx'
SHEET_NAME = 'Sheet2'


class TreeNode:
    def __init__(self, category, category_code, stage, org_code):
        self.category = category
        self.category_emb = None
        self.category_code = category_code
        self.stage = stage
        self.org_code = org_code
        self.children = []
        self.documents = []
        self.cluster_labels = None

    def add_child(self, child):
        self.children.append(child)

    def add_document(self, document):
        self.documents.append(document)

    def generate_embeddings(self):
        self.category_emb = np.array(encoding_model.encode(self.category))

def create_tree(excel_file=EXCEL_FILE, sheet_name=SHEET_NAME):
    tree = {}
    df = pd.read_excel(excel_file, sheet_name)

    for index, row in df.iterrows():
        subject_code = row['Code']
        parent_subject_code = row['ParentCode']

        node = TreeNode(
            category=row['Description'],
            category_code=subject_code,
            stage=row['Stage'],
            org_code=row['OrgCode']
        )

        node.generate_embeddings()

        if subject_code not in tree:
            tree[subject_code] = node

        # update the parent info for the child node
        if parent_subject_code is not pd.NA:
            if parent_subject_code not in tree:
                tree[parent_subject_code] = TreeNode(category=None, category_code=parent_subject_code, stage=None, org_code=None)
            tree[parent_subject_code].add_child(node)

    root_nodes = [code for code, node in tree.items() if not node.children]
    artificial_root = TreeNode(category='TopicRoot', category_code='Root', stage='Root', org_code=None)
    for root in root_nodes:
        artificial_root.add_child(tree[root])

    return artificial_root

