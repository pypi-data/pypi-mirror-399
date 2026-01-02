# omnidoc/rag/graph_linker.py

import uuid
from typing import List, Dict


def link_chunks(chunks: List[Dict]) -> Dict:
    """
    Produces graph-ready chunk relationships.
    """

    nodes = []
    edges = []

    for idx, chunk in enumerate(chunks):
        node_id = str(uuid.uuid4())

        chunk["_node_id"] = node_id
        nodes.append({
            "id": node_id,
            "type": "chunk",
            "intent": chunk["intent"],
            "confidence": chunk["confidence"],
        })

        # Sequential relationship
        if idx > 0:
            edges.append({
                "from": chunks[idx - 1]["_node_id"],
                "to": node_id,
                "relation": "NEXT",
            })

        # Semantic relationship
        if chunk["intent"] == "metric":
            edges.append({
                "from": node_id,
                "to": "VALUE_NODE",
                "relation": "MEASURES",
            })

    return {
        "nodes": nodes,
        "edges": edges,
    }
