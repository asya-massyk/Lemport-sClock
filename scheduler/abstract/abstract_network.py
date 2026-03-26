from random import choice
from typing import List

from scheduler.abstract.abstract_node import AbstractNode
from scheduler.core.action import Action
from scheduler.core.external_request_generator import ExternalRequestGenerator
from scheduler.settings.network_settings import settings


class AbstractNetwork:
    nodes: List[AbstractNode]
    request_generator: ExternalRequestGenerator

    def __init__(self, nodes: List[AbstractNode]):
        if settings.EXTERNAL_REQUEST_MODE:
            self.request_generator = ExternalRequestGenerator(nodes)


    def get_action(self) -> Action | None:
        if settings.EXTERNAL_REQUEST_MODE:
            self.process_external_requests()

    # 🥇 Спочатку inbox
        inbox_actions = [
            action for node in self.nodes for action in node.mailbox.inbox
        ]
        if inbox_actions:
            return choice(inbox_actions)

    # 🥈 Потім outbox
        outbox_actions = [
            action for node in self.nodes for action in node.mailbox.outbox
        ]
        if outbox_actions:
            return choice(outbox_actions)

        return None

    def process_external_requests(self) -> None:
        external_requests = self.request_generator.get_requests()
        for external_request in external_requests:
            node_id, external_request_obj = next(iter(external_request.items()))
            for node in self.nodes:
                if node.node_id == node_id:
                    node.mailbox.add_inbox_action(
                        Action(
                            external_request_obj.to_dict(),
                            node_id=node_id,
                            action_id=external_request_obj.transaction_id
                        )
                    )