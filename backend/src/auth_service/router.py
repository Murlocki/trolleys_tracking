import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.auth_service import auth_functions
from src.auth_service.auth_functions import verify_and_refresh_access_token, get_old_token_record
from src.auth_service.external_functions import create_session, get_session_by_token, delete_session_by_id, create_user, \
    authenticate_user, find_user_by_username, get_user_sessions
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
    response = await authenticate_user(UserAuthDTO(identifier=auth_form.identifier, password=auth_form.password),
                                       settings.api_key)
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
    refresh_token = auth_functions.create_new_token(user.username, user.role,
                                                    is_refresh=True) if auth_form.remember_me else None
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
        raise HTTPException(status_code=error["status_code"],
                            detail=AuthResponse(token=token, data=error["detail"]).model_dump())
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


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
import logging
from typing import Optional

logger = logging.getLogger(__name__)


@auth_router.get("/auth/check_auth",
                 response_model=TokenModelResponse,
                 responses={
                     401: {"description": "Invalid or expired token"},
                     404: {"description": "User not found"},
                     500: {"description": "Internal server error"}
                 })
async def check_auth(
        credentials: HTTPAuthorizationCredentials = Depends(bearer)
) -> TokenModelResponse:
    """
    Verify user authentication and handle token rotation.

    Checks:
    1. Valid JWT structure
    2. Active user existence
    3. Token rotation if old token provided
    4. Automatic token refresh if nearing expiration

    Returns:
        TokenModelResponse: Contains the current valid token
    """
    try:
        token = credentials.credentials

        # 1. Verify basic token validity
        try:
            payload = decode_token(token)
            if not payload or not payload.get("sub"):
                logger.warning(f"Invalid token payload: {payload}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"message": "Invalid token", "token": None}
                )
        except Exception as decode_error:
            logger.warning(f"Token decode failed: {str(decode_error)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"message": "Invalid token", "token": None}
            )

        logger.info(f"Token decoded successfully for user: {payload['sub']}")

        # 2. Verify user exists
        user = await find_user_by_username(
            username=payload["sub"],
            api_key=settings.api_key
        )
        if not user:
            logger.warning(f"User not found: {payload['sub']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"message": "User not found", "token": None}
            )

        # 3. Check for token rotation
        old_token_record = await get_old_token_record(token)
        if old_token_record:
            if not old_token_record.get("new_access_token"):
                logger.warning("Invalid old token record - missing new token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"message": "Invalid token rotation", "token": None}
                )
            token = old_token_record["new_access_token"]
            logger.info(f"Performed token rotation for user: {payload['sub']}")

        # 4. Verify and potentially refresh token
        refreshed_token = await verify_and_refresh_access_token(token)
        if not refreshed_token:
            logger.warning(f"Token validation failed for user: {payload['sub']}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"message": "Invalid token", "token": None}
            )

        # Return the most current valid token
        return TokenModelResponse(token = refreshed_token)

    except HTTPException:
        # Re-raise already handled HTTP exceptions
        raise

    except Exception as error:
        logger.error(f"Authentication check failed: {str(error)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Authentication check failed", "token": None}
        )
