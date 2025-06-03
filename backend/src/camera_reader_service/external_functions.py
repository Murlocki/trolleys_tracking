import httpx
from httpx import Response

from src.camera_reader_service.endpoints import FIND_CAMERA_BY_ID
from src.shared.logger_setup import setup_logger
from src.shared.schemas import TokenModelResponse
from src.user_service.endpoints import CHECK_AUTH

logger = setup_logger(__name__)


async def check_auth_from_external_service(access_token: str) -> TokenModelResponse | None:
    """
    Check auth
    :param access_token:
    :return: json - token old or new
    """
    try:
        headers = {
            "content-type": "application/json",
            "authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(CHECK_AUTH, headers=headers)
            response.raise_for_status()  # Проверяем статусный код на ошибки
            json_data = response.json()
            return json_data
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting {e.request.url!r}.")
    except httpx.HTTPStatusError as e:
        logger.error(f"Error response {e.response.status_code} while requesting {e.request.url!r}.")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    return None


async def find_camera_by_id(group_id: int, camera_id: int, api_key: str) -> Response:
    """
    Find user by username
    :param api_key: api key
    :param group_id: group id for finding camera
    :param camera_id: camera id for finding camera
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
        "X-API-Key": api_key,
    }
    async with httpx.AsyncClient() as client:
        request_string = FIND_CAMERA_BY_ID.replace("group_id", str(group_id)).replace("camera_id", str(camera_id))
        response = await client.get(
            request_string,
            headers=headers,
        )
        logger.info(f"Find camera by camera_id and group+id: {camera_id}|{group_id} with response {response.json()}")
        return response
