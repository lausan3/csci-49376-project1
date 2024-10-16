import pymongo
import csv
from pymongo.errors import BulkWriteError

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["hetionet"]

nodes_collection = db["nodes"]
edges_collection = db["edges"]

def insert_nodes(file_path):
    with open(file_path, mode='r') as file:
        tsv_reader = csv.DictReader(file, delimiter="\t")
        nodes = []
        for row in tsv_reader:
            node_id = row['id']
            name = row['name']
            kind = row['kind']

            if node_id and name and kind:
                nodes.append({
                    "_id": node_id,
                    "name": name,
                    "type": kind
                })
        try:
            nodes_collection.insert_many(nodes, ordered=False)  #if ordered=False skips duplicates
        except BulkWriteError as e:
            #handle duplicate key errors and continue
            print(f"Error: {e.details}")
            print(f"Duplicate key")

def insert_edges(file_path):
    with open(file_path, mode='r') as file:
        tsv_reader = csv.DictReader(file, delimiter="\t")
        edges = []
        for row in tsv_reader:
            source = row['source']
            target = row['target']
            metaedge = row['metaedge']

            if source and target and metaedge:
                edges.append({
                    "source": source,
                    "target": target,
                    "metaedge": metaedge
                })
        try:
            edges_collection.insert_many(edges, ordered=False)
        except BulkWriteError as e:
            print(f"Error: {e.details}")
            print(f"Duplicate key")

insert_nodes('nodes.tsv')
insert_edges('edges.tsv')
