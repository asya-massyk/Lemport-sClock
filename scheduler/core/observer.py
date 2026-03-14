import uuid
from time import sleep
from timeit import default_timer

from scheduler.abstract.abstract_network import AbstractNetwork
from scheduler.abstract.abstract_node import AbstractNode
from scheduler.core.action import Action
from scheduler.settings.network_settings import settings


class Observer:
    network: AbstractNetwork
    nodes: dict[uuid.UUID, AbstractNode]

    def __init__(self, network: AbstractNetwork):
        nodes = network.nodes
        if nodes is None or len(nodes) < settings.NODES_NUMBER_MIN:
            raise ValueError("The observer must have at least two nodes")
        self.network = network
        self.nodes = {node.node_id: node for node in nodes}

    def process_action(self, action: Action) -> None:
        if action.action_type != 'inbox':
            raise ValueError(f"Unknown action type: {action.action_type}")

        print(f"Processing Action ID: {action.action_id}, DATA: {action}")
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
        while True:
            action = self.network.get_action()
            if action:
                print(action)
                try:
                    self.process_action(action)
                except Exception as e:
                    print(f"Cannot process action {action}. Exception: {e}")
                    if settings.INTERRUPT_ON_ERROR:
                        raise
                else:
                    # безпечно видаляємо дію
                    node = self.nodes.get(action.node_id)
                    if node is not None and hasattr(node, 'mailbox'):
                        node.mailbox.remove_action(action)
            else:
                print("No available action found")
                for node in self.nodes.values():
                    if hasattr(node, 'visited') and hasattr(node, 'data'):
                        print(f"Node {node.node_id}, Visited: {node.visited}, Data: {node.data}") # type: ignore
                    else:
                        print(f"Node {node.node_id} (абстрактний або без додаткових даних)")
            sleep(settings.ACTION_SLEEP_TIME_SECONDS)