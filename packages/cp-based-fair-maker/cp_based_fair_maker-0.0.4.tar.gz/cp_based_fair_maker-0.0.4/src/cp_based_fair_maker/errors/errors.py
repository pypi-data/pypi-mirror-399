class CPFairMakerError(Exception):
    """Base exception for cp-based-fair-maker."""
    pass

class DatasetValidationError(CPFairMakerError):
    """Raised when dataset validation fails."""
    pass

class TransformationError(CPFairMakerError):
    """Raised when transformation fails."""
    pass

class GroupDefinitionError(CPFairMakerError):
    """Raised when group definition is invalid."""
    pass