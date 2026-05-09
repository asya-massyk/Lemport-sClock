import uuid
from abc import abstractmethod
from collections.abc import Generator
from typing import List, Dict, Any, Tuple

from scheduler.core.action import Action
from scheduler.core.node_response import NodeResponse
from scheduler.core.mailbox import Mailbox


class AbstractNode(Generator):

    neighbors: List[uuid.UUID]
    mailbox: Mailbox
    node_id: uuid.UUID

    @abstractmethod
    def process_action(self, message: Action) -> NodeResponse:
        pass

    @abstractmethod
    def get_routing_table(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def start_algo(self) -> List[Tuple[uuid.UUID, dict]]:
        pass

    def start(self):
        pass

    def send(self, value: Action) -> NodeResponse:
        if value is not None:
            return self.process_action(value)
        return NodeResponse([])

    def throw(self, typ, val=None, tb=None):
        raise NotImplementedError()