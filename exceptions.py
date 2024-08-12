class EmptyAccountException(Exception):
    """Exception raised for specific errors in your application."""
    def __init__(self, message="Account is empty. Probably, FBbot banned"):
        self.message = message
        super().__init__(self.message)