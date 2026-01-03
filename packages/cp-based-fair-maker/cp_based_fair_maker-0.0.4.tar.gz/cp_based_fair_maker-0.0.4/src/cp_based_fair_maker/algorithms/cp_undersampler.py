from ortools.sat.python import cp_model
from ortools.linear_solver import pywraplp

from cp_based_fair_maker.algorithms.cp_transformer import CPTransformer, CPTransformable
from cp_based_fair_maker.datasets import Dataset


# TODO 31/05/2025 Add support for not-to-be-removed instances
class CPUndersampler(CPTransformer):
    """
    Class to perform undersampling using the CP-based method.
    """

    def __init__(self, dataset: Dataset, coef, transformable: CPTransformable):
        """
        Initialize the CPTransformer with the dataset and transformable object.

        Args:
            dataset (Dataset): The dataset to be transformed.
            coef (float): Coefficient for the transformation.
            transformable (CPTransformable): The CPTransformable object. Generally, it is a subclass of DatasetMetric.
        """
        super().__init__(dataset, coef, transformable)
        self.selected = None
        self.verbose = False

        # Check if the coefficient is valid
        bound = int(self.dataset.instance_weights.sum() * self.coef)
        if bound < 1:
            raise ValueError("The undersampling bound must be greater than 0.")
        if bound > self.dataset.instance_weights.sum():
            raise ValueError("The undersampling bound must be less than the weighted size of the dataset.")
        self.bound = bound

    def fit(self):
        """
        Fit the undersampler to the data.
        """
        # Create the variables for the model
        self.model, variables = self.transformable.create_variables(self.model)

        # Add the objective function to the model
        self.model = self.transformable.add_objective_function(self.model, variables)

        # Add object specific constraints to the model
        self.model = self.transformable.add_constraints(self.model, variables)

        # TODO 31/05/2025 Move into add_constraints method
        # Add constraint on minimum output dataset size
        self.model.Add(sum(w * var for w, var in zip(self.dataset.instance_weights, variables))
                       >= self.bound)  # Assuming variables are 0-1

        status = self.model.Solve()

        if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
            if self.verbose:
                print(f"Solution {'(optimal)' if status == pywraplp.Solver.OPTIMAL else '(feasible)'} found. "
                      f"FS value: {self.transformable.estimate_objective_function(self.model, variables)}. Status = {status}")
            self.selected = [var.solution_value() for var in variables]
            # self.selected = [self.model.BooleanValue(var) for var in variables]
        else:
            raise RuntimeError("No solution found for the undersampling problem.")

        return self

    def transform(self):
        """
        Transform the data using the fitted undersampler.

        Returns:
            pd.DataFrame: The undersampled dataset with same indexes as in dataset.df.
        """
        if self.selected is None:
            raise ValueError("The undersampler has not been fitted yet. Call fit() before transform(). "
                             "You can also use fit_transform() to fit and transform in one step.")

        # Create a new dataset with the selected instances
        selected_indices = [i for i, selected in enumerate(self.selected) if selected]
        return self.dataset.df.iloc[selected_indices].copy()
