import functools


def call_user_features(base_func, method_name):
    @functools.wraps(base_func)
    def decorator(self, *args, **kwargs):
        ret_val = base_func(self, *args, **kwargs)

        try:
            user_func = self._features[method_name]
            user_func(*args, **kwargs)
        except:
            pass

        return ret_val

    return decorator
