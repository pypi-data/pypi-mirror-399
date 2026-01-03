from abc import ABC, abstractmethod


class RawDataset(ABC):
    """Abstract class for datasets."""

    @abstractmethod
    def __init__(self, **kwargs):
        self.validate()

    def validate(self):
        """Check errors and validate types of dataset."""
        pass

    def summary(self):
        """Print summary of dataset."""
        raise NotImplementedError

    @abstractmethod
    def save(self, output_file):
        """Save dataset in file."""
        raise NotImplementedError
