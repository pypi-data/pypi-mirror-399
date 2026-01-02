import httpx
from typing import Optional, Any, Dict
from hiinsta.types import Update, InstagramUser
from hiinsta.types.exeptions import InstagramApiException

INSTAGRAM_BASE_URL = "https://graph.instagram.com"
INSTAGRAM_MESSAGES_ENDPOINT = "/me/messages"
DEFAULT_TIMEOUT = 15.0  # seconds

class InstagramMessenger:
    """
    A class to interact with Instagram's messaging API.
    """
    access_token: str
    request_timeout: Optional[float] = DEFAULT_TIMEOUT
    
    def __init__(self, access_token: str, request_timeout: Optional[float] = DEFAULT_TIMEOUT):
        self.access_token = access_token
        self.request_timeout = request_timeout

    async def send_text(self, text: str, recipient_id: str) -> str:
        """
        Send a text message to a user.
        Args:
            text (str): The text message to send.
            recipient_id (str): The recipient's Instagram user ID.
        Returns:
            str: The message ID of the sent message.
        """
        url = f"{INSTAGRAM_BASE_URL}{INSTAGRAM_MESSAGES_ENDPOINT}"
        payload = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "text": text
            }
        }
        return await self._send_message_payload(payload)
        
    async def send_image(self, image_url: str, recipient_id: str) -> str:
        """
        Send an image or GIF to a user.
        Args:
            image_url (str): The URL of the image or GIF to send.
            recipient_id (str): The recipient's Instagram user ID.
        Returns:
            str: The message ID of the sent message.
        """
        return await self._send_attachment("image", image_url, recipient_id)
    
    async def send_video(self, video_url: str, recipient_id: str) -> str:
        """
        Send a video to a user.
        Args:
            video_url (str): The URL of the video to send.
            recipient_id (str): The recipient's Instagram user ID.
        Returns:
            str: The message ID of the sent message.
        """
        return await self._send_attachment("video", video_url, recipient_id)
    
    async def send_audio(self, audio_url: str, recipient_id: str):
        """
        Send an audio file to a user.
        Args:
            audio_url (str): The URL of the audio file to send.
            recipient_id (str): The recipient's Instagram user ID.
        Returns:
            str: The message ID of the sent message.
        """
        return await self._send_attachment("audio", audio_url, recipient_id)
        
    async def _send_attachment(self, attachment_type: str, attachment_url: str, recipient_id: str):
        """
        Send an attachment (image, video, audio, file) to a user.
        Args:
            attachment_type (str): The type of attachment ('image', 'video', 'audio', 'file').
            attachment_url (str): The URL of the attachment to send.
            recipient_id (str): The recipient's Instagram user ID.
        """
        payload = {
            "recipient": {
                "id": recipient_id
            },
            "message": {
                "attachment": {
                    "type": attachment_type,
                    "payload": {
                        "url": attachment_url
                    }
                }
            }
        }
        return await self._send_message_payload(payload)

    async def _send_message_payload(self, payload: dict) -> str:
        """
        Send a custom payload to Instagram's API messages endpoint with robust error handling.

        Args:
            payload (dict): The payload to send.
            timeout (Optional[float]): Request timeout in seconds. Defaults to DEFAULT_TIMEOUT.

        Returns:
            SendResponse: A mapping with at least the "message_id" and, when available, "recipient_id".

        Raises:
            InstagramApiException: For network errors, non-2xx responses, or malformed responses.
        """
        url = f"{INSTAGRAM_BASE_URL}{INSTAGRAM_MESSAGES_ENDPOINT}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.request_timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
        except httpx.RequestError as e:
            raise InstagramApiException(
                message="Network error while sending payload",
                endpoint=url,
                method="POST",
                payload=payload,
                details=str(e),
            ) from e

        # Non-2xx -> raise a structured exception with parsed error body when possible
        if response.status_code < 200 or response.status_code >= 300:
            raise InstagramApiException.from_httpx_response(
                response,
                endpoint=url,
                method="POST",
                payload=payload,
            )

        # Parse JSON and validate presence of message_id
        try:
            data: Dict[str, Any] = response.json()
        except ValueError:
            raise InstagramApiException(
                message="Response is not valid JSON",
                endpoint=url,
                method="POST",
                payload=payload,
                status_code=response.status_code,
                response_text=response.text,
            )

        message_id = data.get("message_id") or data.get("id")
        if not message_id:
            raise InstagramApiException(
                message="Missing message_id in successful response",
                endpoint=url,
                method="POST",
                payload=payload,
                status_code=response.status_code,
                response_json=data,
            )

        
        return message_id

    async def get_user_data(self, user_id: str) -> InstagramUser:
        """
        Get user data from Instagram.
        Args:
            user_id (str): The Instagram user ID.
        Returns:
            InstagramUser: The user data.
        """
        url = f"{INSTAGRAM_BASE_URL}/{user_id}"
        params = {
            "fields": "id,username,name",
            "access_token": self.access_token
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.request_timeout) as client:
                response = await client.get(url, params=params)
        except httpx.RequestError as e:
             raise InstagramApiException(
                message="Network error while getting user data",
                endpoint=url,
                method="GET",
                payload=None,
                details=str(e),
            ) from e

        if response.status_code != 200:
             raise InstagramApiException.from_httpx_response(
                response,
                endpoint=url,
                method="GET",
                payload=None,
            )
            
        return InstagramUser(**response.json())
        
    @staticmethod
    def process_payload(payload: dict) -> Update:
        try:
            return Update(**payload)
        except Exception as e:
            raise ValueError(f"Invalid payload: {e}")
        