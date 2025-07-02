from gsp_core.client.base import BaseGSPClient, GSPTimeout
from gsp_core.client.commands.bootloader_ops.erase import EraseMixin
from gsp_core.client.commands.bootloader_ops.write import WriteMixin
from gsp_core.client.commands.bootloader_ops.verify import VerifyMixin
from gsp_core.client.commands.bootloader_ops.reset import ResetMixin
from gsp_core.client.commands.bootloader_ops.abort import AbortMixin
from gsp_core.client.commands.messaging.message    import MessageMixin

class GSPClient(BaseGSPClient,
                EraseMixin,
                WriteMixin,
                VerifyMixin,
                ResetMixin,
                AbortMixin,
                MessageMixin):
    """
    High-level GSP client composed of:
     - BaseGSPClient: transport, framing, retry logic
     - Mixins: one file per command category
    """
    pass
