import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.auth_service import auth_functions
from src.auth_service.auth_functions import verify_and_refresh_access_token
from src.auth_service.external_functions import create_session, get_session_by_token, delete_session_by_id, create_user, \
    authenticate_user, find_user_by_email, get_user_sessions
from src.auth_service.schemas import UserCreate, AuthForm
from src.shared import logger_setup
from src.shared.common_functions import decode_token, verify_response
from src.shared.config import settings
from src.shared.schemas import SessionSchema, AuthResponse, SessionDTO, UserAuthDTO
from src.shared.schemas import TokenModelResponse
from src.shared.schemas import UserDTO

auth_router = APIRouter()
logger = logger_setup.setup_logger(__name__)
logger.info(f"""
Server start time (UTC): {datetime.now()}
Server timestamp: {int(time.time())}
System timezone: {time.tzname}
Environment timezone: {os.environ.get('TZ', 'Not set')}
""")

bearer = HTTPBearer()

@auth_router.post("/auth/login", response_model=TokenModelResponse, status_code=status.HTTP_200_OK)
async def login_user(auth_form: AuthForm):
    # Authenticate user
    response = await authenticate_user(UserAuthDTO(identifier=auth_form.identifier, password=auth_form.password),settings.api_key)
    error = verify_response(response)
    if error:
        logger.error(error)
        raise HTTPException(status_code=error["status_code"], detail=error["detail"])
    user = UserDTO(**response.json())
    logger.info(f"User {user.username} is found")

    # Check if user is active
    if not user.is_active:
        logger.error(f"Could not login user {user.username} because it is inactive")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Activate account")
    logger.info(f"User {user} logged in")

    # Create access tokens
    access_token = auth_functions.create_new_token(user.username, user.role)
    logger.info(f"User {user.username} logged in with access token {access_token}")
    # Create refresh token if remember_me is set
    refresh_token = auth_functions.create_new_token(user.username, user.role, is_refresh=True) if auth_form.remember_me else None
    response = await create_session(
        SessionSchema(
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            device=auth_form.device,
            ip_address=auth_form.ip_address))
    error = verify_response(response, 201)
    if error:
        logger.error(error)
        raise HTTPException(status_code=error["status_code"], detail=error["detail"])
    logger.info(f"User logged in {'(rem mode)' if auth_form.remember_me else ''}: {user.username}")
    return TokenModelResponse(token=access_token).model_dump()


@auth_router.post("/auth/logout", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    """
    Perform logout of user
    :param credentials: token
    :return: AuthResponse
    """
    # Check if token is valid
    token_verified = await check_auth(credentials)
    logger.info("Verified token {token_verified}")
    if not token_verified or not token_verified["token"]:
        logger.warning("Invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "Invalid token"})
    token = token_verified["token"]
    logger.info(f"Valid Token: {token}")
    # Get session by token
    response = await get_session_by_token(token, token_type="access_token")
    error = verify_response(response)
    if error:
        logger.error(error)
        raise HTTPException(status_code=error["status_code"], detail=AuthResponse(token=token,data=error["detail"]).model_dump())
    session = SessionDTO(**response.json())
    logger.info(f"Found session {session}")
    # Delete session
    response = await delete_session_by_id(session.session_id, token, True)
    error = verify_response(response)
    if error:
        logger.error(error)
        raise HTTPException(status_code=error["status_code"], detail=error["detail"])
    logger.info(f"Session {session.session_id} deleted")
    return AuthResponse(data=response.json(), token=token).model_dump()


@auth_router.get("/auth/check_auth", response_model=TokenModelResponse)
async def check_auth(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    """
    Check if user is authenticated
    :param credentials: Carryind token in header
    :param db: Database session
    :return: Token data
    """
    token = credentials.credentials

    # Get token payload
    payload = decode_token(token)
    logger.info(f"Token decoded successfully {payload}")
    if not payload or not payload["sub"]:
        logger.warning("Invalid token")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Invalid token",
                                                                           "token": None})

    # Get token user
    user = await find_user_by_email(email=payload["sub"])
    if not user:
        logger.warning("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "User is not found",
                                                                           "token": None})

    # Check token validity and refresh if needed
    token = await verify_and_refresh_access_token(token)
    if not token:
        logger.warning("Invalid new token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"message": "Invalid new token",
                                                                              "token": None})
    return {"token": token}
