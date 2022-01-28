from src.services.service_adapter import CategoryService
from src.services.crypto import CryptoService


def demo_service() -> CategoryService:
    return CategoryService()


def crypto_service() -> CryptoService:
    return CryptoService()
