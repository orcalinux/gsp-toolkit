from typing import Optional
from gsp_core.events import publish
from gsp_core.protocol.commands import CMD_ERASE_FLASH
from gsp_core.protocol.cra import Priority

class EraseMixin:
    def erase_flash(
        self,
        address: Optional[int] = None,
        length: Optional[int] = None,
        priority: Priority = Priority.NORMAL
    ) -> None:
        """
        Erase flash memory. If address+length given, erases that region;
        otherwise a full-chip erase.
        """
        publish("status", "Erasing flash")
        data = b""
        if address is not None and length is not None:
            data = address.to_bytes(4, "little") + length.to_bytes(4, "little")
        # self._call comes from the base client
        self._call(cmd=CMD_ERASE_FLASH, payload=data, priority=priority)
