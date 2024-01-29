class Notification:
    count = 1

    def __init__(self, event_id,  message, status="unread"):
        """Инициализация уведомления с указанным идентификатором события, сообщением и статусом."""
        self.id = Notification.count
        Notification.count += 1
        self.event_id = event_id
        self.status = status
        self.message = message

    def to_dict(self):
        """Сериализация уведомления в словарь."""
        return {
            "id": self.id,
            "event_id": self.event_id,
            "status": self.status,
            "message": self.message
        }

    @staticmethod
    def from_dict(n_data):
        """Десериализация уведомления из словаря."""
        notification = Notification(n_data['event_id'], n_data['message'], n_data['status'])
        notification.id = n_data['id']
        Notification.count = max(Notification.count, notification.id + 1)
        return notification

