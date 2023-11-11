from jupyter_client import AsyncKernelClient
from jupyter_client.asynchronous.client import wrapped
from jupyter_client.client import reqrep


class EngeeKernelClient(AsyncKernelClient):
    def interrupt_(self):
        msg = self.session.msg("interrupt_request", {})
        self.control_channel.send(msg)
        return msg['header']['msg_id']

    interrupt = reqrep(wrapped, interrupt_, channel='control')
