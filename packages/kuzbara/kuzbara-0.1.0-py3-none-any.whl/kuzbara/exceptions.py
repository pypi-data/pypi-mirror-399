class KuzbaraError(Exception):
    """Base exception for the library."""
    pass

class WarnCondition(KuzbaraError):
    """
    Raise this in a probe check to signal a WARN status 
    instead of a FAIL.
    """
    pass