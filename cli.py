import argparse

from neo import Neo
from queries import query_disease, find_new_treatments

def main():
    parser = argparse.ArgumentParser(prog="Hetionet", description="HetioNet MongoDB")
    subparsers = parser.add_subparsers(dest="command")


    parser.add_argument('--disease', help="Query disease information by ID using MongoDB", nargs=1,
                        metavar="disease_id")
    parser.add_argument('--new-treatments', help="Find potential new treatments using MongoDB", nargs=1,
                        metavar="disease_id")

    neo = subparsers.add_parser(name="neo", help="Query a hetionet dataset using a local Neo4j DBMS")

    neo.add_argument('--disease', help="Query disease information by Disease ID. ", type=str, nargs=1,
                     metavar="disease_id")
    neo.add_argument('--new-treatments', help="Find potential new treatments by Disease ID", type=str, nargs=1,
                     metavar="disease_id")

    args = parser.parse_args()

    if not args.command:
        if args.disease:
            result = query_disease(args.disease)
            print(f"THIS IS INFORMATION OF THE DISEASE: {result}")
        elif args.new_treatments:
            result = find_new_treatments(args.new_treatments)
            print(f"POTENTIAL NEW TREATMENTS: {result}")
        else:
            parser.print_help()

    elif args.command == 'neo':
        neo_app = Neo()
        if args.disease:
            neo_app.query1(args.disease[0])
        elif args.new_treatments:
            neo_app.query2(args.new_treatments[0])
        else:
            neo.print_help()

if __name__ == "__main__":
    main()