from typing import Any, Optional, Dict, Tuple
from urllib.parse import urlparse
import requests
import json

from airflow.hooks.base import BaseHook
from airflow.exceptions import AirflowException


class LarkWebhookHook(BaseHook):
    """
    Airflow hook for interacting with Lark (Feishu) custom bot webhooks.

    This hook allows Airflow to send messages to Lark groups using custom bot webhooks.
    The webhook URL is configured in Airflow connections.

    :param lark_conn_id: The connection ID for the Lark webhook
    :type lark_conn_id: str
    :param timeout: The timeout for the webhook request
    :type timeout: int
    :param retry_limit: The number of retries for the webhook request
    :type retry_limit: int
    """

    conn_name_attr = 'lark_conn_id'
    default_conn_name = 'lark_default'
    conn_type = 'lark_webhook'
    hook_name = 'Lark Webhook'

    def __init__(
        self,
        lark_conn_id: str = default_conn_name,
        timeout: int = 30,
        retry_limit: int = 3,
    ) -> None:
        super().__init__()
        self.lark_conn_id = lark_conn_id
        self.timeout = timeout
        self.retry_limit = retry_limit
        self.base_url: Optional[str] = None
        self.session = requests.Session()

    def get_conn(self) -> requests.Session:
        """Get the connection session."""
        if self.base_url is None:
            conn = self.get_connection(self.lark_conn_id)

            # Parse the webhook URL
            if not conn.host and not conn.schema:
                raise AirflowException(f"No host or schema found in connection {self.lark_conn_id}")

            # Construct the URL from the connection
            url_parts = []
            if conn.schema:
                url_parts.append(conn.schema)
            if conn.host:
                url_parts.append(conn.host)
            if conn.port:
                url_parts.append(f":{conn.port}")
            if conn.extra_dejson and conn.extra_dejson.get('path'):
                url_parts.append(conn.extra_dejson['path'])

            self.base_url = '/'.join(part.strip('/') for part in url_parts)

            # Alternatively, if password is used as the webhook URL
            if conn.password:
                self.base_url = conn.password
                # Validate URL format
                parsed = urlparse(self.base_url)
                if not parsed.scheme or not parsed.netloc:
                    raise AirflowException(f"Invalid webhook URL in connection {self.lark_conn_id}")

        return self.session

    def send_message(
        self,
        message: str,
        title: Optional[str] = None,
        message_type: str = "text",
        at_user_ids: Optional[list] = None,
        at_all: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a message to Lark group via webhook.

        :param message: The message content
        :type message: str
        :param title: The title for rich text messages
        :type title: str
        :param message_type: The type of message (text, post, image)
        :type message_type: str
        :param at_user_ids: List of user IDs to @ mention
        :type at_user_ids: list
        :param at_all: Whether to @ all users
        :type at_all: bool
        :return: The response from the API
        :rtype: dict
        """
        self.get_conn()

        if not self.base_url:
            raise AirflowException("Webhook URL not configured properly")

        # Build the message payload based on type
        if message_type == "text":
            payload = self._build_text_message(message, at_user_ids, at_all)
        elif message_type == "post":
            payload = self._build_post_message(title, message, at_user_ids, at_all)
        elif message_type == "image":
            payload = self._build_image_message(message)
        else:
            raise AirflowException(f"Unsupported message type: {message_type}")

        # Send the request
        for attempt in range(self.retry_limit):
            try:
                response = self.session.post(
                    self.base_url,
                    json=payload,
                    timeout=self.timeout,
                    headers={
                        'Content-Type': 'application/json',
                    }
                )
                response.raise_for_status()

                result = response.json()
                if result.get('code') != 0:
                    raise AirflowException(
                        f"Lark API returned error: {result.get('msg', 'Unknown error')}"
                    )

                self.log.info("Message sent successfully to Lark")
                return result

            except Exception as e:
                self.log.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.retry_limit - 1:
                    raise AirflowException(f"Failed to send message to Lark after {self.retry_limit} attempts") from e

    def _build_text_message(
        self,
        text: str,
        at_user_ids: Optional[list] = None,
        at_all: bool = False
    ) -> Dict[str, Any]:
        """Build a text message payload."""
        # Add @ mentions to the text
        if at_all:
            text = f"<at user_id=\"all\">all</at> {text}"
        elif at_user_ids:
            for user_id in at_user_ids:
                text = f"<at user_id=\"{user_id}\">{user_id}</at> {text}"

        return {
            "msg_type": "text",
            "content": {
                "text": text
            }
        }

    def _build_post_message(
        self,
        title: str,
        content: str,
        at_user_ids: Optional[list] = None,
        at_all: bool = False
    ) -> Dict[str, Any]:
        """Build a post (rich text) message payload."""
        # Add @ mentions to the content
        if at_all:
            content = f"<at user_id=\"all\">all</at> {content}"
        elif at_user_ids:
            for user_id in at_user_ids:
                content = f"<at user_id=\"{user_id}\">{user_id}</at> {content}"

        return {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title or "",
                        "content": [
                            [{
                                "tag": "text",
                                "text": content
                            }]
                        ]
                    }
                }
            }
        }

    def _build_image_message(self, image_key: str) -> Dict[str, Any]:
        """Build an image message payload."""
        return {
            "msg_type": "image",
            "content": {
                "image_key": image_key
            }
        }

    def test_connection(self) -> Tuple[bool, str]:
        """Test the Lark webhook connection."""
        try:
            # Send a test message
            self.send_message("Test connection from Apache Airflow")
            return True, "Connection test successful"
        except Exception as e:
            return False, str(e)