from ortools.linear_solver import pywraplp

from cp_based_fair_maker.algorithms.cp_transformer import CPTransformable
from cp_based_fair_maker.metrics import FairScore


class FairScoreCPTransformable(FairScore, CPTransformable):
    """
    Class for computing fairness scores for datasets, inheriting from both FairScore and CPTransformable.
    """

    def __init__(self, dataset, protected_attributes=None):
        """
        Initialize the FairScoreCPTransformable with the dataset and protected attributes.

        Args:
            dataset (Dataset): The dataset to be transformed.
            protected_attributes (list): List of protected attributes.
        """
        FairScore.__init__(self, dataset, protected_attributes)
        CPTransformable.__init__(self)
        self.intermediate_variables = {}

    def create_variables(self, model: pywraplp.Solver):
        """
        Create the variables for the model.

        Args:
            model: The model to create variables for.

        Returns:
            The model with the created variables, and
            a list of boolean variables representing the dataset instances.
        """
        variables = [model.BoolVar(f"var_{i}") for i in range(len(self.dataset.df))]
        return model, variables

    def add_objective_function(self, model: pywraplp.Solver, variables):
        # Size of the dataset (represented by the sum of selected instance weights)
        t_value = sum(w * var for w, var in zip(self.dataset.instance_weights, variables))
        # Initial size of the dataset (represented by the sum of all instance weights)
        initial_size = int(self.dataset.instance_weights.sum())
        fs_terms = []

        # Iterate over all the groups of protected attributes
        for c_idx, columns in enumerate(self.protected_attributes):
            if isinstance(columns, str):
                columns = [columns]
            # Infer the groups
            combinations = self.dataset.df[columns].drop_duplicates().dropna().to_dict(orient='records')

            # Number of distinct groups
            v_value = len(combinations)

            # Iterate over all combinations of the columns
            for idx, combination in enumerate(combinations):
                # Get the group size (number of selected instances in the group)
                mask = self.build_groups_mask([combination])
                weights = self.dataset.instance_weights * mask.astype(int)

                # Simplify abs((group_size / t_value) - (1 / v_value)) to ((group_size * v_value) - t_value),
                #   ignoring the denominator to avoid divisions
                # Defining intermediate z_{group} variable to represent the absolute value
                z_group = model.IntVar(0, initial_size * v_value, f"z_group_{c_idx}_{idx}")

                # Add the constraint for the absolute value
                model = self._add_abs_equality(model, z_group,
                                       ((sum(w * var for w, var in zip(weights, variables)) * v_value) - t_value))

                # model.AddAbsEquality(z_group,
                #                      ((sum(w * var for w, var in zip(weights, variables)) * v_value) - t_value))

                # Store the intermediate variable for later use
                self.intermediate_variables[f"z_group_{c_idx}_{idx}"] = z_group
                # Add the z_{group} variable to the list of terms
                fs_terms.append(z_group)

        # Set the objective function to minimize the fairness score
        fair_score_expr = sum(fs_terms)
        # print(f"Fairness score expression: {fair_score_expr}")
        model.Minimize(fair_score_expr)

        return model

    def estimate_objective_function(self, solver, variables):
        # Size of the dataset (represented by the sum of selected instance weights)
        t_value = sum(w * solver.BooleanValue(var) for w, var in zip(self.dataset.instance_weights, variables))
        fs_terms = []
        fs_terms_ = []

        dataset_df = self.dataset.df
        selected = [solver.BooleanValue(var) for var in variables]
        selected_indices = [i for i, selected in enumerate(selected) if selected]
        dataset_df = dataset_df.iloc[selected_indices]

        # Iterate over all the groups of protected attributes
        for c_idx, columns in enumerate(self.protected_attributes):
            if isinstance(columns, str):
                columns = [columns]
            # Infer the groups
            # combinations = self.dataset.df[columns].drop_duplicates().dropna().to_dict(orient='records')
            combinations = dataset_df[columns].drop_duplicates().dropna().to_dict(orient='records')

            # Number of distinct groups
            v_value = len(combinations)

            terms = []
            # Iterate over all combinations of the columns
            for idx, combination in enumerate(combinations):
                z_group = self.intermediate_variables[f'z_group_{c_idx}_{idx}']
                z_group_value = solver.Value(z_group)
                z_group_value = z_group_value / (t_value * v_value)
                terms.append(z_group_value)

            fs_terms.append(sum(terms) / len(self.protected_attributes))
            fs_terms_.append((columns, sum(terms) / len(self.protected_attributes)))

        # Set the objective function to minimize the fairness score
        fair_score = sum(fs_terms)
        return fair_score

    def add_constraints(self, model, variables):
        """
        Add the constraints to the model.
        """
        # TODO 09/06/2025 Compare the two following approaches

        # 1. The min selected lines for each sensitive attribute is >= max(len(protected_groups)): well implemented?
        # It seems incorrect, as it does not guarantee that each group is represented at least once.
        # most_represented_group_length = 0
        # for c_idx, columns in enumerate(self.protected_attributes):
        #     if isinstance(columns, str):
        #         columns = [columns]
        #     # Infer the groups
        #     combinations = self.dataset.df[columns].drop_duplicates().dropna().to_dict(orient='records')
        #     for idx, combination in enumerate(combinations):
        #         mask = self.build_groups_mask([combination])
        #         weights = self.dataset.instance_weights * mask.astype(int)
        #         most_represented_group_length = max(most_represented_group_length, sum(weights))
        #
        # int_weights = [int(w) for w in self.dataset.instance_weights]
        #
        # model.Add(cp_model.LinearExpr.WeightedSum(variables, int_weights)
        #           >= int(most_represented_group_length))

        # 2. Each protected group should be represented at least once
        for c_idx, columns in enumerate(self.protected_attributes):
            if isinstance(columns, str):
                columns = [columns]
            # Infer the groups
            combinations = self.dataset.df[columns].drop_duplicates().dropna().to_dict(orient='records')

            # Iterate over all combinations of the columns
            for idx, combination in enumerate(combinations):
                # Get the group size (number of selected instances in the group)
                mask = self.build_groups_mask([combination])
                weights = self.dataset.instance_weights * mask.astype(int)

                # Add the constraint that the group size must be at least 1
                model.Add(sum(w * var for w, var in zip(weights, variables)) >= 1)

        return model

    def estimate_constraints(self, model, variables):
        return model

    def _add_abs_equality(self, solver, x, z):
        """Add the constraint x = |z| to the solver."""
        solver.Add(x >= z)
        solver.Add(x >= -z)
        return solver