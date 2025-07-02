from gsp_core.events import publish
from gsp_core.protocol.commands import CMD_WRITE_CHUNK
from gsp_core.protocol.cra import Priority

class WriteMixin:
    def write_chunk(
        self,
        data: bytes,
        priority: Priority = Priority.NORMAL
    ) -> None:
        """
        Send one 0–256 byte data chunk to the target.
        """
        publish("progress", len(data))
        self._call(cmd=CMD_WRITE_CHUNK, payload=data, priority=priority)
