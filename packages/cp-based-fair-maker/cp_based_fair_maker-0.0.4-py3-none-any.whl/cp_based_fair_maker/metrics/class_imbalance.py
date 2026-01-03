from cp_based_fair_maker.metrics.dataset_metric import DatasetMetric
from cp_based_fair_maker.utils.operations import difference
from cp_based_fair_maker.utils.range import Range


class ClassImbalance(DatasetMetric):
    """Class for computing class imbalance metrics for datasets.
        CI = (N_u - N_p) / N
        where:
            N_u = number of unprivileged positive instances
            N_p = number of privileged positive instances
            N = total number of instances (N_u + N_p)
    """

    def __init__(self, dataset, privileged_groups=None, unprivileged_groups=None):
        super(ClassImbalance, self).__init__(dataset, privileged_groups, unprivileged_groups)

    def compute(self, **kwargs):
        """
        Calculate the class imbalance.
        CI = (N_u - N_p) / N
        where:
            N_u = number of unprivileged positive instances
            N_p = number of privileged positive instances
            N = total number of instances (N_u + N_p)

        Returns:
            float: Class imbalance (unprivileged positive rate / privileged positive rate).
        """
        diff = difference(self.num_instances, self.privileged_groups, self.unprivileged_groups)
        return diff / self.dataset.instance_weights.sum()

    def value_range(self):
        """
        Return the value range of the class imbalance metric.

        Returns:
            Range: Value range of the class imbalance metric.
        """
        return Range(-1, 1, inclusive=True)

    def ideal(self):
        """
        Return the ideal value of the class imbalance metric.

        Returns:
            float: Ideal value of the class imbalance metric.
        """
        return 0.0

    def use_cases(self):
        return ['classification', 'regression']
