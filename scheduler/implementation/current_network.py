import uuid
from pprint import pprint
from typing import List, Dict

from scheduler.abstract.abstract_network import AbstractNetwork

from typing import List
from scheduler.implementation.node import Node
from scheduler.core.action import Action


class CurrentNetwork(AbstractNetwork):
    NUMBER_OF_NODES = 8

    def __init__(self) -> None:

        self.nodes: List[Node] = []
        ids = [uuid.uuid4() for _ in range(self.NUMBER_OF_NODES)]
        self.__get_edges(ids)

        for node_id in ids:
            neighbors = self.edges[node_id]
            self.nodes.append(Node(node_id, neighbors))

        super().__init__(list(self.nodes))

    def __get_edges(self, ids: List[uuid.UUID]) -> Dict:
        self.edges = {
            ids[0]: [ids[1], ids[2]],
            ids[1]: [ids[0], ids[3], ids[4]],
            ids[2]: [ids[0], ids[5], ids[6], ids[7]],
            ids[3]: [ids[1]],
            ids[4]: [ids[1]],
            ids[5]: [ids[2]],
            ids[6]: [ids[2]],
            ids[7]: [ids[2]]
        }
        pprint(self.edges)
        return self.edges

    def start_merlin_sigal(self):
        """Правильний запуск Merlin-Sigal"""
        print("🚀 Запуск Merlin-Sigal алгоритму...")

        for node in self.nodes:
            initial_pairs = node.start_algo()
            for target, msg in initial_pairs:
                    action = Action(
                        data={
                            "target": target,
                            "message": msg,
                            "sender": node.node_id
                        },
                        node_id=target,
                        action_id=uuid.uuid4()
                    )
                    
                    # Додаємо повідомлення в mailbox цільового вузла
                    target_node = next((n for n in self.nodes if n.node_id == target), None)
                    if target_node and hasattr(target_node, 'mailbox'):
                        target_node.mailbox.add_inbox_action(action)
                        # print(f"   → {str(node.node_id)[:8]} → {str(target)[:8]}")  # можна розкоментувати

        print("✅ Початкові повідомлення додані в mailboxes\n")