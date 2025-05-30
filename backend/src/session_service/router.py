import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends, Request, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

from src.session_service import crud
from src.session_service.crud import create_and_store_session, delete_sessions_by_user_id
from src.session_service.external_functions import check_auth_from_external_service, \
    find_user_by_id
from src.shared import logger_setup
from src.shared.common_functions import decode_token, verify_response
from src.shared.config import settings
from src.shared.schemas import SessionDTO, AccessTokenUpdate, AuthResponse, UserDTO
from src.shared.schemas import SessionSchema

session_router = APIRouter()
logger = logger_setup.setup_logger(__name__)
logger.info(f"""
Server start time (UTC): {datetime.now()}
Server timestamp: {int(time.time())}
System timezone: {time.tzname}
Environment timezone: {os.environ.get('TZ', 'Not set')}
""")

bearer = HTTPBearer(auto_error=False)
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_valid_token(request: Request, credentials: HTTPAuthorizationCredentials | None = Security(bearer), api_key: str | None = Security(api_key_scheme)) -> str:
    logger.info(request.headers)
    if api_key == settings.api_key:
        return settings.api_key
    verify_result = await check_auth_from_external_service(credentials.credentials)
    logger.info(f"Verify result {verify_result}")
    if not verify_result or not verify_result["token"]:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return verify_result["token"]


