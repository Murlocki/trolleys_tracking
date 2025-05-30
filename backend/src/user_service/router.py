import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.common_functions import decode_token, verify_response
from src.shared.config import settings
from src.shared.database import SessionLocal
from src.shared.logger_setup import setup_logger
from src.shared.schemas import AuthResponse, UserAuthDTO, UserDTO
from src.user_service import crud, auth_functions
from src.user_service.auth_functions import validate_password
from src.user_service.external_functions import check_auth_from_external_service, delete_user_sessions
from src.user_service.models import User, Role
from src.user_service.schemas import UserCreate, UserUpdate

user_router = APIRouter()
logger = setup_logger(__name__)
logger.info(f"""
Server start time (UTC): {datetime.now()}
Server timestamp: {int(time.time())}
System timezone: {time.tzname}
Environment timezone: {os.environ.get('TZ', 'Not set')}
""")

bearer = HTTPBearer(auto_error=False)


async def get_valid_token(request: Request, credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    logger.info(request.headers)
    if request.headers.get("X-API-Key") == settings.api_key:
        return settings.api_key
    verify_result = await check_auth_from_external_service(credentials.credentials)
    logger.info(f"Verify result {verify_result}")
    if not verify_result or not verify_result["token"]:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return verify_result["token"]


async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


bearer = HTTPBearer(auto_error=False)


@user_router.post(
    "/user/crud",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthResponse,
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - insufficient privileges"},
        409: {"description": "User already exists"},
        422: {"description": "Validation error"}
    }
)
async def create_user(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(get_valid_token)
) -> AuthResponse:
    """
    Creates a new user account with validation checks.

    Security Flow:
    1. Validates authentication token
    2. Checks username/email availability
    3. Validates password complexity
    4. Creates user record

    Permissions:
    - Requires valid service token for SERVICE role creation
    - Regular users can only create STANDARD role accounts

    Args:
        user_in: User creation data
        db: Database session
        token: Validated authentication token

    Returns:
        AuthResponse with created user data

    Raises:
        HTTPException: For any validation or authorization failure
    """
    result = AuthResponse(token=token)

    try:
        # 1. Log creation attempt (without sensitive data)
        logger.info(
            f"User creation attempt | "
            f"Username: {user_in.username} | "
            f"Role: {user_in.role.value if user_in.role else 'STANDARD'}"
        )

        # 2. Check username availability
        existing_user = await crud.get_user_by_username(db, user_in.username)
        if existing_user:
            logger.warning(f"Username taken | Username: {user_in.username}")
            result.data = {"message": "Username already in use"}
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result.model_dump()
            )

        # 3. Validate user data for non-service accounts
        if user_in.role != Role.SERVICE:
            if not user_in.user_data:
                result.data = {"message": "User data required"}
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result.model_dump()
                )

            # 4. Check email availability
            if hasattr(user_in.user_data, 'email'):
                existing_email = await crud.get_user_by_email(db, user_in.user_data.email)
                if existing_email:
                    logger.warning(f"Email taken | Email: {user_in.user_data.email[:3]}...")
                    result.data = {"message": "Email already registered"}
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=result.model_dump()
                    )

        # 5. Validate password complexity
        if not auth_functions.validate_password(user_in.password):
            logger.warning("Password complexity failed")
            result.data = {"message": "Password must contain [A-Z], [a-z], [0-9] and be 8+ chars"}
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.model_dump()
            )

        # 6. Create user
        user = await crud.create_user(db, user_in)
        if not user:
            logger.error("User creation failed")
            result.data = {"message": "User creation failed"}
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.model_dump()
            )

        # 7. Return success response
        logger.info(f"User created | ID: {user.id} | Role: {user.role.value}")
        user_dict = user.to_dict()
        result.data = UserDTO(
            id=user_dict["id"],
            username=user_dict["username"],
            is_active=user_dict["is_active"],
            role=user_dict["role"],
            user_data=user_dict.get(user_dict["user_data"], None),
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User creation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "Internal server error"}
        )


@user_router.get(
    "/user/crud/{user_id}",
    response_model=AuthResponse,
    responses={
        200: {"description": "User data retrieved successfully"},
        401: {"description": "Unauthorized - invalid token"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }
)
async def find_user_by_id(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(get_valid_token),
) -> AuthResponse:
    """
    Retrieves user information by ID with access control.

    Security Flow:
    1. Validates authentication token
    2. Checks requested user exists
    3. Returns user data

    Permissions:
    - Service accounts cannot do anything

    Args:
        user_id: ID of user to retrieve
        db: Database session
        token: Validated authentication token

    Returns:
        AuthResponse with user data

    Raises:
        HTTPException: For authorization or not found errors
    """
    result = AuthResponse(token=token)

    try:
        # 1. Retrieve target user
        user = await crud.get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"User not found | ID: {user_id}")
            result.data = {"message": "User not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )
        logger.info(f"User found | ID: {user_id} {user.to_dict()}")
        # 2. Prepare response data (filter sensitive fields)
        user_dict = user.to_dict()
        result.data = UserDTO(
            id=user_dict["id"],
            username=user_dict["username"],
            is_active=user_dict["is_active"],
            role=user_dict["role"],
            user_data=user_dict.get(user_dict["user_data"],None),
        )
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"User lookup error | ID: {user_id} | Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@user_router.post("/user/authenticate", response_model=UserDTO, status_code=status.HTTP_200_OK)
async def auth_user(user_auth_data: UserAuthDTO, token=Depends(get_valid_token), db: AsyncSession = Depends(get_db)):
    user = await crud.authenticate_user(db, user_auth_data.identifier, user_auth_data.password)
    if not user:
        logger.info("User authentication failed")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect identifier or password")
    logger.info(f"Authenticated user using {user}")
    return user


@user_router.get("/user/crud/search", status_code=status.HTTP_200_OK, response_model=UserDTO)
async def search_user(username: str, db: AsyncSession = Depends(get_db), token=Depends(get_valid_token)):
    logger.info(f"Searching user using {username}")
    user = await crud.get_user_by_username(db, username)
    if not user:
        logger.info(f"User with email {user} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logger.info(f"User with email {user} found")
    return user


@user_router.get("/user/me", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def get_profile(token: str = Depends(get_valid_token), db: AsyncSession = Depends(get_db)):
    """
    Get user by token (basically gey my profile)
    :param token: User access token
    :param db: Database session
    :return: User data
    """
    result = AuthResponse(token=token, data={"message": "User not found"})
    payload = decode_token(token)
    if not payload or not payload["sub"]:
        logger.info(f"Invalid token")
        result.data = {"message": "Invalid token"}
        raise HTTPException(status_code=401, detail=result.model_dump())

    user = await crud.get_user_by_email(db, email=payload["sub"])
    if not user:
        logger.warning("User not found")
        result.data = {"message": "User not found"}
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.model_dump())
    logger.info(f"User {user.username} found")
    result.data = UserDTO.model_validate(user)
    return result.model_dump(by_alias=True)


# TODO: ПЕРЕДЕЛАТЬ РУЧКУ ОБНОВЛЕНИЯ ПАРОЛЯ ДЛЯ ОБНОВЛЕНИЯ ПРОИЗВОЛЬНОГО ПОЛЬЗОВАТЕЛЯ
@user_router.patch("/user/me/password", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def update_password(password_form, token: str = Depends(get_valid_token),
                          db: AsyncSession = Depends(get_db)):
    """
    Update user password
    :param password_form: New password
    :param token: Access token
    :param db: Database session
    :return: None
    """
    result = AuthResponse(token=token, data={"message": "Password updated"})
    payload = decode_token(token)
    logger.info(f"Decode token {payload}")
    user: User = await crud.get_user_by_email(db, email=payload["sub"])
    if not user:
        logger.warning("User not found")
        result.data["message"] = "User not found"
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.model_dump())
    logger.info(f"User {user.to_dict()} is found")
    # Check if password meets complexity requirements
    if not validate_password(password_form.new_password):
        logger.warning("Password does not meet complexity requirements")
        result.data["message"] = "Password does not meet complexity requirements"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.model_dump())
    logger.info(f"Password validated {password_form.new_password}")
    # Update user password
    user_update = UserUpdate(**user.to_dict(), password=password_form.new_password)
    logger.info(f"Update user:{user_update}")
    user_update = await crud.update_user(db, user.username, user_update)
    logger.info(f"User {user_update.username} updated password {user_update.hashed_password}")

    response = await delete_user_sessions(token, skip_auth=True)
    error = verify_response(response)
    if error:
        logger.error(f"Error {error}")
        result.data["message"] = error["detail"]["message"]
        raise HTTPException(status_code=error["status"], detail=result.model_dump())
    logger.info(f"User sessions deleted {response.json()}")
    return AuthResponse(data=UserDTO(**user_update.to_dict()), token=token).model_dump()


@user_router.patch("/user/me/account", response_model=AuthResponse, status_code=status.HTTP_200_OK)
async def update_my_account(user: UserUpdate, token: str = Depends(get_valid_token),
                            db: AsyncSession = Depends(get_db)):
    """
    Update user by username
    :param db: database session
    :param user: User data
    :param token: Access token
    :return: Updated user data
    """
    db_user = await crud.update_user(db, user_name=user.username, user=user)
    if not db_user:
        logger.warning("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=AuthResponse(token=token,
                                                data={
                                                    "message": "User not found"}).model_dump())
    logger.info(f"User {user.username} updated")
    return AuthResponse(token=token, data=UserDTO(**db_user.to_dict()))
