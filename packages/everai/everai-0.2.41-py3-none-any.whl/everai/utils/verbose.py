is_verbose = False


def verbose_print(*args, **kwargs):
    v_print = print if is_verbose else lambda *a, **kw: None
    v_print(*args, **kwargs)
