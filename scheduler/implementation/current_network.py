import uuid
from typing import List, Dict

from scheduler.abstract.abstract_network import AbstractNetwork
from scheduler.core.action import Action
from scheduler.implementation.node import EchoNode, TreeNode


class EchoNetwork(AbstractNetwork):
    NUMBER_OF_NODES = 7

    def __init__(self):
        ids = [uuid.uuid4() for _ in range(self.NUMBER_OF_NODES)]
        edges = self._get_edges(ids)

        self.nodes = []
        initiator_id = ids[0]

        for node_id in ids:
            is_initiator = (node_id == initiator_id)
            node = EchoNode(node_id, edges[node_id], is_initiator)
            
            # Агресивне очищення всіх старих повідомлень
            if hasattr(node.mailbox, 'inbox'):
                node.mailbox.inbox.clear()
            if hasattr(node.mailbox, 'outbox'):
                node.mailbox.outbox.clear()
            
            self.nodes.append(node)

        super().__init__(self.nodes)

        # Запуск тільки ініціатора
        init_action = Action({"type": "init"}, initiator_id, uuid.uuid4())
        for node in self.nodes:
            if node.node_id == initiator_id:
                node.mailbox.add_inbox_action(init_action)
                print(f"Ініціатор запущений: {node.node_id}")
                break

    def _get_edges(self, ids: List[uuid.UUID]) -> Dict[uuid.UUID, List[uuid.UUID]]:
        return {
            ids[0]: [ids[1], ids[2], ids[3]],
            ids[1]: [ids[0], ids[4]],
            ids[2]: [ids[0], ids[5]],
            ids[3]: [ids[0], ids[6]],
            ids[4]: [ids[1]],
            ids[5]: [ids[2]],
            ids[6]: [ids[3]]
        }


class TreeNetwork(AbstractNetwork):
    NUMBER_OF_NODES = 7

    def __init__(self):
        ids = [uuid.uuid4() for _ in range(self.NUMBER_OF_NODES)]
        edges = self._get_edges(ids)

        self.nodes = []
        initiator_id = ids[0]   # перший вузол — ініціатор

        for node_id in ids:
            node = TreeNode(node_id, edges[node_id])
            # Очищення черг
            if hasattr(node.mailbox, 'inbox'):
                node.mailbox.inbox.clear()
            if hasattr(node.mailbox, 'outbox'):
                node.mailbox.outbox.clear()
            self.nodes.append(node)

        super().__init__(self.nodes)

        # Запускаємо тільки ініціатора
        init_action = Action({"type": "start"}, initiator_id, uuid.uuid4())
        for node in self.nodes:
            if node.node_id == initiator_id:
                node.mailbox.add_inbox_action(init_action)
                print(f"Ініціатор Tree запущений: {initiator_id}")
                break

    def _get_edges(self, ids: List[uuid.UUID]) -> Dict[uuid.UUID, List[uuid.UUID]]:
        return {
            ids[0]: [ids[1], ids[2], ids[3]],
            ids[1]: [ids[0], ids[4]],
            ids[2]: [ids[0], ids[5]],
            ids[3]: [ids[0], ids[6]],
            ids[4]: [ids[1]],
            ids[5]: [ids[2]],
            ids[6]: [ids[3]]
        }


# Вибір алгоритму
CurrentNetwork = EchoNetwork      # Echo
#CurrentNetwork = TreeNetwork    # Tree