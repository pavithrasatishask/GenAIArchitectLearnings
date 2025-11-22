# kg/neo4j_client.py
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

def get_driver():
    if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
        raise RuntimeError("Neo4j credentials missing in .env")
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def create_page_node(tx, page_num, excerpt, source="TamilBook"):
    tx.run("MERGE (p:Page {page:$page}) SET p.excerpt=$excerpt, p.source=$source",
           page=page_num, excerpt=excerpt, source=source)

def link_topic_page(tx, topic, page_num):
    tx.run("MERGE (t:Topic {name:$topic}) MERGE (p:Page {page:$page}) MERGE (t)-[:EXPLAINED_ON]->(p)",
           topic=topic, page=page_num)

def query_graph_for_topic(topic_text, limit=100):
    driver = get_driver()
    q = """
    MATCH (t:Topic)
    WHERE toLower(t.name) CONTAINS toLower($text)
    OPTIONAL MATCH (t)-[r]-(n)
    RETURN t, r, n LIMIT $limit
    """
    nodes = {}
    edges = []
    with driver.session() as session:
        res = session.run(q, text=topic_text, limit=limit)
        for rec in res:
            tnode = rec.get("t")
            rel = rec.get("r")
            nnode = rec.get("n")
            if tnode:
                tid = f"Topic::{tnode.id}"
                nodes[tid] = {"id": tid, "label": tnode.get("name"), "type": "Topic", "props": dict(tnode)}
            if nnode:
                labels = list(nnode.labels) if hasattr(nnode, "labels") else []
                nlabel = labels[0] if labels else "Node"
                nid = f"{nlabel}::{nnode.id}"
                nodes[nid] = {"id": nid, "label": nnode.get("name") or nnode.get("excerpt") or nlabel, "type": nlabel, "props": dict(nnode)}
            if rel and tnode and nnode:
                src = f"Topic::{tnode.id}"
                dst = f"{list(nnode.labels)[0]}::{nnode.id}" if hasattr(nnode, "labels") and list(nnode.labels) else f"Node::{nnode.id}"
                edges.append({"source": src, "target": dst, "type": type(rel).__name__})
    driver.close()
    return {"nodes": list(nodes.values()), "edges": edges}
