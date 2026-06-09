from .models import OrderStatus


class StatusMachine:
    _transitions = {
        OrderStatus.ACCEPTED: [OrderStatus.DIAGNOSTICS],
        OrderStatus.DIAGNOSTICS: [
            OrderStatus.WAITING_APPROVAL,
            OrderStatus.IN_PROGRESS,
        ],
        OrderStatus.WAITING_APPROVAL: [OrderStatus.IN_PROGRESS],
        OrderStatus.IN_PROGRESS: [OrderStatus.READY],
        OrderStatus.READY: [OrderStatus.COMPLETED],
        OrderStatus.COMPLETED: [],
    }

    @staticmethod
    def can_transition(order, new_status):
        return new_status in StatusMachine._transitions.get(order.status, [])

    @staticmethod
    def transition(order, new_status):
        if StatusMachine.can_transition(order, new_status):
            order.status = new_status
            return True
        return False
