import functools
import inspect


def call_user_features(base_func, method_name):
    @functools.wraps(base_func)
    def decorator(self, *args, **kwargs):
        ret_val = base_func(self, *args, **kwargs)

        try:
            user_func = self.features[method_name]

            user_func_args = inspect.getargspec(user_func)[0]
            if 'ls' in user_func_args:
                user_func(ls=self, *args, **kwargs)
            else:
                user_func(*args, **kwargs)
        except:
            pass

        return ret_val

    return decorator
