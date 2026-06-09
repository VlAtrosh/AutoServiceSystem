from .service import IntegrationService


class PdfExporter:
    @staticmethod
    def export_report(data: dict, filename: str = None) -> str:
        return IntegrationService.export_to_excel(data, filename)
