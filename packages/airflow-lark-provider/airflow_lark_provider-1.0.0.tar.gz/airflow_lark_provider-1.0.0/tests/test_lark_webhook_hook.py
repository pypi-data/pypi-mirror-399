import pytest
from unittest.mock import Mock, patch
import requests

from airflow.exceptions import AirflowException
from airflow_lark_provider.hooks.lark_webhook_hook import LarkWebhookHook


class TestLarkWebhookHook:
    """Test cases for LarkWebhookHook"""

    def setup_method(self):
        """Set up test fixtures"""
        self.hook = LarkWebhookHook(lark_conn_id='test_lark')

    @patch('airflow.hooks.base.BaseHook.get_connection')
    def test_get_conn_with_password_url(self, mock_get_connection):
        """Test connection configuration with password as webhook URL"""
        mock_conn = Mock()
        mock_conn.password = 'https://open.larksuite.com/open-apis/bot/v2/hook/abc123'
        mock_get_connection.return_value = mock_conn

        session = self.hook.get_conn()
        assert self.hook.base_url == 'https://open.larksuite.com/open-apis/bot/v2/hook/abc123'

    @patch('airflow.hooks.base.BaseHook.get_connection')
    def test_get_conn_with_host_schema(self, mock_get_connection):
        """Test connection configuration with host and schema"""
        mock_conn = Mock()
        mock_conn.password = None
        mock_conn.host = 'open.larksuite.com/open-apis/bot/v2/hook/abc123'
        mock_conn.schema = 'https'
        mock_conn.extra_dejson = {}
        mock_get_connection.return_value = mock_conn

        session = self.hook.get_conn()
        assert self.hook.base_url == 'https://open.larksuite.com/open-apis/bot/v2/hook/abc123'

    @patch('airflow.hooks.base.BaseHook.get_connection')
    def test_constructor_with_timeout_and_retry(self, mock_get_connection):
        """Test hook initialization with custom timeout and retry"""
        hook = LarkWebhookHook(
            lark_conn_id='test_lark',
            timeout=60,
            retry_limit=5
        )
        assert hook.timeout == 60
        assert hook.retry_limit == 5

    @patch('airflow.hooks.base.BaseHook.get_connection')
    @patch('requests.Session.post')
    def test_send_text_message(self, mock_post, mock_get_connection):
        """Test sending text message"""
        mock_conn = Mock()
        mock_conn.password = 'https://open.larksuite.com/open-apis/bot/v2/hook/abc123'
        mock_get_connection.return_value = mock_conn

        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {'code': 0, 'msg': 'success'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.hook.send_message(
            message='Test message',
            message_type='text'
        )

        assert result['code'] == 0
        mock_post.assert_called_once()

        # Verify the payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['msg_type'] == 'text'
        assert payload['content']['text'] == 'Test message'

    @patch('airflow.hooks.base.BaseHook.get_connection')
    @patch('requests.Session.post')
    def test_send_post_message(self, mock_post, mock_get_connection):
        """Test sending rich text (post) message"""
        mock_conn = Mock()
        mock_conn.password = 'https://open.larksuite.com/open-apis/bot/v2/hook/abc123'
        mock_get_connection.return_value = mock_conn

        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {'code': 0, 'msg': 'success'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.hook.send_message(
            message='Rich text content',
            title='Test Title',
            message_type='post'
        )

        assert result['code'] == 0
        mock_post.assert_called_once()

        # Verify the payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert payload['msg_type'] == 'post'
        assert payload['content']['post']['zh_cn']['title'] == 'Test Title'

    @patch('airflow.hooks.base.BaseHook.get_connection')
    @patch('requests.Session.post')
    def test_send_with_at_users(self, mock_post, mock_get_connection):
        """Test sending message with @ mentions"""
        mock_conn = Mock()
        mock_conn.password = 'https://open.larksuite.com/open-apis/bot/v2/hook/abc123'
        mock_get_connection.return_value = mock_conn

        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {'code': 0}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.hook.send_message(
            message='Urgent message',
            message_type='text',
            at_user_ids=['user1@example.com', 'user2@example.com']
        )

        assert result['code'] == 0

        # Verify mention is in message
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert '<at user_id="user1@example.com">' in payload['content']['text']
        assert '<at user_id="user2@example.com">' in payload['content']['text']

    @patch('airflow.hooks.base.BaseHook.get_connection')
    @patch('requests.Session.post')
    def test_send_with_at_all(self, mock_post, mock_get_connection):
        """Test sending message with @ all"""
        mock_conn = Mock()
        mock_conn.password = 'https://open.larksuite.com/open-apis/bot/v2/hook/abc123'
        mock_get_connection.return_value = mock_conn

        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {'code': 0}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = self.hook.send_message(
            message='Announcement',
            message_type='text',
            at_all=True
        )

        assert result['code'] == 0

        # Verify mention is in message
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert '<at user_id="all">all</at>' in payload['content']['text']

    @patch('airflow.hooks.base.BaseHook.get_connection')
    @patch('requests.Session.post')
    def test_retry_on_failure(self, mock_post, mock_get_connection):
        """Test retry mechanism on failure"""
        mock_conn = Mock()
        mock_conn.password = 'https://open.larksuite.com/open-apis/bot/v2/hook/abc123'
        mock_get_connection.return_value = mock_conn

        # Mock first failure, then success
        mock_response_fail = Mock()
        mock_response_fail.raise_for_status.side_effect = requests.HTTPError('500')

        mock_response_success = Mock()
        mock_response_success.json.return_value = {'code': 0}
        mock_response_success.raise_for_status.return_value = None

        mock_post.side_effect = [mock_response_fail, mock_response_success]

        result = self.hook.send_message(
            message='Test retry',
            message_type='text'
        )

        assert result['code'] == 0
        assert mock_post.call_count == 2  # Retried once

    @patch('airflow.hooks.base.BaseHook.get_connection')
    @patch('requests.Session.post')
    def test_lark_api_error(self, mock_post, mock_get_connection):
        """Test handling of Lark API error response"""
        mock_conn = Mock()
        mock_conn.password = 'https://open.larksuite.com/open-apis/bot/v2/hook/abc123'
        mock_get_connection.return_value = mock_conn

        # Mock Lark API error
        mock_response = Mock()
        mock_response.json.return_value = {'code': 1, 'msg': 'invalid webhook'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        with pytest.raises(AirflowException) as excinfo:
            self.hook.send_message(
                message='Test',
                message_type='text'
            )

        assert 'invalid webhook' in str(excinfo.value)

    @patch('airflow.hooks.base.BaseHook.get_connection')
    def test_invalid_connection(self, mock_get_connection):
        """Test error handling for invalid connection"""
        mock_conn = Mock()
        mock_conn.password = 'invalid-url'
        mock_get_connection.return_value = mock_conn

        with pytest.raises(AirflowException) as excinfo:
            self.hook.get_conn()

        assert 'Invalid webhook URL' in str(excinfo.value)

    @patch('airflow.hooks.base.BaseHook.get_connection')
    @patch('requests.Session.post')
    def test_test_connection_success(self, mock_post, mock_get_connection):
        """Test connection test function"""
        mock_conn = Mock()
        mock_conn.password = 'https://open.larksuite.com/open-apis/bot/v2/hook/abc123'
        mock_get_connection.return_value = mock_conn

        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {'code': 0}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        success, message = self.hook.test_connection()

        assert success is True
        assert 'test successful' in message

    @patch('airflow.hooks.base.BaseHook.get_connection')
    @patch('requests.Session.post')
    def test_test_connection_failure(self, mock_post, mock_get_connection):
        """Test connection test function on failure"""
        mock_conn = Mock()
        mock_conn.password = 'https://open.larksuite.com/open-apis/bot/v2/hook/abc123'
        mock_get_connection.return_value = mock_conn

        # Mock failed response
        mock_response = Mock()
        mock_response.json.return_value = {'code': 1, 'msg': 'invalid webhook'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        success, message = self.hook.test_connection()

        assert success is False
        assert 'invalid webhook' in message

    @patch('airflow.hooks.base.BaseHook.get_connection')
    def test_unsupported_message_type(self, mock_get_connection):
        """Test error for unsupported message type"""
        mock_conn = Mock()
        mock_conn.password = 'https://open.larksuite.com/open-apis/bot/v2/hook/abc123'
        mock_get_connection.return_value = mock_conn

        with pytest.raises(AirflowException) as excinfo:
            self.hook.send_message(
                message='Test',
                message_type='video'
            )

        assert 'Unsupported message type' in str(excinfo.value)

    @patch('airflow.hooks.base.BaseHook.get_connection')
    def test_image_message(self, mock_get_connection):
        """Test image message building"""
        mock_conn = Mock()
        mock_conn.password = 'https://open.larksuite.com/open-apis/bot/v2/hook/abc123'
        mock_get_connection.return_value = mock_conn

        payload = self.hook._build_image_message('img_123')

        assert payload['msg_type'] == 'image'
        assert payload['content']['image_key'] == 'img_123'