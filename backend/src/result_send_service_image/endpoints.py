from src.shared.config import settings

CHECK_AUTH = f"{settings.auth_service_url}/auth/check_auth"
GET_USER_SUBS = f"{settings.camera_service_url}/camera/crud/users"