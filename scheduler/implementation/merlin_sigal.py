import uuid
from math import inf
from typing import Dict, List, Tuple, Optional


class MerlinSigalNode:
    def __init__(self, node_id: uuid.UUID, neighbors: List[uuid.UUID]):
        self.id = node_id
        self.neighbors = neighbors
        self.link_costs: Dict[uuid.UUID, float] = {n: 1.0 for n in neighbors}

        self.routing_table: Dict[uuid.UUID, Tuple[float, Optional[uuid.UUID]]] = {}
        self.routing_table[node_id] = (0.0, None)

    def start(self) -> List[Tuple[uuid.UUID, dict]]:
        actions = []
        for neigh in self.neighbors:
            msg = {
                "type": "DIST_UPDATE",
                "dest": self.id,
                "dist": 0.0,
                "sender": self.id
            }
            actions.append((neigh, msg))
        return actions

    def on_receive(self, sender: uuid.UUID, message: dict) -> List[Tuple[uuid.UUID, dict]]:
        actions = []
        if message.get("type") != "DIST_UPDATE":
            return actions

        dest = message["dest"]
        received_dist = message.get("dist", inf)
        new_dist = received_dist + self.link_costs.get(sender, 1.0)

        current_dist, _ = self.routing_table.get(dest, (inf, None))

        if new_dist < current_dist:
            self.routing_table[dest] = (new_dist, sender)

            for neigh in self.neighbors:
                if neigh != sender:   # уникнення зациклення
                    update = {
                        "type": "DIST_UPDATE",
                        "dest": dest,
                        "dist": new_dist,
                        "sender": self.id
                    }
                    actions.append((neigh, update))

        return actions

    def get_routing_table(self) -> Dict:
        return {
            str(dest): {
                "distance": round(dist, 2),
                "next_hop": str(next_hop)[:8]+"..." if next_hop else "SELF"
            }
            for dest, (dist, next_hop) in self.routing_table.items()
        }