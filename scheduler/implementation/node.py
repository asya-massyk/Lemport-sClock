import uuid
from typing import List, Tuple

from scheduler.abstract.abstract_node import AbstractNode
from scheduler.core.action import Action
from scheduler.core.mailbox import Mailbox
from scheduler.core.node_response import NodeResponse

from .merlin_sigal import MerlinSigalNode


class Node(AbstractNode):
    def __init__(self, node_id: uuid.UUID, neighbors: List[uuid.UUID]):
        self.node_id = node_id
        self.neighbors = neighbors
        self.mailbox = Mailbox()
        self.algo = MerlinSigalNode(node_id, neighbors)
        self.started = False

    def process_action(self, action: Action) -> NodeResponse:
        if not self.started:
            self.start()
            self.started = True

        data = action.data
        if not isinstance(data, dict) or "sender" not in data or "message" not in data:
            return NodeResponse([])

        sender = data["sender"]
        message = data["message"]

        new_pairs = self.algo.on_receive(sender, message)

        response_actions: List[Action] = []
        for target, msg in new_pairs:
            new_action = Action(
                data={
                    "target": target,
                    "message": msg,
                    "sender": self.node_id
                },
                node_id=target,
                action_id=uuid.uuid4()
            )
            response_actions.append(new_action)

        return NodeResponse(response_actions)

    def start(self):
        if self.started:
            return
        self.started = True
        print(f"Node {str(self.node_id)[:8]}... started")

    def get_routing_table(self):
        return self.algo.get_routing_table()

    def start_algo(self) -> List[Tuple[uuid.UUID, dict]]:
        return self.algo.start()