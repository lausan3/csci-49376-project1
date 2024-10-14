import os
import sys

from neo import Neo
from modeltypes import *

class App:
    def run(self):
        model_input = input("Hello there! Which type of NoSQL database would you like to use?\n"
                        "\t1. Graph/Neo4j\n"
                        "\t2. Document\n"
                        "Input: ")
        cls()

        if model_input == "1":
            _input_query(ModelType.NEO4J)
        elif model_input == "2":
            _input_query(ModelType.DOCUMENT)
        else:
            print("Incorrect input. Please choose 1 or 2.")
            print("")
            self.run()


def _input_query(model_type: ModelType):
    query_input = input("You've chosen " + ("Neo4j" if model_type == ModelType.NEO4J else "Document") + ". Which query would you like to do?\n"
                        "\t1. Given a disease's id, get its name, genes that cause it, drugs that treat it, and areas it localizes in.\n"
                        "\t2. Given a disease's id, get the names of drugs that indirectly treat it.\n"
                        "Input: ")
    cls()

    app = Neo() if model_type == ModelType.NEO4J else Neo()  # Replace the second Neo() with Document class when implemented

    if query_input == '1':
        disease_id = input("You have selected query 1. Please input the ID of the disease you want to query for.\nDisease ID: ")
        print("")

        app.query1(disease_id)
    elif query_input == '2':
        disease_id = input("You have selected query 2. Please input the ID of the disease you want to query for.\nDisease ID: ")
        print("")

        app.query2(disease_id)
    else:
        print("Incorrect input. Please choose 1 or 2.")
        print("")

        _input_query(model_type)

    _continue_query(model_type)



def _continue_query(model_type: ModelType):
    continue_input = input("Would you like to continue (Yes/No)?\n").lower()

    if continue_input == 'yes' or continue_input == 'y':
        cls()
        _input_query(model_type)
    else:
        sys.exit(1)

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')
