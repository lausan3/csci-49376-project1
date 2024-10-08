from enum import Enum


def main():
    model_type = ModelType.NEO4J if input("Please input 1 if you want to model the hetionet dataset using Neo4j."
                                           "\nInput anything else if you want to model using a document database.") == '1' else ModelType.DOCUMENT

    print(model_type)

    # Call modelling code depending on what the model_type enum is.

class ModelType(Enum):
    NEO4J = 1
    DOCUMENT = 2

if __name__ == '__main__':
    main()