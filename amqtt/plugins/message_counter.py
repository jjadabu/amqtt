import logging

from amqtt.plugins.base import BasePlugin
from amqtt.session import ApplicationMessage


class MessageCounterPlugin(BasePlugin):
    """Log and count messages on a specific topic."""

    def __init__(self, context):
        super().__init__(context)
        self.message_count = 0
        self.logger = logging.getLogger(__name__)

    async def on_broker_message_received(
        self, *, client_id: str, message: ApplicationMessage
    ) -> None:
        if message.topic == "brown/hello":
            self.message_count += 1
            self.logger.info(
                "Message #%s on %s from %s: %s",
                self.message_count,
                message.topic,
                client_id,
                message.data.decode("utf-8", errors="replace"),
            )


