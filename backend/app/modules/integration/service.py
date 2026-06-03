import json
from datetime import datetime


class IntegrationService:
    @staticmethod
    def export_to_excel(data: dict, filename: str = None) -> str:
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        else:
            filename = filename.replace(".xlsx", ".json")

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"[EXPORT] Exported to {filename}")
        return filename
