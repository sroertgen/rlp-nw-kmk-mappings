import json
from rdflib import Graph, RDF, Literal, URIRef
from rdflib.namespace import SKOS, DCTERMS

with open("./data/curriculum-rlp.json") as f:
    rlp = json.load(f)

medienkompass = [item for item in rlp if any(e for e in item if "MedienkomP@" in e["title"]) ]

rlp = URIRef("http://rlp.de/")


def build_graph(raw):
    g = Graph()
    cs_id = next(item for item in raw if item["parent_id"] == None)["id"]
    cs_uri = URIRef(rlp + cs_id)
    for item in raw:
        item_uri = rlp + item["id"]
        if item["parent_id"] == None:
            g.add((item_uri, RDF.type, SKOS.ConceptScheme))
            g.add((item_uri, DCTERMS.title, Literal(item["title"], lang="de")))
            continue
        # Concepts
        g.add((item_uri, RDF.type, SKOS.Concept))
        g.add((item_uri, SKOS.prefLabel, Literal(item["title"], lang="de")))
        g.add((item_uri, SKOS.inScheme, cs_uri))
        if item["parent_id"] == cs_id:
            g.add((item_uri, SKOS.topConceptOf, cs_uri)) 
            g.add((cs_uri, SKOS.hasTopConcept, item_uri))
        else:
            g.add((item_uri, SKOS.broader, URIRef(rlp + item["parent_id"])))

    g.bind("skos", SKOS)
    g.bind("dct", DCTERMS)

    g.serialize(f"./rlp_{cs_id}.ttl")

for item in medienkompass:
    build_graph(item)