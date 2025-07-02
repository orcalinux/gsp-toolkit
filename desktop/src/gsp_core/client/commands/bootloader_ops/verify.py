from gsp_core.events import publish
from gsp_core.protocol.commands import CMD_VERIFY_CHUNK

class VerifyMixin:
    def verify_chunk(self) -> None:
        """
        Request CRC check of the last written chunk.
        """
        publish("status", "Verifying chunk")
        self._call(cmd=CMD_VERIFY_CHUNK)
