class SDKValidationException(Exception):
    """Custom exception raised when SDK validation fails"""
    
    def __init__(self, message="SDK could not be validated"):
        self.message = message
        super().__init__(self.message)
    
class JourneyException(Exception):
    """Custom exception raised when SDK validation fails"""
    
    def __init__(self, message="SDK could not be validated"):
        self.message = message
        super().__init__(self.message)