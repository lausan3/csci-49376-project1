import sys
import pandas as pd

from dotenv import get_key, dotenv_values
from neo4j import GraphDatabase, RoutingControl

loaded_env = dotenv_values()

if not loaded_env:
    sys.exit("Could not load .env")

NEO4J_CONNECT_PASS = loaded_env["NEO4J_CONNECT_PASS"]

URI = "neo4j+s://f9e8a043.databases.neo4j.io"
AUTH = ("neo4j", NEO4J_CONNECT_PASS)
DATASET_PATH = "./Data/"


class Neo:

    def __init__(self):
        self.driver = GraphDatabase.driver(uri=URI, auth=AUTH)

    def __del__(self):
        self.driver.close()

    def create_nodes_in_graph(self):

        skipped_header = False

        with (self.driver.session() as session):
            with open(DATASET_PATH + "nodes.tsv") as f:
                for line in f:
                    if not skipped_header:
                        skipped_header = True
                        continue

                    line_items = line.split('\t')

                    id_string = line_items[0]
                    id_no_type = id_string.split('::')[1]
                    name = line_items[1]
                    cell_type = line_items[2].rstrip('\n')

                    # Node creation code
                    query = self.create_node_query(id_string, id_no_type, name, cell_type)
                    result = session.run(query)
                    created_node = result.consume().counters.nodes_created > 0

                    if created_node:
                        print(f"Successfully created node {id_no_type} of type {cell_type}")
                    else:
                        print(f"Failed to create node {id_no_type}. It may exist already.")

    def create_node_query(self, id_raw: str, id_no_type: str, name: str, cell_type: str) -> str:
        # The MERGE Cypher command does what the SQL CREATE IF NOT EXISTS does.
        return (f'MERGE (n:{cell_type} {{ name: "{name}", id_raw: "{id_raw}", id: "{id_no_type}" }}) '
                f'RETURN n ')

    def test_connect(self):
        """
        Test the connection to the remote Neo4j Aura server.
        Will throw an exception if it could not find the server.
        """
        info = self.driver.get_server_info()

        if info:
            print(f"Connected to Neo4j at {info.address}")

    def close(self):
        self.driver.close()


def query_neo4j_model():
    app = Neo()

    try:
        app.test_connect()
        app.create_nodes_in_graph()
    finally:
        app.close()


query_neo4j_model()
