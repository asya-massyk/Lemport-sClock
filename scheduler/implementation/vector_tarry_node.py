import uuid
from typing import List, Dict, Any

from scheduler.core.action import Action
from scheduler.core.node_response import NodeResponse
from scheduler.implementation.tarry_node import TarryNode


class VectorTarryNode(TarryNode):
    def __init__(self, node_id: uuid.UUID, neighbors: List[uuid.UUID]):
        super().__init__(node_id, neighbors)
        self.vector_clock: Dict[uuid.UUID, int] = {node_id: 0}

    def process_action(self, message: Action) -> NodeResponse:
        # Receive event
        received_vc = message.data.get('vector_clock', {})
        for nid, val in received_vc.items():
            self.vector_clock[nid] = max(self.vector_clock.get(nid, 0), val)
        self.vector_clock[self.node_id] += 1

        self.visited += 1
        new_message = self.process_message(message)
        if new_message is None:
            print(f"Node {self.node_id} | Vector: {self.vector_clock} | FINISHED")
            return NodeResponse([])

        # Send event
        self.vector_clock[self.node_id] += 1
        receiver = list(new_message.keys())[0]
        offer = new_message[receiver]
        offer['vector_clock'] = self.vector_clock.copy()

        print(f"Node {self.node_id} | Vector: {self.vector_clock} | SEND to {receiver}")
        return NodeResponse([Action(offer, receiver, uuid.uuid4())])