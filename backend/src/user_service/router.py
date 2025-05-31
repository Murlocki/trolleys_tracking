import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends, Request, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.common_functions import decode_token, verify_response
from src.shared.config import settings
from src.shared.database import SessionLocal
from src.shared.logger_setup import setup_logger
from src.shared.schemas import AuthResponse, UserAuthDTO, UserDTO, PaginatorList
from src.user_service import crud, auth_functions
from src.user_service.auth_functions import validate_password
from src.user_service.external_functions import check_auth_from_external_service, delete_user_sessions
from src.shared.models import User, Role
from src.user_service.schemas import UserCreate, UserUpdate, UserAdminDTO, PasswordForm

user_router = APIRouter()
logger = setup_logger(__name__)
logger.info(f"""
Server start time (UTC): {datetime.now()}
Server timestamp: {int(time.time())}
System timezone: {time.tzname}
Environment timezone: {os.environ.get('TZ', 'Not set')}
""")

bearer = HTTPBearer(auto_error=False)
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_valid_token(request: Request, credentials: HTTPAuthorizationCredentials | None = Security(bearer),
                          api_key: str | None = Security(api_key_scheme)) -> str:
    logger.info(request.headers)
    if api_key == settings.api_key:
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
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


@user_router.post(
    "/user/crud",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthResponse[UserDTO],
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - insufficient privileges"},
        409: {"description": "User already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    }
)
async def create_user(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(get_valid_token)
) -> AuthResponse[UserDTO]:
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
            user_data=user_dict.get("user_data", None),
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
    response_model=AuthResponse[UserDTO],
    responses={
        200: {"description": "User data retrieved successfully"},
        401: {"description": "Unauthorized - invalid token"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def find_user_by_id(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(get_valid_token),
) -> AuthResponse[UserDTO]:
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
            user_data=user_dict.get("user_data", None),
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
            detail=AuthResponse(
                token=token,
                data={"message": "Internal server error"}
            ).model_dump()
        )


@user_router.post(
    "/user/authenticate",
    response_model=AuthResponse[UserDTO],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Authentication successful"},
        401: {"description": "Invalid credentials"},
        403: {"description": "Account inactive"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def auth_user(
        user_auth_data: UserAuthDTO,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(get_valid_token),
) -> AuthResponse[UserDTO]:
    """
    Authenticates user credentials and returns user profile if valid.

    Args:
        user_auth_data: Contains identifier (username/email) and password
        db: Database session
        token: jwt token or api key

    Returns:
        Authenticated user's profile data

    Raises:
        HTTPException: 401 for invalid credentials
        HTTPException: 403 for inactive accounts
    """
    result = AuthResponse(token=token)
    try:
        # Authentication attempt
        user = await crud.authenticate_user(
            db,
            user_auth_data.identifier,
            user_auth_data.password
        )

        if not user:
            logger.warning(f"Failed authentication attempt for: {user_auth_data.identifier}")
            result.data = {"message": "Invalid credentials"}
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.model_dump()
            )

        # Account activity check
        if not getattr(user, 'is_active', True):
            logger.warning(f"Login attempt for inactive account: {user.id}")
            result.data = {"message": "Inactive account"}
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.model_dump()
            )

        logger.info(f"Successful authentication for user: {user.id}")
        result.data = UserDTO(**user.to_dict())
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@user_router.get(
    "/user/crud",
    response_model=AuthResponse[PaginatorList[UserAdminDTO]],
    responses={
        200: {"description": "List of users matching search criteria"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def get_users(
        page: int = Query(1, description="Page number"),
        count: int = Query(10, description="Number of users to return"),
        username: str | None = Query(None, description="Filter by username (partial match)"),
        email: str | None = Query(None, description="Filter by email (partial match)"),
        first_name: str | None = Query(None, description="Filter by first name (partial match)"),
        last_name: str | None = Query(None, description="Filter by last name (partial match)"),
        user_id: int | None = Query(None, description="Filter by exact user ID"),
        role: str | None = Query(None, description="Filter by role (partial match)"),
        created_from: datetime | None = Query(None, description="Filter by creation date (from)"),
        created_to: datetime | None = Query(None, description="Filter by creation date (to)"),
        updated_from: datetime | None = Query(None, description="Filter by update date (from)"),
        updated_to: datetime | None = Query(None, description="Filter by update date (to)"),
        sort_by: list[str] = Query(
            ["created_at"],
            description="Fields to sort by (comma-separated)"
        ),
        sort_order: list[str] = Query(
            ["desc"],
            description="Sort order for each field (asc/desc)"
        ),
        db: AsyncSession = Depends(get_db),
        token: str = Depends(get_valid_token),
) -> AuthResponse[PaginatorList[UserAdminDTO]]:
    """
    Search and filter users with advanced querying capabilities

    Features:
    - Multi-field filtering with partial matching (ILIKE)
    - Date range filtering
    - Multi-column sorting
    - Pagination-ready (use with skip/limit parameters)

    Security:
    - Requires valid authentication token
    - Returns only non-sensitive user data

    Examples:
    - /user/crud?username=john&role=admin
    - /user/crud?created_from=2023-01-01&sort_by=username&sort_order=asc
    """
    result = AuthResponse(token=token, data={})
    logger.info(decode_token(token))
    try:
        if page < 1:
            result.data = {"message": "Invalid page number"}
            logger.error(f"Invalid page number {page}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.model_dump())

        if count < 1:
            result.data = {"message": "Invalid number of users per page"}
            logger.error(f"Invalid number of users per page number {count}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.model_dump())

        # Log the search attempt (mask sensitive parameters)
        logger.info(
            "User search initiated",
            extra={
                "extra_data": {
                    "filters": {
                        "username": username[:3] + "..." if username else None,
                        "email": email[:3] + "..." if email else None,
                        "user_id": user_id,
                        "role": role
                    },
                    "sorting": {
                        "by": sort_by,
                        "order": sort_order
                    }
                }
            }
        )
        if len(sort_by) != len(sort_order):
            logger.error(f"Sort_by and Sort_order must have same length",
                         extra={
                             "extra_data": {
                                 "sort_by": sort_by,
                                 "sort_order": sort_order
                             }
                         })
            result.data = {"message": "Sort_by and Sort_order must have same length"}
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.model_dump())

        # Execute the search
        users = await crud.search_users(
            db=db,
            filters={
                "username": username,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "id": user_id,
                "role": role,
                "created_from": created_from,
                "created_to": created_to,
                "updated_from": updated_from,
                "updated_to": updated_to,
            },
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            count=count
        )

        # Log results
        logger.info(
            f"User search completed. Found {len(users)} matching records",
            extra={
                "result_count": len(users),
                "first_user_id": users[0].id if users else None
            }
        )
        logger.info([user.to_dict() for user in users])
        result.data = PaginatorList(
            page=page,
            page_count=len(users) // count + 1,
            items_per_page=count,
            item_count=len(users),
            items=[UserAdminDTO(**user.to_dict()) for user in users]
        )
        return result

    except HTTPException:
        logger.warning("User search failed - authorization error")
        raise
    except Exception as e:
        result.data = {"message": "Internal server error"}
        logger.error(
            "User search failed unexpectedly",
            exc_info=True,
            extra={
                "extra_data": {
                    "error": str(e)
                }
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@user_router.delete(
    "/user/crud/{user_id}",
    response_model=AuthResponse[UserDTO],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User deleted successfully"},
        400: {"description": "Bad request - deletion failed"},
        401: {"description": "Unauthorized - invalid token"},
        403: {"description": "Forbidden - insufficient privileges"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def delete_user_by_id(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(get_valid_token),
) -> AuthResponse[UserDTO]:
    """
    Delete a user account after validation checks

    Security Flow:
    1. Validate authentication token
    2. Verify target user exists
    3. Check requester's permissions
    4. Delete user if authorized

    Rules:
    - Users can delete their own account
    - Admins can delete any account
    - Cannot delete accounts with higher privilege level

    Args:
        user_id: ID of user to delete
        db: Database session
        token: Validated JWT token

    Returns:
        AuthResponse with deleted user data

    Raises:
        HTTPException: For any validation or authorization failure
    """
    result = AuthResponse(token=token, data={"message": ""})

    try:
        # 1. Get target user
        user = await crud.get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"User not found | ID: {user_id}")
            result.data = {"message": "User not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        # 2. Check permissions
        decoded_token = decode_token(token)
        requester_role = Role(decoded_token["role"])
        target_role = user.role
        if target_role.level() > requester_role.level():
            logger.warning(
                f"Privilege escalation attempt | "
                f"Requester: {requester_role.value} | "
                f"Target: {target_role.value}"
            )
            result.data = {"message": "Cannot delete higher-privileged account"}
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.model_dump()
            )

        # 3. Perform deletion
        deleted_user = await crud.delete_user(db, user)
        if not deleted_user:
            logger.error(f"Deletion failed | User ID: {user_id}")
            result.data = {"message": "Deletion failed"}
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.model_dump()
            )

        # 7. Log and return success
        logger.info(
            f"User deleted successfully | "
            f"ID: {user_id} | "
            f"Role: {target_role.value}"
        )

        result.data = UserDTO(**deleted_user.to_dict())
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"User deletion error | ID: {user_id} | Error: {str(e)}",
            exc_info=True
        )
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@user_router.get(
    "/user/me",
    response_model=AuthResponse[UserDTO],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"description": "Unauthorized - invalid or missing token"},
        404: {"description": "User not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def get_profile(
        token: str = Depends(get_valid_token),
        db: AsyncSession = Depends(get_db)
) -> AuthResponse[UserDTO]:
    """
    Get current user's profile using their access token

    Security Flow:
    1. Validate JWT token
    2. Extract user ID from token
    3. Fetch user from database

    Args:
        token: Valid JWT access token
        db: Database session

    Returns:
        AuthResponse containing UserDTO if found

    Raises:
        HTTPException: 401 if token invalid, 404 if user not found
    """
    result = AuthResponse(token=token, data={"message": "User not found"})

    try:
        payload = decode_token(token)
        if not payload or not payload.get("sub"):
            logger.warning(f"Invalid token payload | Token: {token}")
            result.data = {"message": "Invalid token"}
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.model_dump()
            )
        logger.info(f"Token decoded successfully | ID: {payload['sub']}")
        user_id = int(payload["sub"])
        user = await crud.get_user_by_id(db, user_id)
        if not user:
            logger.warning(f"User not found | ID: {user_id}")
            result.data = {"message": "User not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        logger.info(f"Profile retrieved | User ID: {user.id}")
        result.data = UserDTO(**user.to_dict())
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected profile retrieval error | Error: {str(e)}")
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@user_router.patch(
    "/user/crud/{user_id}/password_update",
    status_code=status.HTTP_200_OK,
    response_model=AuthResponse[UserDTO],
    responses={
        200: {"description": "Password successfully updated"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        409: {"description": "User was already updated"},
        422: {"description": "Validation error"},
        500: {"description": "Internal Server Error"}
    }
)
async def update_password(
        password_form: PasswordForm,
        user_id: int,
        token: str = Depends(get_valid_token),
        db: AsyncSession = Depends(get_db)
) -> AuthResponse[UserDTO]:
    """
    Update user password with full security checks

    Security Flow:
    1. Authenticates the request using JWT token
    2. Verifies user exists
    3. Checks privilege levels
    4. Validates password complexity
    5. Checks version to prevent concurrent modifications
    6. Terminates all active sessions after password change

    Args:
        password_form: Form with new password and user version
        user_id: User ID for updating password
        token: Valid JWT access token or api key
        db: Database session

    Returns:
        AuthResponse containing updated UserDTO

    """
    result = AuthResponse(token=token, data={"message": "Password update in progress"})

    try:
        # Token validation
        payload = decode_token(token)
        if not payload or not payload.get("sub"):
            logger.error(f"Invalid token payload | Token: {token[:8]}...")
            result.data = {"message": "Invalid token"}
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.model_dump()
            )
        logger.debug(f"Token validated for user_id: {payload.get('sub')}")

        # User lookup
        user: User = await crud.get_user_by_id(db, user_id)
        if not user:
            logger.error(f"User not found | ID: {user_id}")
            result.data = {"message": "User not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )
        logger.debug(f"User found | ID: {user.id} | Username: {user.username}")

        # Privilege check
        if user.role.level() > Role(payload.get("role")).level():
            logger.warning(
                f"Privilege escalation attempt | "
                f"Requester role: {payload.get('role')} | "
                f"Target role: {user.role.value}"
            )
            result.data = {"message": "Cannot update higher-privileged account"}
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=result.model_dump()
            )

        # Version check
        if user.version > password_form.user_version:
            logger.warning(
                f"Version conflict | "
                f"Current version: {user.version} | "
                f"Submitted version: {password_form.user_version}"
            )
            result.data = {"message": "User was already updated"}
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result.model_dump()
            )

        # Password validation
        if not validate_password(password_form.new_password):
            logger.error("Password complexity requirements not met")
            result.data = {"message": "Password must contain uppercase, lowercase, number and special character"}
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.model_dump()
            )
        logger.debug("Password validated successfully")

        # Password update
        try:
            user_update = await crud.update_user_password(db=db, user_id=user_id, password_form=password_form)
            logger.info(f"Password updated for user | ID: {user_id}")
        except Exception as e:
            logger.error(f"Database update failed: {str(e)}", exc_info=True)
            result.data = {"message": "Failed to update password"}
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.model_dump()
            )

        # Session termination
        try:
            response = await delete_user_sessions(user_id, api_key=settings.api_key)
            if error := verify_response(response):
                logger.error(f"Session termination failed: {error}")
                result.data["warning"] = "Password changed but sessions may still be active"
            else:
                logger.info(f"Sessions terminated | User ID: {user_id}")
        except Exception as e:
            logger.error(f"Session termination error: {str(e)}")
            result.data["warning"] = "Password changed but session cleanup failed"

        return AuthResponse(
            data=UserDTO(**user_update.to_dict()),
            token=token
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.critical(
            f"Unexpected error in password update | "
            f"User ID: {user_id} | "
            f"Error: {str(e)}",
            exc_info=True
        )
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@user_router.patch(
    "/user/crud/{user_id}",
    response_model=AuthResponse[UserDTO],
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "User updated successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized - invalid token"},
        403: {"description": "Forbidden - insufficient privileges"},
        404: {"description": "User not found"},
        409: {"description": "User is already updated"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def update_user_by_id(
        user_id: int,
        user: UserUpdate,
        token: str = Depends(get_valid_token),
        db: AsyncSession = Depends(get_db)
) -> AuthResponse[UserDTO]:
    """
    Update user information by ID

    Performs the following operations:
    1. Validates authentication token
    2. Checks user existence
    3. Updates user data
    4. Returns updated user information

    Security:
    - Requires valid JWT token
    - Users can only update their own information (or admin access required)
    """
    result = AuthResponse(token=token, data={"message": "Update in progress"})

    try:
        # Token validation
        payload = decode_token(token)
        if not payload or not payload.get("sub"):
            logger.error(f"Invalid token payload | Token: {token[:8]}...")
            result.data = {"message": "Invalid token"}
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.model_dump()
            )

        db_user = await crud.get_user_by_id(db=db, user_id=user_id)
        if not db_user:
            logger.error(f"User not found | ID: {user_id}")
            result.data = {"message": "User not found"}
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.model_dump())
        logger.info(f"Found user | ID: {user_id}")

        if db_user.version > user.version:
            logger.error(f"User was already updated | ID: {user_id}")
            result.data = {"message": f"User was already updated | ID: {user_id}"}
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=result.model_dump())
        logger.info(f"User version | Version:{user.version}")
        user.version += 1

        if db_user.role.level() > Role(payload.get("role")).level():
            logger.error("Insufficient privileges")
            result.data = {"message": "Insufficient privileges"}
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=result.model_dump())

        # Update user
        db_user = await crud.update_user(db, user_id=user_id, user_update=user)

        if not db_user:
            logger.warning(f"User not found | ID: {user_id}")
            result.data = {"message": "User not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        logger.info(f"User updated | ID: {user_id} | Username: {db_user.username}")
        return AuthResponse(
            token=token,
            data=UserDTO(**db_user.to_dict())
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error updating user | ID: {user_id} | Error: {str(e)}",
            exc_info=True
        )
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )
