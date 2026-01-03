def format_size(bytes: float, digits: int = 1):
    if bytes < 1000:
        return _format_size(int(bytes), 0, "B")

    kilo = bytes / 1000
    if kilo < 1000:
        return _format_size(kilo, digits, "kB")

    mega = kilo / 1000
    if mega < 1000:
        return _format_size(mega, digits, "MB")

    return _format_size(mega / 1000, digits, "GB")


def _format_size(value: float, digits: int, unit: str):
    if digits > 0:
        return "{{:.{}f}} {}".format(digits, unit).format(value)
    else:
        return "{{:d}} {}".format(unit).format(value)
