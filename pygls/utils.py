import asyncio

import psutil


async def process_watcher(pid, on_process_terminated, delay=5):
    """Periodically checks if the given pid exists.

    - pid: Process id to check
    - on_process_terminated: Function without arguments which is called if process is
                             not alive anymore
    - delay: Delay in seconds
    """
    while True:
        if not psutil.pid_exists(pid):
            return on_process_terminated()
        await asyncio.sleep(delay)
