import uuid
from timeit import default_timer

from scheduler.abstract.abstract_network import AbstractNetwork
from scheduler.abstract.abstract_node import AbstractNode
from scheduler.core.action import Action
from scheduler.settings.network_settings import settings


class Observer:
    network: AbstractNetwork
    nodes: dict[uuid.UUID, AbstractNode]

    def __init__(self, network: AbstractNetwork):
        if network.nodes is None or len(network.nodes) < settings.NODES_NUMBER_MIN:
            raise ValueError("The observer must have at least two nodes")

        self.network = network
        self.nodes = {node.node_id: node for node in network.nodes}

    def process_action(self, action: Action) -> None:
        if action.action_type != 'inbox':
            print(f"Пропущено дію не-inbox типу: {action.action_type}")
            return

        print(f"Processing Action ID: {action.action_id} | Type: {action.data.get('type', 'unknown')}")
        start = default_timer()

        node = self.nodes.get(action.node_id)
        if node is None:
            print(f"Node {action.node_id} not found!")
            return

        response = node.send(action)

        for incoming_action in response.actions:
            target_node = self.nodes.get(incoming_action.node_id)
            if target_node is not None and hasattr(target_node, 'mailbox'):
                target_node.mailbox.add_inbox_action(incoming_action)
                print(
                    f"New incoming message for node {incoming_action.node_id} "
                    f"with data {incoming_action.data}"
                )
            else:
                print(f"Cannot deliver to node {incoming_action.node_id} — no mailbox")

        print(f"Processed a message for node {action.node_id}. Time: {default_timer() - start:.4f} seconds\n")

    def run(self) -> None:
        print("Observer запущено. Починаємо обробку дій...\n")
        processed_count = 0

        while True:
            action = self.network.get_action()

            if not action:
                print("\nNo available action found — черги порожні.")
                break

            print(f"→ Обрано дію: {action.action_id} | Node: {action.node_id} | Type: {action.action_type}")

            try:
                self.process_action(action)
                processed_count += 1
            except Exception as e:
                print(f"Помилка обробки дії {action.action_id}: {e}")
                if settings.INTERRUPT_ON_ERROR:
                    raise

            # Видаляємо оброблену дію
            node = self.nodes.get(action.node_id)
            if node and hasattr(node, 'mailbox'):
                try:
                    node.mailbox.remove_action(action)
                except (ValueError, Exception):
                    pass  # дія вже видалена

        print(f"\nСимуляція завершена. Оброблено дій: {processed_count}")