class DataConflictException(Exception):
    def __init__(self, error_msg):
        super().__init__(self)
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg
