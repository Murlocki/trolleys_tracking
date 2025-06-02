from src.shared.config import settings

CHECK_AUTH = f"{settings.auth_service_url}/auth/check_auth"
FIND_USER_BY_ID= f"{settings.user_service_url}/user/crud"