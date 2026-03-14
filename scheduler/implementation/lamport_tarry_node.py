import uuid
from typing import List, Dict, Any

from scheduler.core.action import Action
from scheduler.core.node_response import NodeResponse
from scheduler.implementation.tarry_node import TarryNode


class LamportTarryNode(TarryNode):
    def __init__(self, node_id: uuid.UUID, neighbors: List[uuid.UUID]):
        super().__init__(node_id, neighbors)
        self.lamport_clock = 0

    def process_action(self, message: Action) -> NodeResponse:
        # Receive event (Lamport rule)
        received_ts = message.data.get('lamport_clock', 0)
        self.lamport_clock = max(self.lamport_clock, received_ts) + 1

        self.visited += 1
        new_message = self.process_message(message)
        if new_message is None:
            print(f"Node {self.node_id} | Lamport: {self.lamport_clock} | FINISHED")
            return NodeResponse([])

        # Send event
        self.lamport_clock += 1
        receiver = list(new_message.keys())[0]
        offer = new_message[receiver]
        offer['lamport_clock'] = self.lamport_clock

        print(f"Node {self.node_id} | Lamport: {self.lamport_clock} | SEND to {receiver}")
        return NodeResponse([Action(offer, receiver, uuid.uuid4())])