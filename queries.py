import pymongo
import re

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["hetio_net"]
nodes_collection = db["nodes"]
edges_collection = db["edges"]

def normalize_disease_id(disease_id):
    match = re.match(r'[Dd]isease::([A-Za-z]+):([0-9]+)', disease_id)
    if match:
        normalized_id = f"Disease::{match.group(1)}:{match.group(2)}"
        return normalized_id
    else:
        return None

#Query 1:
def query_disease(disease_id):
    normalized_id = normalize_disease_id(disease_id)
    if not normalized_id:
        return

    disease = nodes_collection.find_one({"_id": normalized_id})
    if not disease:
        print("Not found")
        return

    disease_name = disease['name']

    #Find compounds
    treatments = edges_collection.find({
        "target": normalized_id,
        "metaedge": {"$in": ["CtD", "CpD"]} 
    })

    #Find drug names from compounds
    drugs = [nodes_collection.find_one({"_id": treatment['source']})['name'] for treatment in treatments if nodes_collection.find_one({"_id": treatment['source']})]

    unique_drugs = list(set(drugs))

    #Find genes
    gene_edges = edges_collection.find({
        "source": normalized_id,
        "metaedge": {"$in": ["GcD", "DdG"]}
    })
    genes = [nodes_collection.find_one({"_id": edge['target']})['name'] for edge in gene_edges]

    unique_genes = list(set(genes))

    #Find locations
    anatomy_edges = edges_collection.find({
        "source": normalized_id,
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
def find_new_treatments(disease_id):
    normalized_id = normalize_disease_id(disease_id)
    if not normalized_id:
        return 

    #Find all locations of the disease
    anatomy_edges = list(edges_collection.find({
        "source": normalized_id,
        "metaedge": "DlA"
    }))
    anatomy_locations = [edge['target'] for edge in anatomy_edges]
    unique_locations = list(set(anatomy_locations))
    
    #Find all genes regulated by these locations
    anatomy_regulation_edges = list(edges_collection.find({
        "source": {"$in": unique_locations},
        "metaedge": {"$in": ["AuG", "AdG"]}
    }))
    
    regulated_genes = {}
    for edge in anatomy_regulation_edges:
        gene_id = edge['target']
        anatomy_regulation = edge['metaedge']
        regulated_genes[gene_id] = anatomy_regulation
    
    #Find allexisting drugs
    existing_edges = list(edges_collection.find({
        "target": normalized_id,
        "metaedge": {"$in": ["CtD"]}
    }))
    
    existing_drugs = {edge["source"] for edge in existing_edges}
    print(f"Existing compound {normalized_id}: {existing_drugs}")

    #Find compounds regulate genes in opposite direction
    gene_ids = list(regulated_genes.keys())
    compound_regulation_edges = list(edges_collection.find({
        "target": {"$in": gene_ids},
        "metaedge": {"$in": ["CuG", "CdG"]}
    }))

    potential_new_treatments = set()

    for edge in compound_regulation_edges:
        gene_id = edge['target']
        compound_id = edge['source']
        compound_regulation = edge['metaedge']
        
        if compound_id not in existing_drugs:
            anatomy_regulation = regulated_genes[gene_id]
            
            #Check direction, add to potential treatments
            if (compound_regulation == "CuG" and anatomy_regulation == "AdG") or \
               (compound_regulation == "CdG" and anatomy_regulation == "AuG"):
                compound_name = nodes_collection.find_one({"_id": compound_id})['name']
                potential_new_treatments.add(compound_name)

    return sorted(potential_new_treatments)