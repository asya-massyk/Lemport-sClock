import uuid
from abc import abstractmethod
from collections.abc import Generator
from typing import List

from scheduler.core.action import Action
from scheduler.core.node_response import NodeResponse
from scheduler.core.mailbox import Mailbox


class AbstractNode(Generator):

    neighbors: List[uuid.UUID]
    mailbox: Mailbox
    node_id: uuid.UUID

    @abstractmethod
    def process_action(self, message: Action) -> NodeResponse:
        """Обробка однієї дії (повідомлення)"""
        pass

    def send(self, value: Action) -> NodeResponse:
        if value is not None:
            return self.process_action(value)
        return NodeResponse([])

    def throw(self, typ, val=None, tb=None):
        raise NotImplementedError("throw() must be implemented in concrete node classes")