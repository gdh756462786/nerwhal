from importlib import import_module


def load(backend):
    if backend == "re":
        mod = ".re_backend"
        cls = "ReBackend"
    elif backend == "flashtext":
        mod = ".flashtext_backend"
        cls = "FlashtextBackend"
    else:
        raise ValueError(f"Unknown backend type {backend}")

    backend_cls = getattr(import_module(mod, package="nerwhal.backends"), cls)
    return backend_cls
