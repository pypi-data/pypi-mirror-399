def difference(metric_func, privileged_groups, unprivileged_groups):
    """
    Calculate the difference in a metric between unprivileged and privileged groups.

    Args:
        metric_func (function): Function that calculates a metric.
        privileged_groups (list of dict): Definitions of privileged groups.
        unprivileged_groups (list of dict): Definitions of unprivileged groups.

    Returns:
        float: Difference in the metric between unprivileged and privileged groups.
    """
    metric_privileged = metric_func(group=privileged_groups)
    metric_unprivileged = metric_func(group=unprivileged_groups)
    return metric_unprivileged - metric_privileged


def ratio(metric_func, privileged_groups, unprivileged_groups):
    """
    Calculate the ratio of a metric between unprivileged and privileged groups.

    Args:
        metric_func (function): Function that calculates a metric.
        privileged_groups (list of dict): Definitions of privileged groups.
        unprivileged_groups (list of dict): Definitions of unprivileged groups.

    Returns:
        float: Ratio of the metric between unprivileged and privileged groups.
    """
    metric_privileged = metric_func(group=privileged_groups)
    metric_unprivileged = metric_func(group=unprivileged_groups)
    return metric_unprivileged / metric_privileged if metric_privileged != 0 else float('inf')
