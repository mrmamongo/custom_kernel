from jupyter_client import BlockingKernelClient, AsyncKernelClient

from src.presentation.kernel_listener.handlers import control_handler, IopubHandler, stdin_handler, shell_handler
from src.presentation.kernel_listener.listener import KernelListener, SocketType


async def setup_kernel_listener(kernel_client: AsyncKernelClient) -> KernelListener:
    kernel_client.start_channels()
    await kernel_client.wait_for_ready()
    listener = KernelListener(kernel_client)

    listener.register_handler(SocketType.iopub_channel, IopubHandler)
    listener.register_handler(SocketType.stdin_channel, IopubHandler)
    listener.register_handler(SocketType.shell_channel, shell_handler)
    listener.register_handler(SocketType.control_channel, control_handler)

    return listener
