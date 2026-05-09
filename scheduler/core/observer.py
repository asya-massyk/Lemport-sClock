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

        print(f"Processing Action ID: {action.action_id}")
        start = default_timer()

        node = self.nodes.get(action.node_id)
        if node is None:
            print(f"Node {action.node_id} not found!")
            return
        
        if not isinstance(action.data, dict) or "message" not in action.data:
            print(f"Skipping incompatible action: {action.data}")
            return

        # Викликаємо process_action, а не send!
        response = node.process_action(action)

        for incoming_action in response.actions:
            target_node = self.nodes.get(incoming_action.node_id)
            if target_node is not None and hasattr(target_node, 'mailbox'):
                target_node.mailbox.add_inbox_action(incoming_action)
                print(
                    f"New incoming message for node {str(incoming_action.node_id)[:8]}..."
                )
            else:
                print(f"Cannot deliver to node {incoming_action.node_id}")

        print(f"Processed message for node {str(action.node_id)[:8]}... Time: {default_timer() - start:.4f}s\n")
    
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
                print("No available action found. Simulation finished.\n")
                
                # === ВИВІД ТАБЛИЦЬ МАРШРУТИЗАЦІЇ MERLIN-SIGAL ===
                print("=== ROUTING TABLES (Merlin-Sigal) ===")
                for node_id, node in self.nodes.items():
                    print(f"\nNode {str(node_id)[:8]}...")
                    try:
                        table = node.get_routing_table()
                        from pprint import pprint
                        pprint(table)
                    except Exception as e:
                        print(f"   Cannot get routing table: {e}")
                
                break  # Завершуємо симуляцію