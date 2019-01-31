
class SubnetNotFoundError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ImageNotFoundError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InvalidParameterTypeError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

