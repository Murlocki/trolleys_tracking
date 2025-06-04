import os
import time
from datetime import datetime

from fastapi import HTTPException, status, APIRouter, Depends, Request, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

from src.camera_reader_service.camera_process_management.CameraReaderManager import CameraReaderManager
from src.camera_reader_service.external_functions import find_camera_by_id
from src.camera_reader_service.schemas import CameraProcess, ActivationProps
from src.camera_service.external_functions import check_auth_from_external_service
from src.camera_service.schemas import CameraGroupDTO
from src.shared.common_functions import verify_response
from src.shared.config import settings
from src.shared.logger_setup import setup_logger
from src.shared.schemas import AuthResponse, CameraDTO

camera_reader_router = APIRouter()
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


@camera_reader_router.post(
    "/camera_reader/groups/{group_id}/cameras/{camera_id}/activate",
    status_code=status.HTTP_200_OK,
    response_model=AuthResponse[CameraProcess],
    responses={
        201: {"description": "Camera reading activated successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - insufficient privileges"},
        409: {"description": "Camera group already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    }
)
async def activate_camera_reader(
        activation_props: ActivationProps,
        group_id: int,
        camera_id: int,
        token: str = Depends(get_valid_token)
) -> AuthResponse[CameraProcess]:
    result = AuthResponse(token=token)

    try:
        # 1. Log creation attempt (without sensitive data)
        logger.info(
            f"Camera activation attempt | "
            f"Schema: {group_id} | {camera_id} | {activation_props}"
        )

        # 2. Check name availability
        response = await find_camera_by_id(group_id=group_id, camera_id=camera_id, api_key=settings.api_key)
        if error := verify_response(response, 200):
            logger.warning(f"Camera not found: {error['detail']['data']['message']} with code: {error['status_code']}")
            result.data = {"message": error["detail"]["data"]["message"]}
            raise HTTPException(
                status_code=error["status_code"],
                detail=result.model_dump()
            )
        camera = CameraDTO(**response.json()["data"])
        activate_result = await CameraReaderManager.activate_camera(camera=camera, activation_props = activation_props)
        if not activate_result:
            result.data = {"message": f"Camera activation failed for {camera_id}"}
            logger.error(f"Camera activation failed for {camera_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.model_dump()
            )

        # 4. Return success response
        logger.info(f"Camera activated | ID: {camera.id}")
        result.data = activate_result
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Camera activation error: {str(e)}", exc_info=True)
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@camera_reader_router.post(
    "/camera_reader/groups/{group_id}/cameras/{camera_id}/deactivate",
    status_code=status.HTTP_200_OK,
    response_model=AuthResponse[CameraProcess],
    responses={
        201: {"description": "Camera reading deactivated successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - insufficient privileges"},
        409: {"description": "Camera group already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    }
)
async def deactivate_camera_reader(
        group_id: int,
        camera_id: int,
        token: str = Depends(get_valid_token)
) -> AuthResponse[CameraProcess]:
    result = AuthResponse(token=token)

    try:
        # 1. Log creation attempt (without sensitive data)
        logger.info(
            f"Camera deactivation attempt | "
            f"Schema: {group_id} | {camera_id} | "
        )

        # 2. Check name availability
        response = await find_camera_by_id(group_id=group_id, camera_id=camera_id, api_key=settings.api_key)
        if error := verify_response(response, 200):
            logger.warning(f"Camera not found: {error['detail']['data']['message']} with code: {error['status_code']}")
            result.data = {"message": error["detail"]["data"]["message"]}
            raise HTTPException(
                status_code=error["status_code"],
                detail=result.model_dump()
            )
        camera = CameraDTO(**response.json()["data"])
        deactivate_result = await CameraReaderManager.deactivate_camera(camera=camera)
        if not deactivate_result:
            result.data = {"message": f"Camera deactivation failed for {camera_id}"}
            logger.error(f"Camera deactivation failed for {camera_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.model_dump()
            )

        # 4. Return success response
        logger.info(f"Camera deactivated | ID: {camera.id}")
        result.data = deactivate_result
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Camera deactivation error: {str(e)}", exc_info=True)
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )


@camera_reader_router.get(
    "/camera_reader/groups/{group_id}/cameras/{camera_id}/status",
    status_code=status.HTTP_200_OK,
    response_model=AuthResponse,
    responses={
        201: {"description": "Camera reading status extraction successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - insufficient privileges"},
        409: {"description": "Camera group already exists"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    }
)
async def get_camera_reader_status(
        group_id: int,
        camera_id: int,
        token: str = Depends(get_valid_token)
) -> AuthResponse:
    result = AuthResponse(token=token)

    try:
        # 1. Log creation attempt (without sensitive data)
        logger.info(
            f"Camera status extraction attempt | "
            f"Schema: {group_id} | {camera_id} | "
        )

        # 2. Check name availability
        response = await find_camera_by_id(group_id=group_id, camera_id=camera_id, api_key=settings.api_key)
        if error := verify_response(response, 200):
            logger.warning(f"Camera not found: {error['detail']['data']['message']} with code: {error['status_code']}")
            result.data = {"message": error["detail"]["data"]["message"]}
            raise HTTPException(
                status_code=error["status_code"],
                detail=result.model_dump()
            )
        camera = CameraDTO(**response.json()["data"])
        camera_reader_status = await CameraReaderManager.get_camera_status(camera=camera)
        if not camera_reader_status:
            result.data = {"message": f"Camera reader status extraction failed for {camera_id}"}
            logger.error(f"Camera reader status extraction failed for {camera_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.model_dump()
            )

        # 4. Return success response
        logger.info(f"Camera reader status extraction  successed | status: {camera_reader_status}")
        result.data = {"status": camera_reader_status}
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Camera activation error: {str(e)}", exc_info=True)
        result.data = {"message": "Internal server error"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.model_dump()
        )
