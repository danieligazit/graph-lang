import shortuuid


def unique_name():
    return f'u{shortuuid.uuid()[:12]}'
