from src.shared.config import settings

CHECK_AUTH = f"{settings.auth_service_url}/auth/check_auth"
FIND_CAMERA_BY_ID= f"{settings.camera_service_url}/camera/crud/groups/group_id/cameras/camera_id"