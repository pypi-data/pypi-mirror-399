from cp_based_fair_maker.datasets.dataset import Dataset


class MulticlassLabelDataset(Dataset):
    """Class for a dataset with multi-class label."""

    def __init__(self, favorable_labels, unfavorable_labels, **kwargs):
        """
        Args:
        :param favorable_labels: Positive label values.
        :param unfavorable_labels: Negative label values.
        :param kwargs: Dataset arguments.
        """
        if not isinstance(favorable_labels, list) or not isinstance(unfavorable_labels, list):
            raise ValueError("favorable_labels and unfavorable_labels must be lists.")
        self.favorable_labels = favorable_labels
        self.unfavorable_labels = unfavorable_labels
        self.class_labels = list(set(self.favorable_labels + self.unfavorable_labels))

        self.df = kwargs['df']
        self.protected_attributes_names = kwargs['protected_attributes_names']
        self.label_names = kwargs['label_names']
        self.scores_names = kwargs['scores_names']

        super(MulticlassLabelDataset, self).__init__(**kwargs)

    def validate(self):
        """Validate that the dataset contains a multi-class label."""
        super().validate()

        # Check if the label column exists
        if len(self.label_names) != 1:
            raise ValueError("MulticlassLabelDataset only supports single-column labels.")

        label = self.label_names[0]
        unique_values = set(self.df[label].unique())

        # If class labels were provided, validate against them
        if self.class_labels is not None:
            if not unique_values.issubset(self.class_labels):
                raise ValueError(
                    f"Label column '{label}' contains unexpected values: {unique_values - self.class_labels}. Expected classes are {self.class_labels}.")
            if len(unique_values) > len(self.class_labels):
                raise ValueError(
                    f"Label column '{label}' contains {len(unique_values)} unique values, but {len(self.class_labels)} class labels were provided.")
        else:
            # If no class labels were provided, assume all unique labels in the dataset are valid
            self.class_labels = unique_values

        # Ensure that the favorable and unfavorable labels are disjoints
        if not set(self.favorable_labels).isdisjoint(set(self.unfavorable_labels)):
            raise ValueError("Favorable and unfavorable labels must be disjoint.")


    def summary(self):
        """Provide a summary of the multi-class labeled dataset."""
        summary = {
            'Number of samples': len(self.df),
            'Number of features': self.df.shape[1] - len(self.label_names) - len(self.scores_names),
            'Label distribution': self.df[self.label_names[0]].value_counts().to_dict(),
            'Protected attributes': self.protected_attributes_names,
            'Favorable labels': sorted(list(self.favorable_labels)),
            'Unfavorable labels': sorted(list(self.unfavorable_labels))
        }
        return summary
