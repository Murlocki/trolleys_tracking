from src.shared.config import settings

CREATE_SESSION = f"{settings.session_service_url}/session/crud/me"
GET_SESSION_BY_TOKEN = f"{settings.session_service_url}/session/crud/search"
UPDATE_SESSION_TOKEN = f"{settings.session_service_url}/session/crud"
DELETE_SESSION = f"{settings.session_service_url}/session/crud"
DELETE_SESSION_BY_TOKEN = f"{settings.session_service_url}/session/crud/me"
AUTHENTICATE_USER = f"{settings.user_service_url}/user/authenticate"
FIND_USER_BY_USERNAME = f"{settings.user_service_url}/user/crud/search"
FIND_USER_BY_ID= f"{settings.user_service_url}/user/crud/"
