from .models import Part, Work


class ReferenceService:
    _works = {
        "w1": Work("w1", "Oil change", 1200),
        "w2": Work("w2", "Brake pads replacement", 1500),
        "w3": Work("w3", "Engine diagnostics", 2000),
    }

    _parts = {
        "p1": Part("p1", "Oil filter", "F-123", 500),
        "p2": Part("p2", "Brake pads", "BR-456", 3500),
        "p3": Part("p3", "Motor oil 5W-30", "OIL-789", 3000),
    }

    @staticmethod
    def get_all_works():
        return list(ReferenceService._works.values())

    @staticmethod
    def get_work(work_id: str):
        return ReferenceService._works.get(work_id)

    @staticmethod
    def get_all_parts():
        return list(ReferenceService._parts.values())

    @staticmethod
    def get_part(part_id: str):
        return ReferenceService._parts.get(part_id)
