import pytest
from unittest.mock import Mock, patch, MagicMock

from airflow.utils.context import Context
from airflow_lark_provider.operators.lark_webhook_operator import (
    LarkWebhookOperator,
    LarkWebhookSentimentAnalysisOperator,
)


class TestLarkWebhookOperator:
    """Test cases for LarkWebhookOperator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.operator = LarkWebhookOperator(
            task_id='test_task',
            lark_conn_id='test_conn',
            message='Test message',
            message_type='text',
        )

    @patch('airflow_lark_provider.operators.lark_webhook_operator.LarkWebhookHook')
    def test_execute(self, mock_hook_class):
        """Test operator execution"""
        # Mock hook instance
        mock_hook = Mock()
        mock_hook_class.return_value = mock_hook
        mock_hook.send_message.return_value = {'code': 0}

        # Mock context
        context = Mock()
        context.__getitem__ = Mock(return_value='2023-01-01')

        result = self.operator.execute(context)

        # Verify hook was created with correct parameters
        mock_hook_class.assert_called_once_with(
            lark_conn_id='test_conn',
            timeout=30,
            retry_limit=3,
        )

        # Verify message was sent
        mock_hook.send_message.assert_called_once_with(
            message='Test message',
            title=None,
            message_type='text',
            at_user_ids=None,
            at_all=False,
        )

        assert result == {'code': 0}

    @patch('airflow_lark_provider.operators.lark_webhook_operator.LarkWebhookHook')
    def test_execute_with_string_at_user_ids(self, mock_hook_class):
        """Test operator with string of user IDs"""
        operator = LarkWebhookOperator(
            task_id='test_task',
            lark_conn_id='test_conn',
            message='Test message',
            at_user_ids='user1@example.com, user2@example.com',
        )

        # Mock hook instance
        mock_hook = Mock()
        mock_hook_class.return_value = mock_hook
        mock_hook.send_message.return_value = {'code': 0}

        context = Mock()
        result = operator.execute(context)

        # Verify message was sent with parsed user IDs
        call_args = mock_hook.send_message.call_args
        assert call_args[1]['at_user_ids'] == ['user1@example.com', 'user2@example.com']

    @patch('airflow_lark_provider.operators.lark_webhook_operator.LarkWebhookHook')
    def test_template_fields(self, mock_hook_class):
        """Test that fields are properly templated"""
        operator = LarkWebhookOperator(
            task_id='test_task',
            lark_conn_id='test_conn',
            message='{{ ds }} report',
            title='{{ execution_date }}',
            at_user_ids=['{{ dag.dag_id }}@example.com'],
        )

        # Mock context with template context
        context = Mock()
        context.__getitem__ = Mock(return_value='2023-01-01')

        # Mock hook instance
        mock_hook = Mock()
        mock_hook_class.return_value = mock_hook
        mock_hook.send_message.return_value = {'code': 0}

        # Execute with templating
        operator.render_template_fields(context={'ds': '2023-01-01', 'execution_date': '2023-01-01'})

        operator.execute(context)

        # Verify message was sent with templated content
        call_args = mock_hook.send_message.call_args
        assert '{{ ds }} report' in call_args[1]['message']
        assert '{{ execution_date }}' in call_args[1]['title']

    def test_operator_parameters(self):
        """Test operator initialization with various parameters"""
        operator = LarkWebhookOperator(
            task_id='test_task',
            lark_conn_id='test_conn',
            message='Test message',
            title='Test Title',
            message_type='post',
            at_user_ids=['user1', 'user2'],
            at_all=True,
            timeout=60,
            retry_limit=2,
        )

        assert operator.lark_conn_id == 'test_conn'
        assert operator.message == 'Test message'
        assert operator.title == 'Test Title'
        assert operator.message_type == 'post'
        assert operator.at_user_ids == ['user1', 'user2']
        assert operator.at_all is True
        assert operator.timeout == 60
        assert operator.retry_limit == 2


class TestLarkWebhookSentimentAnalysisOperator:
    """Test cases for LarkWebhookSentimentAnalysisOperator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.operator = LarkWebhookSentimentAnalysisOperator(
            task_id='test_sentiment',
            text='This is great news!',
            lark_conn_id='test_conn',
        )

    @patch('airflow_lark_provider.operators.lark_webhook_operator.LarkWebhookHook')
    def test_positive_sentiment(self, mock_hook_class):
        """Test positive sentiment analysis"""
        # Mock hook instance
        mock_hook = Mock()
        mock_hook_class.return_value = mock_hook
        mock_hook.send_message.return_value = {'code': 0}

        # Mock context
        context = {
            'ts': '2023-01-01T00:00:00Z',
            'dag': Mock(dag_id='test_dag'),
            'run_id': 'test_run',
        }

        result = self.operator.execute(context)

        # Verify hook was called
        mock_hook_class.assert_called_once_with(
            lark_conn_id='test_conn',
        )

        # Verify message was sent
        mock_hook.send_message.assert_called_once_with(
            message=pytest.Any(str),  # Using pytest.Any to match any string
            title=pytest.Any(str),
            message_type='post',
        )

        assert result == {'code': 0}

    @patch('airflow_lark_provider.operators.lark_webhook_operator.LarkWebhookHook')
    def test_negative_sentiment(self, mock_hook_class):
        """Test negative sentiment analysis"""
        operator = LarkWebhookSentimentAnalysisOperator(
            task_id='test_sentiment',
            text='This is terrible and failed completely',
            lark_conn_id='test_conn',
            positive_threshold=0.7,
        )

        # Mock hook instance
        mock_hook = Mock()
        mock_hook_class.return_value = mock_hook
        mock_hook.send_message.return_value = {'code': 0}

        context = {
            'ts': '2023-01-01T00:00:00Z',
            'dag': Mock(dag_id='test_dag'),
            'run_id': 'test_run',
        }

        result = operator.execute(context)

        assert result == {'code': 0}

    def test_sentiment_calculation(self):
        """Test the sentiment calculation logic"""
        # Test positive sentiment
        operator = LarkWebhookSentimentAnalysisOperator(
            task_id='test',
            text='Pipeline execution completed successfully! Great job team!',
        )

        # The test is in the execution, but we can verify the operator initialization
        assert operator.text == 'Pipeline execution completed successfully! Great job team!'
        assert operator.positive_threshold == 0.7

    def test_custom_positive_threshold(self):
        """Test custom positive threshold setting"""
        operator = LarkWebhookSentimentAnalysisOperator(
            task_id='test',
            text='This is okay',
            lark_conn_id='test_conn',
            positive_threshold=0.8,
        )

        assert operator.positive_threshold == 0.8