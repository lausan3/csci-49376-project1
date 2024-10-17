import argparse
from queries import query_disease, find_new_treatments

def main():
    parser = argparse.ArgumentParser(description="HetioNet MongoDB")
    parser.add_argument('--disease', help="Query disease information by ID")
    parser.add_argument('--new-treatments', help="Find potential new treatments")

    args = parser.parse_args()

    if args.disease:
        result = query_disease(args.disease)
        print(f"THIS IS INFORMATION OF THE DISEASE: {result}")

    if args.new_treatments:
        result = find_new_treatments(args.new_treatments)
        print(f"POTENTIAL NEW TREATMENTS: {result}")

if __name__ == "__main__":
    main()