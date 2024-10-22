class DoNotImplementedException(Exception):
    def __init__(self):
        super().__init__('Method do not implemented')
