from ...core.file_storage import (
    add_car,
    delete_car,
    get_all_cars,
    get_car_by_id,
    get_cars_by_client,
    update_car,
)


class CarService:
    @staticmethod
    def get_all() -> list[dict]:
        return get_all_cars()

    @staticmethod
    def get_by_id(car_id: str) -> dict | None:
        return get_car_by_id(car_id)

    @staticmethod
    def get_by_client(client_id: str) -> list[dict]:
        return get_cars_by_client(client_id)

    @staticmethod
    def create(car_data: dict) -> dict:
        return add_car(car_data)

    @staticmethod
    def update(car_id: str, car_data: dict) -> dict | None:
        return update_car(car_id, car_data)

    @staticmethod
    def delete(car_id: str) -> bool:
        return delete_car(car_id)
