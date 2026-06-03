class Car:
    def __init__(
        self,
        id: str,
        client_id: str,
        brand: str,
        model: str,
        year: int,
        license_plate: str,
        vin: str,
        color: str,
    ):
        self.id = id
        self.client_id = client_id
        self.brand = brand
        self.model = model
        self.year = year
        self.license_plate = license_plate
        self.vin = vin
        self.color = color
