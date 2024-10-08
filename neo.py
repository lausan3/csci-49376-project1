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
    finally:
        app.close()


query_neo4j_model()
