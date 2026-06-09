from ...config import config
from ..order.models import OrderStatus
from ..user.service import UserService


class NotificationService:
    @staticmethod
    def send_sms(phone: str, message: str) -> bool:
        # TEST режим: только имитация
        if config.ENV == "test":
            print(f"[TEST MODE] SMS to {phone}: {message}")
            return True

        # Обычная отправка
        print(f"[SMS] -> {phone}: {message}")
        return True

    @staticmethod
    def send_status_notification(client_id: str, order_number: str, status) -> bool:
        client = UserService.get_user(client_id)
        if not client:
            return False

        # DEBUG режим: дополнительное логирование
        if config.DEBUG:
            print(
                f"[DEBUG] send_status_notification: client={client_id}, order={order_number}, status={status}"
            )

        status_names = {
            OrderStatus.READY.value: "ready for pickup",
            OrderStatus.WAITING_APPROVAL.value: "waiting for approval of additional work",
        }

        message = f"Your order {order_number} {status_names.get(status.value if hasattr(status, 'value') else status, status)}"
        return NotificationService.send_sms(client.phone, message)

    @staticmethod
    def send_approval_link(client_id: str, order_number: str, order_id: str) -> str:
        client = UserService.get_user(client_id)
        if not client:
            return ""

        link = f"https://auto-service.ru/approve/{order_id}"
        message = f"To approve additional work for order {order_number} follow the link: {link}"

        # DEBUG режим: показываем ссылку в консоли
        if config.DEBUG:
            print(f"[DEBUG] Approval link: {link}")

        NotificationService.send_sms(client.phone, message)
        return link
