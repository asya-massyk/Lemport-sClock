import uuid
from typing import List, Dict

from scheduler.abstract.abstract_node import AbstractNode
from scheduler.core.action import Action
from scheduler.core.mailbox import Mailbox
from scheduler.core.node_response import NodeResponse

class EchoNode(AbstractNode):
    """Echo алгоритм — відполірований"""

    def __init__(self, node_id: uuid.UUID, neighbors: List[uuid.UUID], is_initiator: bool = False):
        self.node_id = node_id
        self.mailbox = Mailbox()
        self.neighbors = neighbors

        self.parent: uuid.UUID | None = None
        self.received = 0
        self.degree = len(neighbors)

        self.is_initiator = is_initiator
        self.decided = False
        self.sent_to: set[uuid.UUID] = set()

    def process_action(self, message: Action) -> NodeResponse:
        # ❗ Ігноруємо після завершення
        if self.decided:
            return NodeResponse([])

        data = message.data
        msg_type = data.get("type")
        sender = data.get("from")

        outgoing: List[Action] = []

        # 🚀 Ініціатор
        if msg_type == "init" and self.is_initiator:
            print(f"Ініціатор {self.node_id} запускає хвилю Echo")

            for r in self.neighbors:
                act = Action({"type": "wave", "from": self.node_id}, r, uuid.uuid4())
                outgoing.append(act)
                self.sent_to.add(r)

            return NodeResponse(outgoing)

        if msg_type != "wave" or sender is None:
            return NodeResponse([])

        self.received += 1

        if self.parent is None and not self.is_initiator:
            self.parent = sender

        # 📤 Розсилка
        for r in self.neighbors:
            if r != sender and r not in self.sent_to:
                act = Action({"type": "wave", "from": self.node_id}, r, uuid.uuid4())
                outgoing.append(act)
                self.sent_to.add(r)

        # ✅ Завершення
        if self.received == self.degree:
            if not self.is_initiator and self.parent is not None:
                if self.parent not in self.sent_to:
                    act = Action({"type": "wave", "from": self.node_id}, self.parent, uuid.uuid4())
                    outgoing.append(act)
                    self.sent_to.add(self.parent)
            else:
                self.decided = True
                print(f"*** ECHO: Node {self.node_id} DECIDED! ***")

        return NodeResponse(outgoing)

class TreeNode(AbstractNode):
    """Хвильовий алгоритм Tree — відполірована версія"""

    def __init__(self, node_id: uuid.UUID, neighbors: List[uuid.UUID]):
        self.node_id = node_id
        self.mailbox = Mailbox()
        self.neighbors = neighbors

        self.parent: uuid.UUID | None = None
        self.received_from: set[uuid.UUID] = set()
        self.sent_to: set[uuid.UUID] = set()

        self.decided = False
        self.is_initiator = False

    def process_action(self, message: Action) -> NodeResponse:
        # ❗ Ігноруємо все після завершення
        if self.decided:
            return NodeResponse([])

        data = message.data
        msg_type = data.get("type")
        sender = data.get("from")

        outgoing: List[Action] = []

        # 🚀 Старт
        if msg_type == "start":
            self.is_initiator = True
            print(f"Ініціатор Tree {self.node_id} запускає хвилю")

            for r in self.neighbors:
                act = Action({"type": "wave", "from": self.node_id}, r, uuid.uuid4())
                outgoing.append(act)
                self.sent_to.add(r)

            return NodeResponse(outgoing)

        if msg_type != "wave" or sender is None:
            return NodeResponse([])

        # 📥 Отримали повідомлення
        self.received_from.add(sender)

        if self.parent is None and not self.is_initiator:
            self.parent = sender

        # 📤 Розсилка дітям (без дублів)
        for r in self.neighbors:
            if r != self.parent and r not in self.sent_to:
                act = Action({"type": "wave", "from": self.node_id}, r, uuid.uuid4())
                outgoing.append(act)
                self.sent_to.add(r)

        # ✅ Перевірка завершення
        expected = len(self.neighbors) - (1 if self.parent is not None else 0)

        if len(self.received_from) >= expected:
            self.decided = True

            if self.is_initiator:
                print(f"*** TREE: Node {self.node_id} (ініціатор) DECIDED! ***")
            else:
                print(f"*** TREE: Node {self.node_id} DECIDED! ***")

                if self.parent:
                    act = Action({"type": "wave", "from": self.node_id}, self.parent, uuid.uuid4())
                    outgoing.append(act)

        return NodeResponse(outgoing)

# Для сумісності
CurrentNode = EchoNode