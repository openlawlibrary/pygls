"""
It would be great to find the real underlying issue here, but without these
retries we get annoying flakey test errors. So it's preferable to hack this
fix to actually guarantee it doesn't generate false negatives in the test
suite.
"""

import os
import concurrent

RETRIES = 3


def retry_stalled_init_fix_hack():
    if "DISABLE_TIMEOUT" in os.environ:
        return lambda f: f

    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < RETRIES:
                try:
                    return func(*args, **kwargs)
                except concurrent.futures._base.TimeoutError:
                    print(
                        "\n\nRetrying timeouted test server init "
                        "%d of %d\n" % (attempt, RETRIES)
                    )
                    attempt += 1
            return func(*args, **kwargs)

        return newfn

    return decorator