@session_router.delete(
    "/session/crud/me/{session_id}",
    response_model=AuthResponse[SessionDTO],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Session deleted successfully"},
        401: {"description": "Unauthorized - invalid token"},
        403: {"description": "Forbidden - session ownership mismatch"},
        404: {"description": "Session not found"}
    }
)
async def delete_my_session_by_id(
        session_id: str,
        token: str = Depends(get_valid_token)
) -> AuthResponse[SessionDTO]:
    """
    Deletes a specific session for the authenticated user.

    Security Flow:
    1. Validates JWT token
    2. Verifies session exists and belongs to user
    3. Deletes the session

    Args:
        session_id: UUID of session to delete
        token: Validated JWT token

    Returns:
        AuthResponse with deletion confirmation

    Raises:
        HTTPException: 404 if session not found
        HTTPException: 403 if session doesn't belong to user
    """
    # Initialize response
    result = AuthResponse(token=token, data={"message": ""})

    try:
        # 1. Get and validate session
        session = await crud.get_session_by_id(session_id)
        if not session:
            logger.warning(f"Session not found | ID: {session_id}")
            result.data = {"message": "Session not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        # 2. Verify session ownership
        decoded_token = decode_token(token)
        if not decoded_token or str(session.user_id) != decoded_token.get("sub"):
            logger.warning(
                f"Session ownership mismatch | "
                f"User: {decoded_token.get('sub', 'unknown')} | "
                f"Session User: {session.user_id}"
            )
            result.data = {"message": "Session does not belong to user"}
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.model_dump()
            )

        # 3. Perform deletion
        deleted_session = await crud.delete_session_by_id(session_id)
        if not deleted_session:
            logger.error(f"Deletion failed | Session: {session_id}")
            result.data = {"message": "Deletion failed"}
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.model_dump()
            )

        # 4. Return success
        logger.info(f"Session deleted | ID: {session_id}")
        result.data = deleted_session
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session deletion error: {str(e)}", exc_info=True)
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@session_router.delete(
    "/session/crud/me",
    response_model=AuthResponse[list[SessionDTO]],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Sessions deleted successfully"},
        401: {"description": "Invalid or expired token"},
        403: {"description": "Forbidden operation"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_my_sessions(
        token: str = Depends(get_valid_token)
) -> AuthResponse[list[SessionDTO]]:
    """
    Deletes all active sessions for the currently authenticated user.

    Security Flow:
    1. Validates JWT token
    2. Extracts user identity from token
    3. Verifies user exists
    4. Deletes all user sessions
    5. Returns deletion confirmation

    Authentication:
    - Requires valid JWT access token

    Returns:
        AuthResponse with deletion result

    Raises:
        HTTPException: For any validation or authorization failure
    """
    # Initialize response with current token
    result = AuthResponse(token=token, data={"message": ""})

    try:
        # 1. Decode token (already validated by get_valid_token)
        decoded_token = decode_token(token)
        if not decoded_token or "sub" not in decoded_token:
            logger.warning("Invalid token payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        # 2. Find user by username from token
        user_response = await find_user_by_id(user_id=decoded_token["sub"], api_key=settings.api_key)
        if error := verify_response(user_response):
            logger.error(
                f"User lookup failed:{error.get('detail')}",
            )
            result.data = {"message": "User not found"}
            raise HTTPException(
                status_code=error.get("status", 404),
                detail=result.model_dump()
            )

        # 3. Get user data
        user = UserDTO(**user_response.json()['data'])
        logger.info(
            f"Initiating session deletion for user {user.id}",
        )

        # 4. Perform deletion
        deletion_result = await delete_sessions_by_user_id(user.id)
        if not deletion_result:
            logger.error(f"Session deletion failed for user: {user.id}")
            result.data = {"message": "Session deletion failed"}
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.model_dump()
            )

        # 5. Return success response
        logger.info(
            f"Sessions deleted successfully for user: {user.id} with count {len(deletion_result)}")

        result.data = deletion_result
        return result

    except HTTPException:
        # Re-raise handled exceptions
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during session deletion: {str(e)}",
            exc_info=True
        )
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@session_router.post(
    "/session/crud/me",
    response_model=AuthResponse[SessionDTO],
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Session created successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        500: {"description": "Internal server error"}
    }
)
async def create_my_session(
        session_create_data: SessionSchema,
        token: str = Depends(get_valid_token)
) -> AuthResponse[SessionDTO]:
    """
    Creates a new authenticated session for the current user.

    Authentication:
    - Requires valid token via get_valid_token dependency

    Input Validation:
    - Automatic Pydantic validation of SessionSchema
    - Checks for existing sessions

    Process Flow:
    1. Validates authentication token
    2. Creates new session record
    3. Returns session details

    Security:
    - Never logs sensitive token data
    - Validates all inputs
    - Returns standardized error responses
    """
    # Initialize response with authenticated token
    result = AuthResponse(token=token, data={"message": ""})

    try:
        # Attempt to create new session
        session = await create_and_store_session(
            user_id=session_create_data.user_id,
            access_token=session_create_data.access_token,  # Encrypted in storage
            refresh_token=session_create_data.refresh_token,  # Encrypted in storage
            device=session_create_data.device,
            ip_address=session_create_data.ip_address  # Validated format
        )

        # Handle creation failure
        if not session:
            logger.error(
                f"Session creation failed for user {session_create_data.user_id} on device {session_create_data.device}",
            )
            result.data = {"message": "Session creation failed"}
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.model_dump()
            )

        # Log successful creation (excluding sensitive data)
        logger.info(
            f"New session created: {session}"
        )

        # Return standardized success response
        result.data = session
        return result
    except HTTPException:
        # Re-raise existing HTTP exceptions
        raise

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(
            f"Unexpected session creation error for user {session_create_data.user_id} on device {session_create_data.device}: {str(e)}",
            exc_info=True,
        )
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@session_router.get(
    "/session/crud/search",
    response_model=AuthResponse[SessionDTO],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Session by token"},
        401: {"description": "Invalid token"},
        403: {"description": "Unauthorized method"},
    }
)
async def get_session_by_token(
        token: str,
        token_type: str = "access_token",
        access_token: str = Depends(get_valid_token)  # Проверка через вашу функцию
) -> AuthResponse[SessionDTO]:
    """
    Get session by token

    Args:
        token: session token (from query string)
        token_type: token type (access/refresh)
        access_token: jwt token or api key

    Returns:
        AuthResponse: Session data
    """
    result = AuthResponse(token=access_token, data={"message": ""})

    try:
        # 1. Get session
        session = await crud.get_session_by_token(token, token_type)

        if not session:
            logger.warning(f"Session not found | Token: {token}")
            result.data = {"message": "Session not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        # 2. log result
        logger.info(f"Session found | ID: {session.session_id} | User: {session.user_id}")

        result.data = session
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session lookup error: {str(e)}", exc_info=True)
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@session_router.get(
    "/session/crud/{user_id}",
    response_model=AuthResponse[list[SessionDTO]],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "List of user sessions"},
        401: {"description": "Invalid token"},
    }
)
async def get_user_sessions(
        user_id: int,
        token: str = Depends(get_valid_token),
) -> AuthResponse[list[SessionDTO]]:
    """
    Retrieves all sessions for a specific user after validation.

    Security Flow:
    1. Validates the authentication token
    2. Verifies user exists and has sessions

    Args:
        user_id: ID of the user whose sessions should be retrieved
        token: Validated via get_valid_token dependency

    Returns:
        AuthResponse with list of sessions

    Raises:
        HTTPException: 403 if insufficient permissions
        HTTPException: 404 if no sessions found
    """
    result = AuthResponse(token=token, data={"message": ""})
    try:

        # 1. Get sessions with optional filters
        sessions = await crud.get_sessions(
            user_id=user_id,
        )

        if not sessions:
            logger.info(f"No sessions found for user {user_id}")
            result.data = {
                    "message": "No sessions found",
                    "count": 0,
                    "sessions": []
                }
            return result

        # 3. Log and return results
        logger.info(
            f"Retrieved {len(sessions)} sessions for user {user_id}"
        )
        result.data = [SessionDTO(**session) for session in sessions]
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error retrieving sessions for user {user_id}: {str(e)}",
            exc_info=True,
        )
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@session_router.delete(
    "/session/crud/{user_id}",
    response_model=AuthResponse[list[SessionDTO]],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Sessions deleted successfully"},
        401: {"description": "Invalid token"},
        403: {"description": "Forbidden - insufficient permissions"},
        500: {"description": "Internal server error"}
    }
)
async def delete_user_sessions(
        user_id: int,
        token: str = Depends(get_valid_token),
) -> AuthResponse[list[SessionDTO]]:
    """
    Deletes all sessions for a specific user after validation.

    Security Flow:
    1. Validates the authentication token
    2. Verifies user exists and has sessions
    3. Deletes all sessions if checks pass

    Args:
        user_id: ID of the user whose sessions should be deleted
        token: Validated via get_valid_token dependency

    Returns:
        AuthResponse with list of deleted sessions

    Raises:
        HTTPException: 403 if insufficient permissions
        HTTPException: 404 if no sessions found
        HTTPException: 500 for internal errors
    """
    result = AuthResponse(token=token, data={"message": ""})

    try:


        # 2. Check if user has any sessions first
        existing_sessions = await crud.get_sessions(user_id=user_id)
        if not existing_sessions:
            logger.warning(f"No sessions found for user {user_id}")
            result.data = []
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail=result.model_dump()
            )

        # 3. Perform deletion
        deleted_sessions = await crud.delete_sessions_by_user_id(user_id)
        if not deleted_sessions:
            logger.error(f"Deletion failed for user {user_id}'s sessions")
            result.data = {"message": "Session deletion failed"}
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.model_dump()
            )

        # 4. Log and return success
        logger.info(
            f"Deleted {len(deleted_sessions)} sessions for user {user_id} | "
        )

        result.data = deleted_sessions
        return result

    except HTTPException:
        # Re-raise already handled exceptions
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error deleting sessions for user {user_id}: {str(e)}", exc_info=True,
        )
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@session_router.delete(
    "/session/crud/{user_id}/{session_id}",
    response_model=AuthResponse[SessionDTO],
    status_code=status.HTTP_200_OK,
    responses={
        403: {"description": "Forbidden - session doesn't belong to user"},
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"}
    }
)
async def delete_user_session(
        user_id: int,
        session_id: str,
        token: str = Depends(get_valid_token),
) -> AuthResponse[SessionDTO]:
    """
    Deletes a specific user session after validation.

    Security Flow:
    1. Validates the authentication token
    2. Verifies session ownership
    3. Deletes session if all checks pass

    Args:
        user_id: ID of the user owning the session (from path)
        session_id: Session ID to delete (from path)
        token: Validated via get_valid_token dependency

    Returns:
        AuthResponse with deletion confirmation

    Raises:
        HTTPException: 403 if session doesn't belong to user
        HTTPException: 404 if session not found
    """
    result = AuthResponse(token=token, data={"message": ""})

    try:
        # 1. Verify user sessions exist
        user_session = await crud.get_session_by_id(session_id)
        if not user_session or not int(user_session.user_id) == user_id:
            logger.warning(f"No sessions found for user {user_id}")
            result.data = {"message": "No sessions found for user"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        logger.info(f"Found {user_session} for user {user_id}")

        # 3. Perform deletion
        deleted_session = await crud.delete_session_by_id(session_id)
        if not deleted_session:
            logger.error(f"Deletion failed for session {session_id}")
            result.data = {"message": "Session not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        logger.info(
            f"Successfully deleted session {session_id} for user {user_id} | "
            f"Deleted at: {datetime.now().isoformat()}"
        )

        result.data = deleted_session
        return result

    except HTTPException:
        # Re-raise already handled exceptions
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error deleting session {session_id}: {str(e)} | "
            f"User: {user_id}",
            exc_info=True
        )
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@session_router.patch(
    "/session/crud/{user_id}/{session_id}/update_token",
    response_model=AuthResponse[SessionDTO],
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"},
    }
)
async def update_session_token(
        user_id: int,
        session_id: str,
        access_token_update_data: AccessTokenUpdate,
        access_token: str = Depends(get_valid_token)
) -> AuthResponse[SessionDTO]:
    """
    Updates the access token for a specific session after validation.

    Security Flow:
    1. Validates the current access token
    2. Verifies session ownership
    3. Updates token if all checks pass

    Args:
        user_id: ID of the user owning the session (from path)
        session_id: Session ID to update (from path)
        access_token_update_data: Contains old and new tokens
        access_token: Validated via get_valid_token dependency

    Returns:
        AuthResponse with updated session data

    Raises:
        HTTPException: For any validation failure with appropriate status code
    """
    result = AuthResponse(token=access_token, data={"message": ""})

    try:
        # 1. Verify existing session
        session = await crud.get_session_by_token(access_token_update_data.old_access_token)
        if not session:
            logger.error(f"Session not found for token: {access_token_update_data.old_access_token}")
            result.data = {"message": "Session not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        logger.info(f"Session found: {session.session_id}")

        # 2. Validate session ownership
        if session.user_id != user_id:
            logger.error(f"User ID mismatch: session:{session.user_id} vs path:{user_id}")
            result.data = {"message": "Session does not belong to this user"}
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.model_dump()
            )

        if session.session_id != session_id:
            logger.error(f"Session ID mismatch: {session.session_id} vs {session_id}")
            result.data = {"message": "Session ID does not match"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        # 3. Perform token update
        updated_session = await crud.update_session_access_token(
            old_token=access_token_update_data.old_access_token,
            new_token=access_token_update_data.new_access_token
        )

        if not updated_session:
            logger.error("Token update failed")
            result.data = {"message": "Token update failed"}
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.model_dump()
            )

        logger.info(f"Token updated for session {session_id}")
        result.data = updated_session
        return result

    except HTTPException:
        # Re-raise already handled exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token update: {str(e)}", exc_info=True)
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )
