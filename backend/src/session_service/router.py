import os
import time
from datetime import datetime
from idlelib.query import Query

from fastapi import HTTPException, status, APIRouter, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.session_service import crud
from src.session_service.crud import create_and_store_session, delete_inactive_sessions, delete_sessions_by_user_id
from src.session_service.external_functions import check_auth_from_external_service, find_user_by_email
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


async def get_valid_token(request: Request, credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    if request.headers.get("X-API-Key") == settings.api_key:
        return settings.api_key
    verify_result = await check_auth_from_external_service(credentials.credentials)
    logger.info(f"Verify result {verify_result}")
    if not verify_result or not verify_result["token"]:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return verify_result["token"]




@session_router.delete("/session/crud/me/search", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def delete_my_session_by_token(token: str, access_token=Depends(get_valid_token)):
    """
    Delete session by ID
    :param access_token: auth token
    :param token: JWT Token or api key
    :return: AuthResponse
    """
    session = await crud.delete_session_by_access_token(token)
    if not session:
        logger.warning("Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=AuthResponse(data=
                                                {"message": "Session not found"},
                                                token=token).model_dump())
    logger.info(f"Session {session.session_id} was deleted")
    return AuthResponse(data=session, token=access_token).model_dump()

@session_router.delete("/session/crud/me/{session_id}", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def delete_my_session_by_id(session_id: str, token=Depends(get_valid_token)):
    """
    Delete session by ID
    :param token: JWT Token
    :param session_id: Session ID
    :return: None
    """
    session = await crud.delete_session_by_id(session_id)
    if not session:
        logger.warning("Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=AuthResponse(data=
                                                {"message": "Session not found"},
                                                token=token).model_dump())
    logger.info(f"Session {session_id} was deleted")
    return AuthResponse(data=session, token=token).model_dump()

@session_router.delete("/session/crud/me", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def delete_my_sessions(token=Depends(get_valid_token)):
    """
    Delete all sessions for user
    :param token: User token
    :return: Sessions
    """
    decoded_token = decode_token(token)
    logger.info(f"Decoded token: {decoded_token}")
    result = AuthResponse(token=token, data={"message": ""})
    response = await find_user_by_email(email=decoded_token["sub"])
    error = verify_response(response)
    if error:
        logger.error(f"Error: {error}")
        result.data = {"message": f"Error finding user by email: {error['detail']}"}
        raise HTTPException(status_code=error["status"], detail=result.model_dump())
    user = UserDTO(**response.json())
    logger.info(f"Sessions deleting for user {user.username}")
    result = await delete_sessions_by_user_id(user.id)
    return AuthResponse(data=result, token=token).model_dump()

@session_router.post("/session/crud/me", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def create_my_session(session_create_data: SessionSchema, token=Depends(get_valid_token)):
    """
    Create new session
    :param token: token or api key
    :param session_create_data:
    :return: Created session
    """
    session = await create_and_store_session(
        user_id=session_create_data.user_id,
        access_token=session_create_data.access_token,
        refresh_token=session_create_data.refresh_token,
        device=session_create_data.device,
        ip_address=session_create_data.ip_address
    )
    if not session:
        logger.error(f"Session not created {session_create_data}")
        raise HTTPException(status_code=404, detail=AuthResponse(token=token, data={"message":"Session create error"}).model_dump())
    logger.info(f"Created session with data {session}")
    return AuthResponse(token=token, data=session).model_dump()


@session_router.get("/session/crud/search", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def get_session_by_token(token: str, token_type: str = "access_token", access_token = Depends(get_valid_token)):
    """
    Get session by token
    :param token: session token
    :param token_type: access_token or refresh_token
    :return: dict|None
    """
    result = AuthResponse(token=token, data={"message": ""})
    session = await crud.get_session_by_token(token, token_type)
    if not session:
        logger.warning("Session not found")
        result.data = {"message": f"Session not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.model_dump())
    result.data = session
    logger.info(f"Session {session.session_id} was found")
    return result.model_dump()


@session_router.get("/session/crud/{user_id}", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def get_user_sessions(user_id: int, token=Depends(get_valid_token)):
    """
    Get all sessions for user
    :param token: user token or api key
    :param user_id: User ID
    :return: List of sessions
    """
    sessions = await crud.get_sessions(user_id=user_id)
    logger.info(f"Sessions for user {user_id} were found")
    return AuthResponse(data=[SessionDTO(**session) for session in sessions], token=token).model_dump()


@session_router.delete(
    "/session/crud/{user_id}",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Sessions deleted successfully"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "User not found or no sessions exist"},
        500: {"description": "Internal server error"}
    }
)
async def delete_user_sessions(
        user_id: int,
        token: str = Depends(get_valid_token),
) -> AuthResponse:
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
        # 1. Verify user exists (optional - depends on your system)
        # user_exists = await user_service.user_exists(user_id)
        # if not user_exists:
        #     raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

        # 2. Check if user has any sessions first
        existing_sessions = await crud.get_sessions(user_id=user_id)
        if not existing_sessions:
            logger.warning(f"No sessions found for user {user_id}")
            result.data = {"message": "No sessions found for user"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
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

        result.data = {
            "message": "Sessions deleted successfully",
            "count": len(deleted_sessions),
            "sessions": deleted_sessions,
            "deleted_at": datetime.now().isoformat()
        }
        return result

    except HTTPException:
        # Re-raise already handled exceptions
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error deleting sessions for user {user_id}: {str(e)}",
            exc_info=True
        )
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@session_router.delete(
    "/session/crud/{user_id}/{session_id}",
    response_model=AuthResponse,
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
) -> AuthResponse:
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
        user_sessions = await crud.get_sessions(user_id=user_id)
        if not user_sessions:
            logger.warning(f"No sessions found for user {user_id}")
            result.data = {"message": "No sessions found for user"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        logger.info(f"Found {len(user_sessions)} sessions for user {user_id}")

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

        result.data = {
            "message": "Session deleted successfully",
            "session_id": session_id,
            "deleted_at": datetime.now().isoformat()
        }
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
    response_model=AuthResponse,
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
) -> AuthResponse:
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
            logger.error(f"Session not found for token: {access_token_update_data.old_access_token[:8]}...")
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
