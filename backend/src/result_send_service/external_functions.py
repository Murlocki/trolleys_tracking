import httpx
from httpx import Response

from src.result_send_service.endpoints import GET_USER_SUBS
from src.session_service.endpoints import CHECK_AUTH, FIND_USER_BY_ID
from src.shared.logger_setup import setup_logger
from src.shared.schemas import TokenModelResponse

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
            "authorization": f"Bearer {access_token}"
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

async def find_user_subscriptions(user_id: int, api_key: str) -> Response:
    """
    Find user subscriptions
    :param api_key: api key
    :param user_id: username for finding user
    :return: response from external service
    """
    headers = {
        "content-type": "application/json",
        "X-API-Key": api_key,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GET_USER_SUBS}/{user_id}/subscriptions",
            headers=headers,
        )
        logger.info(f"Find user user_id: {user_id} subscriptions with response {response.json()}")
        return response