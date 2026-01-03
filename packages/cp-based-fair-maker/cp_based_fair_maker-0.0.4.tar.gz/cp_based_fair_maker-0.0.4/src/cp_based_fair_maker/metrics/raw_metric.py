from abc import ABC, abstractmethod

from cp_based_fair_maker.datasets.raw_dataset import RawDataset


class RawMetric(ABC):
    """Abstract class for metrics."""

    @abstractmethod
    def __init__(self, dataset):
        if isinstance(dataset, RawDataset):
            self.dataset = dataset
        else:
            raise ValueError("dataset must be an instance of RawDataset")

    @abstractmethod
    def compute(self, group=None):
        """Compute the metric."""
        raise NotImplementedError

    @abstractmethod
    def difference(self):
        """Compute the difference of the metric."""
        raise NotImplementedError

    @abstractmethod
    def ratio(self):
        """Compute the ratio of the metric."""
        raise NotImplementedError

    @abstractmethod
    def value_range(self):
        """Return the value range of the metric."""
        raise NotImplementedError

    @abstractmethod
    def ideal(self):
        """Return the ideal value of the metric."""
        raise NotImplementedError

    @abstractmethod
    def use_cases(self):
        """Return the use cases of the metric."""
        raise NotImplementedError
