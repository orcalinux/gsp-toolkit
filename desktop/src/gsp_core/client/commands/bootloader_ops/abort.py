from gsp_core.events import publish
from gsp_core.protocol.commands import CMD_ABORT

class AbortMixin:
    def abort(self) -> None:
        """
        Abort the current session and discard partial state.
        """
        publish("status", "Aborting session")
        self._call(cmd=CMD_ABORT)
