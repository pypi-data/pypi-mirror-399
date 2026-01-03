from abc import ABC, abstractmethod

from ortools.linear_solver import pywraplp

from cp_based_fair_maker.datasets import Dataset


class CPTransformable(ABC):
    """
    Abstract class for CPTransformable objects.
    """

    @abstractmethod
    def create_variables(self, model: pywraplp.Solver):
        """
        Get the variables expressions for the CPTransformable object.
        """
        raise NotImplementedError

    @abstractmethod
    def add_objective_function(self, model: pywraplp.Solver, variables):
        """
        Add the objective function expression for the CPTransformable object.
        """
        raise NotImplementedError

    @abstractmethod
    def estimate_objective_function(self, solver: pywraplp.Solver, variables):
        """
        Estimate the objective function value for the given variables.
        """
        raise NotImplementedError

    @abstractmethod
    def add_constraints(self, model: pywraplp.Solver, variables: list):
        """
        Add the constraints expressions for the CPTransformable object.
        """
        raise NotImplementedError

    @abstractmethod
    def estimate_constraints(self, model, variables):
        """
        Estimate the constraints values for the given variables.
        """
        raise NotImplementedError


class CPTransformer(ABC):
    """
    Class to perform preprocessing using the CP-based method.
    """

    def __init__(self, dataset: Dataset, coef, transformable: CPTransformable):
        """
        Initialize the CPTransformer with the dataset and transformable object.

        Args:
            dataset (Dataset): The dataset to be transformed.
            coef (float): Coefficient for the transformation.
            transformable (CPTransformable): The CPTransformable object. Generally, it is a subclass of DatasetMetric.
        """
        # self.model = cp_model.CpModel()
        self.model : pywraplp.Solver = pywraplp.Solver.CreateSolver('SCIP')
        if not self.model:
            raise RuntimeError("CP Solver not found.")
        self.dataset = dataset
        self.coef = coef
        self.transformable = transformable

    @abstractmethod
    def fit(self):
        """
        Fit the cp transformer to the data.
        """
        raise NotImplementedError

    @abstractmethod
    def transform(self):
        """
        Transform the data using the fitted cp transformer.
        """
        raise NotImplementedError

    def fit_transform(self):
        """
        Fit the cp transformer to the data and transform it.
        """
        return self.fit().transform()
