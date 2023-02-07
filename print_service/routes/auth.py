from auth_lib.fastapi import UnionAuth
from print_service.settings import get_settings

settings = get_settings()

auth = UnionAuth(settings.AUTH_URL)
