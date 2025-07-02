from gsp_core.events import publish
from gsp_core.protocol.commands import CMD_RESET_AND_RUN

class ResetMixin:
    def reset_and_run(self) -> None:
        """
        Exit bootloader and run the main application.
        """
        publish("status", "Resetting and running")
        self._call(cmd=CMD_RESET_AND_RUN)
