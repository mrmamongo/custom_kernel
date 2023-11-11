from jupyter_client import (BlockingKernelClient)

from src.presentation.kernel_listener.listener import KernelListener


def setup_kernel_listener(kernel_client: BlockingKernelClient) -> KernelListener:
    listener = KernelListener(kernel_client=kernel_client)

    return listener
