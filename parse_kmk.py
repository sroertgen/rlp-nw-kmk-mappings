from rdflib import Graph, URIRef, RDF, Literal
from rdflib.namespace import SKOS, DCTERMS
import json

g_kmk = Graph()
g_kmk.parse("./data/kmk-digitale-kompetenzen.ttl")

with open("./data/kmk-digital-competency-rp-nw.json") as f:
    rp_nw_data = json.load(f)["get"]

def parse_id(_id: str):
    if len(_id) > 5:
        _id = _id[4:]
        n = 2
        notations = [_id[i:i+n] for i in range(0, len(_id), n)]
        notations = "".join([item.replace("0", "") + "." for item in notations])
        # print(notations)
        return notations
    else:
        return ""

for i,item in enumerate(rp_nw_data):
    item["notation"] = parse_id(item["id"])




for s, p , o in g_kmk:
    if p == SKOS.prefLabel:
        notation = o.value.split(" ")[0]
        match = next(((i, item) for i, item in enumerate(rp_nw_data) if item["notation"] == notation), None)
        if not match:
            print("error, did not find", o)
        rp_nw_data[match[0]]["kmk_match"] = s


g_rlp = Graph()
g_nw = Graph()

rlp = URIRef("http://rlp.de/50")
nw = URIRef("http://nw.de/50")

def build_graph(uri, file_name):
    g = Graph()
    for item in rp_nw_data:
        if item["id"] == "50":
            g.add((uri, RDF.type, SKOS.ConceptScheme))
            if uri == rlp:
                g.add((uri, DCTERMS.title, Literal(item["mapping_description_RP"], lang="de")))
            else:
                g.add((uri, DCTERMS.title, Literal(item["mapping_description_NW"], lang="de")))

            g.add((uri, SKOS.note, Literal(item["mapping_id_RP"], lang="de")))
            g.add((uri, SKOS.exactMatch, URIRef("http://w3id.org/kim/kmk-vocabs/digitalisierungsbezogene-kompetenzen/")))
            continue
        elif item["id"] == "5099":
            continue
        else:
            item_uri = URIRef(uri + item["id"])
            g.add((item_uri, RDF.type, SKOS.Concept))
            if uri == rlp:
                g.add((item_uri, SKOS.prefLabel, Literal(item["mapping_description_RP"], lang="de")))
                g.add((item_uri, SKOS.note, Literal(item["mapping_description_RP"], lang="de")))
                g.add((item_uri, SKOS.relatedMatch, URIRef(nw + item["id"])))
            else:
                g.add((item_uri, SKOS.prefLabel, Literal(item["mapping_description_NW"], lang="de")))
                g.add((item_uri, SKOS.note, Literal(item["mapping_description_NW"], lang="de")))
                g.add((item_uri, SKOS.relatedMatch, URIRef(rlp + item["id"])))

            g.add((item_uri, SKOS.notation, Literal(item["notation"])))
            g.add((item_uri, SKOS.exactMatch, item["kmk_match"]))
            g.add((item_uri, SKOS.inScheme, uri))
            # broader, narrower, etc vom kmk graphen ableiten
            for p, o in g_kmk.predicate_objects(subject=item["kmk_match"]):
                # find broader, narrower and topConceptOf of o in rlp_nw_data
                if p == SKOS.broader:
                    rlp_broader = next((e for e in rp_nw_data if e.get("kmk_match", None) == o), None)
                    g.add((item_uri, SKOS.broader, URIRef(uri + rlp_broader["id"])))
                if p == SKOS.narrower:
                    rlp_narrower = next((e for e in rp_nw_data if e.get("kmk_match", None) == o), None)
                    g.add((item_uri, SKOS.narrower, URIRef(uri + rlp_narrower["id"])))
                if p == SKOS.topConceptOf:
                    # rlp_topConceptOf = next((e for e in rp_nw_data if e.get("kmk_match", None) == o), None)
                    g.add((item_uri, SKOS.topConceptOf, URIRef(uri)))



    g.bind("skos", SKOS)
    g.bind("dct", DCTERMS)

    g.serialize(f"./{file_name}.ttl")

build_graph(rlp, "rlp")
build_graph(nw, "nw")