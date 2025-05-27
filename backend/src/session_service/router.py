import os
import time
from datetime import datetime

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


# @session_router.delete("/session/crud/me/search",
# @session_router.delete("/session/crud/me/{session_id}"
# @session_router.delete("/session/crud/me"
# @session_router.post("/session/crud/me"

# @session_router.get("/session/crud/{user_id}"
# @session_router.delete("/session/crud/{user_id}/{session_id}"

# @session_router.patch("/session/crud/{session_id}/update_token"
# @session_router.get("/session/crud/search"

@session_router.delete("/session/crud/me/search", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def delete_session_by_token(token: str, access_token=Depends(get_valid_token)):
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
async def delete_session_by_id(session_id: str, token=Depends(get_valid_token)):
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
async def delete_sessions(token=Depends(get_valid_token)):
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
async def create_session(session_create_data: SessionSchema, token=Depends(get_valid_token)):
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


@session_router.delete("/session/crud/{user_id}/{session_id}", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def delete_user_session(user_id: int, session_id: str, token=Depends(get_valid_token)):
    """
    Delete user session by ID
    :param user_id: user ID
    :param session_id: session ID
    :param token: api key or jwt token
    :return:
    """
    result = AuthResponse(token=token, data={"message": ""})
    user_sessions = await crud.get_sessions(user_id=user_id)
    if not user_sessions:
        logger.error(f"Session for user {user_id} not found")
        result.data = {"message": f"Session not found"}
        raise HTTPException(status_code=404, detail=result.model_dump())

    logger.info(f"Sessions for user {user_id} were found")
    session = await crud.delete_session_by_id(session_id)
    if not session:
        result.data = {"message": f"Session not found"}
        logger.error("Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.model_dump())
    return AuthResponse(data=session, token=token).model_dump()


@session_router.patch("/session/crud/{session_id}/update_token", response_model=SessionDTO,
                      status_code=status.HTTP_200_OK)
async def update_session_token(session_id: str, access_token_update_data: AccessTokenUpdate):
    """
    Update session token
    :param access_token_update_data:
    :param session_id: Session ID
    :return: New session entity
    """
    session = await crud.get_session_by_token(access_token_update_data.old_access_token)
    if not session:
        logger.warning("Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session.session_id != session_id:
        logger.warning("Session ID does not match")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session ID does not match")
    session = await crud.update_session_access_token(access_token_update_data.old_access_token,
                                                     access_token_update_data.new_access_token)
    if not session:
        logger.warning("Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    logger.info(f"Session {session_id} was updated")
    return session



@session_router.get("/session/crud/search", response_model=SessionDTO, status_code=status.HTTP_200_OK)
async def get_session_by_token(token: str, token_type: str = "access_token"):
    """
    Get session by token
    :param token: session token
    :param token_type: access_token or refresh_token
    :return: dict|None
    """
    session = await crud.get_session_by_token(token, token_type)
    if not session:
        logger.warning("Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    logger.info(f"Session {session.session_id} was found")
    return session.model_dump()
