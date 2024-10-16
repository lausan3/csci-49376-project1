import pymongo
import re

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["hetio_net"]
nodes_collection = db["nodes"]
edges_collection = db["edges"]

def normalize_disease_id(disease_id):
    #format and convert
    match = re.match(r'[Dd]isease::([A-Za-z]+):([0-9]+)', disease_id)
    if match:
        normalized_id = f"Disease::{match.group(1)}:{match.group(2)}"
        return normalized_id
    else:
        print(f"Invalid format: {disease_id}")
        return None

#Query 1:
def query_disease(disease_id):
    normalized_disease_id = normalize_disease_id(disease_id)
    if not normalized_disease_id:
        return

    disease = nodes_collection.find_one({"_id": normalized_disease_id})
    if not disease:
        print("Not found")
        return

    disease_name = disease['name']

    #Find compounds
    treatments = edges_collection.find({
        "target": normalized_disease_id,
        "metaedge": {"$in": ["CtD", "CpD"]} 
    })

    #Find drug names from compounds
    drugs = [nodes_collection.find_one({"_id": treatment['source']})['name'] for treatment in treatments if nodes_collection.find_one({"_id": treatment['source']})]

    unique_drugs = list(set(drugs))

    #Find genes
    gene_edges = edges_collection.find({
        "source": normalized_disease_id,
        "metaedge": {"$in": ["GcD", "DdG"]}
    })
    genes = [nodes_collection.find_one({"_id": edge['target']})['name'] for edge in gene_edges]

    unique_genes = list(set(genes))

    #Find locations
    anatomy_edges = edges_collection.find({
        "source": normalized_disease_id,
        "metaedge": {"$in": ["DlA"]}
    })
    anatomy_locations = [nodes_collection.find_one({"_id": edge['target']})['name'] for edge in anatomy_edges]

    unique_anatomy_locations = list(set(anatomy_locations))

    return {
        "DISEASE NAME": disease_name,
        "DRUGS": unique_drugs,
        "GENES": unique_genes,
        "LOCATIONS": unique_anatomy_locations
    }

# Query 2
def find_new_treatments_for_disease(disease_id):
    normalized_disease_id = normalize_disease_id(disease_id)
    if not normalized_disease_id:
        return

    #List all drugs shown already 
    existing_edges = edges_collection.find({
        "target": normalized_disease_id,
        "metaedge": {"$in": ["CtD", "CpD"]}
    })

    existing_drugs = {edge["source"] for edge in existing_edges}

    print(f"EXISTING DRUGS FOR {normalized_disease_id}: {existing_drugs}")

    all_drugs = nodes_collection.find({"kind": "Compound"})

    potential_new_treatments = []

    # Iterate all drugs find potential new treatments check if drug is not already linked to the disease
    for drug in all_drugs:
        drug_id = drug["_id"]
        drug_name = drug["name"]
    
        if drug_id not in existing_drugs:
            potential_new_treatments.append(drug_name)

    return potential_new_treatments