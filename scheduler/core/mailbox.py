from scheduler.core.action import Action

class Mailbox:
    def __init__(self):
        self.inbox = []
        self.outbox = []

    def add_outbox_action(self, action: Action):
        action.action_type = 'outbox'
        self.outbox.append(action)

    def add_inbox_action(self, action: Action):
        action.action_type = 'inbox'
        self.inbox.append(action)

    def get_actions(self):
        """Повертає ВСІ доступні дії (inbox + outbox)"""
        actions = []
        actions.extend(self.inbox[:])   # копіюємо, щоб не було проблем при видаленні
        actions.extend(self.outbox[:])
        return actions

    def remove_action(self, action: Action):
        try:
            if action.action_type == 'outbox':
                self.outbox.remove(action)
            elif action.action_type == 'inbox':
                self.inbox.remove(action)
        except ValueError:
            pass  # дія вже була видалена