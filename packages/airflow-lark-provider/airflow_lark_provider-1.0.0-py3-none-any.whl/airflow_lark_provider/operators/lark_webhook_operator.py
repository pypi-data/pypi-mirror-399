from typing import Optional, Dict, Any, Sequence, Union

from airflow.models import BaseOperator
from airflow.utils.context import Context

from airflow_lark_provider.hooks.lark_webhook_hook import LarkWebhookHook


class LarkWebhookOperator(BaseOperator):
    """
    Send messages to Lark (Feishu) bot webhook.

    This operator sends messages to Lark groups using custom bot webhooks.
    The webhook URL is configured in Airflow connections.

    :param lark_conn_id: The connection ID for the Lark webhook
    :type lark_conn_id: str
    :param message: The message content to send
    :type message: str
    :param title: The title for rich text messages
    :type title: str
    :param message_type: The type of message (text, post, image)
    :type message_type: str
    :param at_user_ids: List of user IDs to @ mention
    :type at_user_ids: list
    :param at_all: Whether to @ all users
    :type at_all: bool
    :param timeout: The timeout for the webhook request
    :type timeout: int
    :param retry_limit: The number of retries for the webhook request
    :type retry_limit: int
    """

    template_fields: Sequence[str] = (
        'message',
        'title',
        'at_user_ids',
    )

    def __init__(
        self,
        lark_conn_id: str = 'lark_default',
        message: str = '',
        title: Optional[str] = None,
        message_type: str = 'text',
        at_user_ids: Optional[Union[list, str]] = None,
        at_all: bool = False,
        timeout: int = 30,
        retry_limit: int = 3,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.lark_conn_id = lark_conn_id
        self.message = message
        self.title = title
        self.message_type = message_type
        self.at_user_ids = at_user_ids
        self.at_all = at_all
        self.timeout = timeout
        self.retry_limit = retry_limit
        self.hook: Optional[LarkWebhookHook] = None

    def execute(self, context: Context) -> Any:
        """Execute the Lark webhook operation."""
        self.log.info(f"Sending Lark message via connection: {self.lark_conn_id}")

        # Ensure at_user_ids is a list
        if isinstance(self.at_user_ids, str):
            at_user_ids = [user.strip() for user in self.at_user_ids.split(',')]
        else:
            at_user_ids = self.at_user_ids

        # Create the hook and send the message
        self.hook = LarkWebhookHook(
            lark_conn_id=self.lark_conn_id,
            timeout=self.timeout,
            retry_limit=self.retry_limit,
        )

        result = self.hook.send_message(
            message=self.message,
            title=self.title,
            message_type=self.message_type,
            at_user_ids=at_user_ids,
            at_all=self.at_all,
        )

        self.log.info("Successfully sent Lark webhook message")
        return result


class LarkWebhookSentimentAnalysisOperator(BaseOperator):
    """
    Send sentiment analysis result to Lark webhook.

    This operator analyzes text and sends the result to Lark.
    """

    template_fields: Sequence[str] = (
        'text',
        'positive_threshold',
    )

    def __init__(
        self,
        text: str,
        lark_conn_id: str = 'lark_default',
        positive_threshold: float = 0.7,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.text = text
        self.lark_conn_id = lark_conn_id
        self.positive_threshold = positive_threshold
        self.hook: Optional[LarkWebhookHook] = None

    def execute(self, context: Context) -> Any:
        """Execute sentiment analysis and send to Lark."""
        # Simple sentiment analysis (placeholder)
        # In production, you might use libraries like TextBlob, VADER, or ML models
        positive_words = ['good', 'great', 'excellent', 'happy', 'success', 'completed', 'done', 'successfully']
        negative_words = ['bad', 'error', 'failed', 'issue', 'problem', 'warning', 'exception']

        text_lower = self.text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count + negative_count == 0:
            sentiment = 'neutral'
            score = 0.5
        else:
            score = positive_count / (positive_count + negative_count)
            sentiment = 'positive' if score >= self.positive_threshold else 'negative'

        # Build the message
        title = f"Sentiment Analysis Result - {sentiment.title()}"
        emoji = "😊" if sentiment == 'positive' else "😔" if sentiment == 'negative' else "😐"

        message = (
            f"**Text:** {self.text}\n\n"
            f"**Sentiment:** {sentiment} {emoji}\n"
            f"**Score:** {score:.2f}\n"
            f"**Analysis Time:** {context['ts']}\n"
            f"**Dag Run:** {context['dag'].dag_id} - {context['run_id']}"
        )

        # Send to Lark
        self.hook = LarkWebhookHook(
            lark_conn_id=self.lark_conn_id,
        )

        result = self.hook.send_message(
            message=message,
            title=title,
            message_type='post',
        )

        self.log.info(f"Sentiment analysis result sent to Lark: {sentiment}")
        return result