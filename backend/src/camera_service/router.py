import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends, Request, Security, Query, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from src.camera_service import crud
from src.camera_service.crud import count_groups_with_name
from src.camera_service.external_functions import check_auth_from_external_service
from src.camera_service.schemas import CameraGroupSchema, CameraGroupDTO, CameraGroupAdminDTO, CameraSchema, \
    CameraAdminDTO
from src.shared.config import settings
from src.shared.database import SessionLocal
from src.shared.logger_setup import setup_logger
from src.shared.schemas import PaginatorList, AuthResponse, CameraDTO

camera_router = APIRouter()
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


@camera_router.post(
    "/camera/crud/groups",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthResponse[CameraGroupDTO],
    responses={
        201: {"description": "Camera group created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - insufficient privileges"},
        409: {"description": "Camera group already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    }
)
async def create_camera_group(
        camera_group: CameraGroupSchema,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(get_valid_token)
) -> AuthResponse[CameraGroupDTO]:
    """
    Creates a new camera group with validation checks.

    Security Flow:
    1. Validates authentication token
    2. Checks camera group name availability
    3. Creates group record

    Args:
        camera_group: Camera group creation data
        db: Database session
        token: Validated authentication token

    Returns:
        AuthResponse with created group data

    Raises:
        HTTPException: For any validation or authorization failure
    """
    result = AuthResponse(token=token)

    try:
        # 1. Log creation attempt (without sensitive data)
        logger.info(
            f"CameraGroup creation attempt | "
            f"Schema: {camera_group} | "
        )

        # 2. Check name availability
        existing_camera_group = await crud.get_camera_group_by_name(db=db, camera_group_name=camera_group.name)
        if existing_camera_group:
            logger.warning(f"Camera group name taken | Name: {camera_group.name}")
            result.data = {"message": "Camera group name already in use"}
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result.model_dump()
            )

        # 3. Create camera group
        new_camera_group = await crud.create_camera_group(db=db, camera_group=camera_group)
        if not new_camera_group:
            logger.error("Camera group creation failed")
            result.data = {"message": "Camera group creation failed"}
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.model_dump()
            )

        # 4. Return success response
        logger.info(f"Camera group created | ID: {new_camera_group.id}")
        camera_group_dict = new_camera_group.to_dict()
        result.data = CameraGroupDTO(**camera_group_dict)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Camera group creation error: {str(e)}", exc_info=True)
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@camera_router.get(
    "/camera/crud/groups/{camera_group_id}",
    response_model=AuthResponse[CameraGroupDTO],
    responses={
        200: {"description": "Group data retrieved successfully"},
        401: {"description": "Unauthorized - invalid token"},
        403: {"description": "Forbidden - insufficient permissions"},
        404: {"description": "Group not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def get_camera_group_by_id(camera_group_id: int, db: AsyncSession = Depends(get_db),
                                 token=Depends(get_valid_token)) -> AuthResponse[CameraGroupDTO]:
    """
        Retrieves camera group information by ID with access control.

        Security Flow:
        1. Validates authentication token
        2. Checks requested group exists
        3. Returns group data

        Permissions:
        - Service accounts cannot do anything

        Args:
            camera_group_id: ID of user to retrieve
            db: Database session
            token: Validated authentication token

        Returns:
            AuthResponse with group data

        Raises:
            HTTPException: For authorization or not found errors
        """
    result = AuthResponse(token=token)
    try:
        camera_group = await crud.get_camera_group_by_id(db=db, camera_group_id=camera_group_id)
        if not camera_group:
            logger.error(f"Camera group not found failed | ID: {camera_group_id}")
            result.data = {"message": "Camera group not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )
        logger.info(f"Camera group retrieved | ID: {camera_group_id} {camera_group.to_dict()}")
        camera_group_dict = camera_group.to_dict()
        result.data = CameraGroupDTO(**camera_group_dict)
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Group lookup error | ID: {camera_group_id} | Error: {str(e)}",
            exc_info=True
        )
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@camera_router.get(
    "/camera/crud/groups",
    response_model=AuthResponse[PaginatorList[CameraGroupDTO]],
    responses={
        200: {"description": "List of users matching search criteria"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def get_user_camera_groups(
        page: int = Query(1, description="Page number"),
        count: int = Query(10, description="Number of users to return"),
        name: str | None = Query(None, description="Filter by group name (partial match)"),
        address: str | None = Query(None, description="Filter by address (partial match)"),
        description: str | None = Query(None, description="Filter by description (partial match)"),
        group_id: int | None = Query(None, description="Filter by group id(partial match)"),
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
        token: str = Depends(get_valid_token)
) -> AuthResponse[PaginatorList[CameraGroupAdminDTO]]:
    """
    Search and filter users with advanced querying capabilities

    Features:
    - Multi-field filtering with partial matching (ILIKE)
    - Date range filtering
    - Multi-column sorting
    - Pagination-ready (use with skip/limit parameters)

    Security:
    - Requires valid authentication token

    Examples:
    /camera/crud?created_from=2024-01-01T00:00:00&sort_by=name&sort_by=id&sort_order=asc&sort_order=desc
    """
    result = AuthResponse(token=token, data={})
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
                        "id": group_id,
                        "name": name if name else None,
                        "description": description if description else None,
                        "address": address if address else None,
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
        groups = await crud.search_groups(
            db=db,
            filters={
                "id": group_id,
                "name": name,
                "description": description,
                "address": address,
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
            f"User search completed. Found {len(groups)} matching records",
            extra={
                "result_count": len(groups),
                "first_user_id": groups[0].id if groups else None
            }
        )
        logger.info([group.to_dict() for group in groups])
        result.data = PaginatorList(
            page=page,
            page_count=len(groups) // count + 1,
            items_per_page=count,
            item_count=len(groups),
            items=[CameraGroupAdminDTO(**group.to_dict()) for group in groups]
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


@camera_router.delete(
    "/camera/crud/groups/{group_id}",
    response_model=AuthResponse[CameraGroupDTO],
    responses={
        200: {"description": "Successful deletion"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def delete_camera_group(
        group_id: int,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(get_valid_token)
)  -> AuthResponse[CameraGroupDTO]:
    """
    Delete a camera group account after validation checks

    Security Flow:
    1. Validate authentication token
    2. Verify target group exists
    3. Delete target group

    Rules:
    - Services cannot delete anything

    Args:
        group_id: ID of camera group to delete
        db: Database session
        token: Validated JWT token

    Returns:
        AuthResponse with deleted group data

    Raises:
        HTTPException: For any validation or authorization failure
    """
    result = AuthResponse(token=token, data={"message": ""})

    try:
        # 1. Get target user
        camera_group = await crud.get_camera_group_by_id(db=db, camera_group_id=group_id)
        if not camera_group:
            logger.warning(f"Camera group not found | ID: {group_id}")
            result.data = {"message": "Camera group not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        # 2. Perform deletion
        deleted_group = await crud.delete_group(db=db, camera_group=camera_group)
        if not deleted_group:
            logger.error(f"Deletion failed | Group ID: {group_id}")
            result.data = {"message": "Deletion failed"}
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.model_dump()
            )

        # 3. Log and return success
        logger.info(
            f"Group deleted successfully | "
            f"ID: {group_id} | "
        )

        result.data = CameraGroupDTO(**deleted_group.to_dict())
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Group deletion error | ID: {group_id} | Error: {str(e)}",
            exc_info=True
        )
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@camera_router.patch(
    "/camera/crud/groups/{group_id}",
    response_model=AuthResponse[CameraGroupDTO],
    responses={
        200: {"description": "Successful update"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def patch_camera_group(
        group_id: int,
        camera_update: CameraGroupSchema,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(get_valid_token)
)-> AuthResponse[CameraGroupDTO]:
    """
    Update a camera group account after validation checks

    Security Flow:
    1. Validate authentication token
    2. Verify target group exists
    3. Verify camera group version
    4. Update camera group

    Rules:
    - Services cannot update anything

    Args:
        group_id: ID of camera group to update
        camera_update: Update camera group schema
        db: Database session
        token: Validated JWT token

    Returns:
        AuthResponse with updated group data

    Raises:
        HTTPException: For any validation or authorization failure
    """
    result = AuthResponse(token=token, data={"message": ""})

    try:
        # 1. Get target user
        camera_group = await crud.get_camera_group_by_id(db=db, camera_group_id=group_id)
        if not camera_group:
            logger.warning(f"Camera group not found | ID: {group_id}")
            result.data = {"message": "Camera group not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        group_count = await count_groups_with_name(db=db, name=camera_update.name)
        if not(group_count == 1 and camera_group.name == camera_update.name):
            logger.error(f"Camera group name {camera_update.name} is not available")
            result.data = {"message": f"Camera group name {camera_update.name} is not available"}
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result.model_dump()
            )
        logger.info(f"Camera group name {camera_update.name} is available")
        # 2. Check version
        if camera_group.version > camera_update.version:
            logger.error(f"Camera group {group_id} was updated to {camera_group.version}")
            result.data = {"message": f"Camera group {group_id} was already updated"}
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result.model_dump()
            )
        camera_update.version +=1
        logger.info(f"Camera group {group_id} new version is {camera_update.version}")

        # 3. Perform deletion
        updated_group = await crud.update_group(db=db, group_id=group_id, camera_group=camera_update)
        if not updated_group:
            logger.error(f"Update failed | Group ID: {group_id}")
            result.data = {"message": "Update failed"}
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.model_dump()
            )

        # 4. Log and return success
        logger.info(
            f"Group updated successfully | "
            f"ID: {group_id} | "
        )

        result.data = CameraGroupDTO(**updated_group.to_dict())
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Group update error | ID: {group_id} | Error: {str(e)}",
            exc_info=True
        )
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )




@camera_router.post(
    "/camera/crud/groups/{group_id}/cameras",
    response_model=AuthResponse[CameraDTO],
    responses={
        200: {"description": "Successful addition"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def create_camera(
        group_id: int,
        camera_data: CameraSchema,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(get_valid_token)
)-> AuthResponse[CameraGroupDTO]:
    """
    Creates a new camera with validation checks.

    Security Flow:
    1. Validates authentication token
    2. Check existing camera group
    3. Checks camera name and camera link availability
    4. Creates camera record

    Args:
        group_id: ID of camera group
        camera_data: Camera creation data
        db: Database session
        token: Validated authentication token

    Returns:
        AuthResponse with created camera data

    Raises:
        HTTPException: For any validation or authorization failure
    """
    result = AuthResponse(token=token)

    try:
        # 1. Log creation attempt (without sensitive data)
        logger.info(
            f"Camera creation attempt | "
            f"Schema: {camera_data} | "
        )

        camera_group = await crud.get_camera_group_by_id(db=db, camera_group_id=group_id)
        if not camera_group:
            logger.error(f"Camera group not found | ID: {group_id}")
            result.data = {"message": "Camera group not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )


        # 3. Check name and link availability
        existing_cameras = await crud.count_cameras_with_name(db=db, name=camera_data.name)
        if existing_cameras:
            logger.warning(f"Camera name taken | Name: {camera_data.name}")
            result.data = {"message": "Camera name already in use"}
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result.model_dump()
            )
        existing_cameras = await crud.count_cameras_with_link(db=db, camera_link=camera_data.address_link)
        if existing_cameras:
            logger.warning(f"Camera link taken | Link: {camera_data.address_link}")
            result.data = {"message": "Camera link already in use"}
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result.model_dump()
            )

        # 3. Create camera group
        new_camera = await crud.create_camera(db=db, camera=camera_data, camera_group=camera_group)
        if not new_camera:
            logger.error("Camera creation failed")
            result.data = {"message": "Camera creation failed"}
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.model_dump()
            )

        # 4. Return success response
        logger.info(f"Camera created | ID: {new_camera.id}")
        camera_dict = new_camera.to_dict()
        result.data = CameraDTO(**camera_dict)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Camera creation error: {str(e)}", exc_info=True)
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@camera_router.delete(
    "/camera/crud/groups/{group_id}/cameras/{camera_id}",
    response_model=AuthResponse[CameraDTO],
    responses={
        200: {"description": "Successful delete"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def delete_camera(
        group_id: int,
        camera_id: int,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(get_valid_token)
)-> AuthResponse[CameraGroupDTO]:
    """
    Creates a new camera with validation checks.

    Security Flow:
    1. Validates authentication token
    2. Checks existing camera group
    3. Checks existing camera record
    4. Deletes camera record

    Args:
        group_id: ID of camera group
        camera_id: ID of camera to delete
        db: Database session
        token: Validated authentication token

    Returns:
        AuthResponse with deleted camera data

    Raises:
        HTTPException: For any validation or authorization failure
    """
    result = AuthResponse(token=token)

    try:
        # 1. Log creation attempt (without sensitive data)
        logger.info(
            f"Camera deletion attempt | "
            f"Camera: {group_id} | {camera_id} | "
        )

        camera_group = await crud.get_camera_group_by_id(db=db, camera_group_id=group_id)
        if not camera_group:
            logger.error(f"Camera group not found | ID: {group_id}")
            result.data = {"message": "Camera group not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        camera = await crud.get_camera_by_id(db=db, camera_id=camera_id)
        if not camera:
            logger.error(f"Camera not found | ID: {camera_id}")
            result.data = {"message": "Camera not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        deleted_camera = await crud.delete_camera_by_id(db=db, camera_id=camera_id)
        if not deleted_camera:
            logger.error(f"Camera not found | ID: {camera_id}")
            result.data = {"message": "Camera not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )
        # 4. Return success response
        logger.info(f"Camera deleted | ID: {deleted_camera.id}")
        camera_dict = deleted_camera.to_dict()
        result.data = CameraDTO(**camera_dict)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Camera deletion error: {str(e)}", exc_info=True)
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )

@camera_router.get(
    "/camera/crud/groups/{group_id}/cameras/{camera_id}",
    response_model=AuthResponse[CameraDTO],
    responses={
        200: {"description": "Successful return"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def get_camera(
        group_id: int,
        camera_id: int,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(get_valid_token)
)-> AuthResponse[CameraGroupDTO]:
    """
    Get a camera with validation checks.

    Security Flow:
    1. Validates authentication token
    2. Checks existing camera group
    3. Checks existing camera record
    4. Returns camera record

    Args:
        group_id: ID of camera group
        camera_id: ID of camera to delete
        db: Database session
        token: Validated authentication token

    Returns:
        AuthResponse with deleted camera data

    Raises:
        HTTPException: For any validation or authorization failure
    """
    result = AuthResponse(token=token)

    try:
        # 1. Log creation attempt (without sensitive data)
        logger.info(
            f"Camera getting attempt | "
            f"Camera: {group_id} | {camera_id} | "
        )

        camera_group = await crud.get_camera_group_by_id(db=db, camera_group_id=group_id)
        if not camera_group:
            logger.error(f"Camera group not found | ID: {group_id}")
            result.data = {"message": "Camera group not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        camera = await crud.get_camera_by_id(db=db, camera_id=camera_id)
        if not camera or camera.group_id != group_id:
            logger.error(f"Camera not found | ID: {camera_id}")
            result.data = {"message": "Camera not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )

        get_camera = await crud.get_camera_by_id(db=db, camera_id=camera_id)
        if not get_camera:
            logger.error(f"Camera not found | ID: {camera_id}")
            result.data = {"message": "Camera not found"}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.model_dump()
            )
        # 4. Return success response
        logger.info(f"Camera get | ID: {get_camera.id}")
        camera_dict = get_camera.to_dict()
        result.data = CameraDTO(**camera_dict)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Camera getting error: {str(e)}", exc_info=True)
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@camera_router.get(
    "/camera/crud/groups/{group_id}/cameras",
    response_model=AuthResponse[PaginatorList[CameraAdminDTO]],
    responses={
        200: {"description": "List of cameras matching search criteria"},
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def get_cameras(
        group_id: int= Path(..., description="ID of camera group"),
        page: int = Query(1, description="Page number"),
        count: int = Query(10, description="Number of users to return"),
        name: str | None = Query(None, description="Filter by name (partial match)"),
        address_link: str | None = Query(None, description="Filter by address_link (partial match)"),
        camera_id: int | None = Query(None, description="Filter by camera id (partial match)"),
        is_active: bool | None = Query(None, description="Filter by active (true/false)"),
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
        token: str = Depends(get_valid_token)
) -> AuthResponse[PaginatorList[CameraAdminDTO]]:
    """
    Search and filter cameras with advanced querying capabilities

    Features:
    - Multi-field filtering with partial matching (ILIKE)
    - Date range filtering
    - Multi-column sorting
    - Pagination-ready (use with skip/limit parameters)

    Security:
    - Requires valid authentication token

    Examples:
    - /camera/crud/groups/5/cameras?created_from=2024-01-01T00:00:00&camera_id=2&sort_by=name&sort_by=id&sort_order=asc&sort_order=desc
    """
    result = AuthResponse(token=token, data={})
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
            "Camera search initiated",
            extra={
                "extra_data": {
                    "filters": {
                        "id": camera_id,
                        "name": name if name else None,
                        "address_link": address_link if address_link else None,
                        "is_active": is_active,
                        "created_from": created_from if created_from else None,
                        "created_to": created_to if created_to else None,
                        "updated_from": updated_from if updated_from else None,
                        "updated_to": updated_to if updated_to else None,
                        "group_id": group_id,
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
        cameras = await crud.search_cameras(
            db=db,
            filters={
                "id": camera_id,
                "name": name,
                "address_link": address_link,
                "is_active": is_active,
                "group_id": group_id,
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
            f"Cameras search completed. Found {len(cameras)} matching records",
            extra={
                "result_count": len(cameras),
                "first_user_id": cameras[0].id if cameras else None
            }
        )
        logger.info([camera.to_dict() for camera in cameras])
        result.data = PaginatorList(
            page=page,
            page_count=len(cameras) // count + 1,
            items_per_page=count,
            item_count=len(cameras),
            items=[CameraAdminDTO(**camera.to_dict()) for camera in cameras]
        )
        return result

    except HTTPException:
        logger.warning("Camera search failed - authorization error")
        raise
    except Exception as e:
        result.data = {"message": "Internal server error"}
        logger.error(
            "Camera search failed unexpectedly",
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