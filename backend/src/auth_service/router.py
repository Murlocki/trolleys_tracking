import os
import time
from datetime import datetime

from fastapi import APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import status, HTTPException, Depends
from src.auth_service import auth_functions
from src.auth_service.auth_functions import verify_and_refresh_access_token, get_old_token_record
from src.auth_service.external_functions import create_session, get_session_by_token, delete_session_by_id, \
    authenticate_user, find_user_by_username, find_user_by_id
from src.auth_service.schemas import AuthForm
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

bearer = HTTPBearer(auto_error=False)





@auth_router.post(
    "/auth/login",
    response_model=TokenModelResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid credentials"},
        401: {"description": "Unauthorized - account inactive or invalid credentials"},
        500: {"description": "Internal server error"}
    }
)
async def login_user(
        auth_form: AuthForm,
) -> TokenModelResponse:
    """
    Authenticate user and return access token.

    Flow:
    1. Validate credentials
    2. Verify user status
    3. Generate tokens
    4. Create session record
    5. Return access token

    Security:
    - Rate limiting recommended
    - All errors return generic messages
    - Sensitive data not logged
    """
    try:
        # 1. Authenticate user
        auth_data = UserAuthDTO(
            identifier=auth_form.identifier,
            password=auth_form.password
        )

        auth_response = await authenticate_user(
            auth_data,
            settings.api_key
        )

        if error := verify_response(auth_response):
            logger.warning(f"Authentication failed for {auth_form.identifier}")
            raise HTTPException(
                status_code=error["status_code"],
                detail="Invalid credentials"
            )

        user = UserDTO(**auth_response.json())
        logger.info(f"User authentication successful: {user.id}")

        # 2. Verify user status
        if not user.is_active:
            logger.warning(f"Login attempt for inactive account: {user.id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account inactive"
            )

        # 3. Generate tokens
        access_token = auth_functions.create_new_token(
            user_id=user.id,
            role=user.role
        )

        refresh_token = None
        if auth_form.remember_me:
            refresh_token = auth_functions.create_new_token(
                user_id=user.id,
                role=user.role,
                is_refresh=True
            )
            logger.debug("Refresh token generated (remember_me=True)")

        # 4. Create session
        session_data = SessionSchema(
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            device=auth_form.device,
            ip_address=auth_form.ip_address  # More reliable than client-provided IP
        )

        session_response = await create_session(session_data, settings.api_key)

        if error := verify_response(session_response, 201):
            logger.error(f"Session creation failed: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login processing failed"
            )

        # 5. Return response
        logger.info(f"Successful login for {user.id} from {auth_form.ip_address}")
        return TokenModelResponse(token=access_token)

    except HTTPException:
        # Re-raise handled exceptions
        raise

    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login processing failed"
        )


@auth_router.post(
    "/auth/logout",
    status_code=status.HTTP_200_OK,
    response_model=AuthResponse,
    responses={
        401: {"description": "Invalid or expired token"},
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"}
    }
)
async def logout_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> AuthResponse:
    """
    Perform user logout by invalidating the current session.

    Steps:
    1. Verify the access token
    2. Retrieve the active session
    3. Delete the session record
    4. Return success response

    Security:
    - Invalidates the current access token
    - Logs the logout activity
    - Returns generic error messages
    """
    try:
        # 1. Verify token
        token_verified = await check_auth(credentials)
        if not token_verified or not token_verified.token:
            logger.warning("Invalid token provided for logout")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"message": "Invalid token"}
            )

        token = token_verified.token
        logger.debug(f"Token verified (first 6 chars): {token[:6]}...")

        # 2. Get session by token
        session_response = await get_session_by_token(
            api_key=settings.api_key,
            token=token,
            token_type="access_token"
        )

        if error := verify_response(session_response):
            logger.error(f"Session lookup failed: {error}")
            raise HTTPException(
                status_code=error["status_code"],
                detail=AuthResponse(
                    token=token,
                    data={"message": "Session not found"}
                ).model_dump()
            )

        session = SessionDTO(**session_response.json()['data'])
        logger.info(f"Session found: {session.session_id}")

        # 3. Delete session
        delete_response = await delete_session_by_id(
            api_key=settings.api_key,
            session_id=session.session_id,
            user_id=session.user_id
        )

        if error := verify_response(delete_response):
            logger.error(f"Session deletion failed: {error}")
            raise HTTPException(
                status_code=error["status_code"],
                detail=AuthResponse(
                    token=token,
                    data={"message": "Logout processing failed"}
                ).model_dump()
            )

        # 4. Return success response
        logger.info(f"Successful logout for session {session.session_id}")
        return AuthResponse(
            token=token,
            data={"message": "Successfully logged out"}
        )

    except HTTPException as http_exc:
        # Re-raise already handled HTTP exceptions
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected logout error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AuthResponse(
                token=credentials.credentials if credentials else None,
                data={"message": "Logout processing failed"}
            ).model_dump()
        )


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
        user = await find_user_by_id(
            user_id=int(payload["sub"]),
            api_key=settings.api_key
        )
        if error:=verify_response(user):
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
        return TokenModelResponse(token=refreshed_token)

    except HTTPException:
        # Re-raise already handled HTTP exceptions
        raise

    except Exception as error:
        logger.error(f"Authentication check failed: {str(error)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Authentication check failed", "token": None}
        )
