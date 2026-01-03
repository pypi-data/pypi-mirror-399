_handlers = {}

def register_handler(domain: str, representation: str):
    def decorator(fn):
        _handlers[(domain, representation)] = fn
        return fn
    return decorator

def get_handler(domain: str, representation: str):
    try:
        return _handlers[(domain, representation)]
    except KeyError:
        raise ValueError(f"No handler registered for {(domain, representation)}")