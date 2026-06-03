class EmailClient:
    @staticmethod
    def send(email: str, subject: str, body: str) -> bool:
        print(f"[EMAIL] -> {email}: {subject}")
        return True
