# src/gsp_core/client/commands/messaging/message.py

from gsp_core.events import publish
from gsp_core.protocol.commands import CMD_SEND_MESSAGE
from gsp_core.protocol.cra import Priority

class MessageMixin:
    def send_message(
        self,
        data: bytes,
        priority: Priority = Priority.NORMAL
    ) -> None:
        """
        Send an arbitrary message blob to the board.
        """
        publish("status", f"Sending message ({len(data)} bytes)")
        self._call(cmd=CMD_SEND_MESSAGE, payload=data, priority=priority)
