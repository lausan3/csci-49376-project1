import sys

from dotenv import dotenv_values
from neo4j import GraphDatabase

loaded_env = dotenv_values()

if not loaded_env:
    sys.exit("Could not load .env")

NEO4J_CONNECT_PASS = loaded_env["NEO4J_CONNECT_PASS"]

URI = "bolt://localhost:7687"
AUTH = ("neo4j", NEO4J_CONNECT_PASS)
DATASET_PATH = "./Data/"


class Neo:

    def __init__(self):
        self.driver = GraphDatabase.driver(uri=URI, auth=AUTH)

    def __del__(self):
        self.driver.close()

    def _create_nodes_in_graph(self):

        with self.driver.session() as session:
            query = (
                "LOAD CSV FROM 'file:///nodes.tsv' AS line FIELDTERMINATOR '\t' "
                "CALL { "
                "   WITH line "
                "   MERGE (:Node{id: line[0], name: line[1], type: line[2]}) "
                "} IN TRANSACTIONS OF 500 ROWS "
            )

            result = session.run(query)
            summary = result.consume()
            nodes_created = summary.counters.nodes_created
            time_elapsed = summary.result_available_after

            if nodes_created > 0:
                print(f"{nodes_created} nodes created in Neo4j database at {self.driver.get_server_info().address}")
            else:
                print("No new nodes created in Neo4j database")

            print(f"Time elapsed: {time_elapsed / 1000} seconds")

    def _create_edges_in_graph(self):

        with self.driver.session() as session:
            # Tried replacing MERGE with CREATE to test how much it affects speed.
            # I was thinking that CREATE would be faster than MERGE because we wouldn't have to do the pattern matching on the relationship,
            # but it ended up only saving 2 seconds when setting 10000 properties.
            # When merging the 1,700,000 total properties, we only save about 5 minutes of runtime.

            # Also, without using the CALL { ... } IN TRANSACTIONS OF ... ROWS paradigm (the new way to do USING PERIODIC COMMITS), I saw
            # a slowdown on read times to 20 relationships created a second, which was going to take HOURS. After switching, there was no slowdown
            # and relationships were being created live to the database as well.
            query = (
                "LOAD CSV FROM 'file:///edges.tsv' AS line FIELDTERMINATOR '\t' " 
                "CALL {  " 
                "    WITH line " 
                "    MATCH (s:Node{id:line[0]})  " 
                "    MATCH (t:Node{id:line[2]})  " 
                "    WITH line, substring(line[1], 1, size(line[1]) - 2) AS relationship, s, t  " 
                "    WITH relationship, s, t,  " 
                "        CASE relationship   " 
                "            WHEN 'r' THEN 'RESEMBLES'   " 
                "            WHEN 'i' THEN 'INTERACTS'   " 
                "            WHEN 'u' THEN 'UPREGULATES'   " 
                "            WHEN 'd' THEN 'DOWNREGULATES'   " 
                "            WHEN 'e' THEN 'EXPRESSES'   " 
                "            WHEN 'a' THEN 'ASSOCIATES'   " 
                "            WHEN 'b' THEN 'BINDS'   " 
                "            WHEN 'c' THEN 'COVARIES'   " 
                "            WHEN 'l' THEN 'LOCALIZES'   " 
                "            WHEN 't' THEN 'TREATS'   " 
                "            WHEN 'p' THEN 'PALLIATES'   " 
                "            WHEN 'r>' THEN 'REGULATES'   " 
                "            ELSE null   " 
                "        END AS relationship_type  " 
                "    WHERE relationship_type IS NOT NULL  " 
                "    MERGE (s)-[r:RELATES{type:relationship_type}]->(t)  " 
                "} IN TRANSACTIONS OF 500 ROWS  "
            )

            result = session.run(query)
            summary = result.consume()
            relationships_created = summary.counters.relationships_created
            time_elapsed = summary.result_available_after

            if relationships_created > 0:
                print(f"{relationships_created} relationships created in Neo4j database at {self.driver.get_server_info().address}")
            else:
                print("No new relationships created in Neo4j database")

            print(f"Time elapsed: {time_elapsed / 1000} seconds")

    def _create_nodes_in_graph_manual_DEPRECATED(self):
        """
        Parses the dataset of nodes individually and creates nodes from them using the Neo4j driver.
        This is much slower and now DEPRECATED in favor of self._create_nodes_in_graph(), which lets Neo4j handle the data parsing instead.
        """

        def create_node_query(id_raw: str, id_no_type: str, name: str, cell_type: str) -> str:
            # The MERGE Cypher command does what the SQL CREATE IF NOT EXISTS does.
            return (f'MERGE (n:{cell_type} {{ name: "{name}", id_raw: "{id_raw}", id: "{id_no_type}" }}) '
                    f'RETURN n ')

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
                    query = create_node_query(id_string, id_no_type, name, cell_type)
                    result = session.run(query)
                    created_node = result.consume().counters.nodes_created > 0

                    if created_node:
                        print(f"Successfully created node {id_string} of type {cell_type}")
                    else:
                        print(f"Failed to create node {id_string}. It may exist already.")

    def _create_edges_in_graph_manual_DEPRECATED(self):
        """
        Parses the dataset of edges individually and creates relationships from them using the Neo4j driver.
        This is much slower and now DEPRECATED in favor of self._create_edges_in_graph(), which lets Neo4j handle the data parsing instead.
        """

        def extract_relationship_from_metaedge(metaedge: str) -> (str, str, str):
            """
            Extract the relationship, source node's code, and target node's code as a tuple in that order.

             Codes are the single capital letters representing the type of node
             e.g. C -> Compound, G -> Gene, ect.

            :param metaedge: A string in the format <SOURCE_CODE><RELATIONSHIP><TARGET_CODE> to be parsed.
            :return: A 3-tuple of strings: (relationship, source, target).
            """
            source_code = metaedge[0]
            target_code = metaedge[-1]
            relationship = metaedge[1:-1]

            match relationship:
                case 'i':
                    return "INTERACTS", source_code, target_code
                case 'u':
                    return "UPREGULATES", source_code, target_code
                case 'e':
                    return "EXPRESSES", source_code, target_code
                case 'd':
                    return "DOWNREGULATES", source_code, target_code
                case 'a':
                    return "ASSOCIATES", source_code, target_code
                case 'b':
                    return "BINDS", source_code, target_code
                case 'c':
                    return "COVARIES", source_code, target_code
                case 'l':
                    return "LOCALIZES", source_code, target_code
                case 't':
                    return "TREATS", source_code, target_code
                case 'p':
                    return "PALLIATES", source_code, target_code
                case 'r':
                    return "RESEMBLES", source_code, target_code
                case 'r>':
                    return "REGULATES", source_code, target_code
                case _:
                    # Tested with sys.exit(), all edges were verified as one of above.
                    print(f"Could not parse relationship {relationship}")
                    return relationship, source_code, target_code

        def create_edge_query(source_id_raw: str, relationship: str, target_id_raw: str) -> str:
            source_type = source_id_raw.split('::')[0]
            target_type = target_id_raw.split('::')[0]

            return (f'MATCH (s:{source_type} {{ id_raw: "{source_id_raw}" }})'
                    f'MATCH (t:{target_type} {{ id_raw: "{target_id_raw}" }})'
                    f'MERGE (s)-[r:{relationship}]->(t)'
                    f'RETURN r')


        skipped_header = False

        with (self.driver.session() as session):
            with open(DATASET_PATH + "edges.tsv") as f:
                for line in f:
                    if not skipped_header:
                        skipped_header = True
                        continue

                    line_items = line.split('\t')

                    source = line_items[0]
                    target = line_items[2].rstrip('\n')
                    metaedge = line_items[1]

                    relationship = extract_relationship_from_metaedge(metaedge)

                    query = create_edge_query(source, relationship[0], target)

                    result = session.run(query)
                    created_edge = result.consume().counters.relationships_created > 0

                    if created_edge:
                        print(f"Successfully created edge {source}-[{relationship[0]}]->{target}")
                    else:
                        print(f"Failed to create edge {source}-[{relationship[0]}]->{target}. It may exist already.")

    def test_connect(self):
        """
        Test the connection to the remote Neo4j Aura server.
        Will throw an exception if it could not find the server.
        """
        self.driver.verify_connectivity()

        print(f"Connected to Neo4j at {URI}!")

    def _reset_graph(self):
        with self.driver.session() as session:
            query = (
                "MATCH (n) DETACH DELETE n"
            )

            session.run(query)

            print("Reset graph complete.")

    def close(self):
        self.driver.close()


def query_neo4j_model():
    app = Neo()

    try:
        app.test_connect()
        app._create_nodes_in_graph()
        app._create_edges_in_graph()
    finally:
        app.close()


query_neo4j_model()
