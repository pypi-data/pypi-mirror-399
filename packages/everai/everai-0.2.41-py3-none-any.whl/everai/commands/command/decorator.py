import functools
import everai.utils.verbose as vb


def command_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if vb.is_verbose:
            return func(*args, **kwargs)
        else:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(e)
            except KeyboardInterrupt as e:
                print('KeyboardInterrupt')

    return wrapper
