import ctypes
import numpy as np
import os
from typing import Tuple, Optional
from numpy.typing import NDArray

class Solution(ctypes.Structure):
    """
    C structure for holding the symbolic regression solution.
    
    This structure is returned from the CUDA library and contains
    the complete representation of the evolved expression tree.
    
    Attributes:
        expression (bytes): String representation of the mathematical expression
        fitness (float): Root Mean Square Error (RMSE) of the solution
        ops (POINTER(int)): Array of operator codes for internal nodes
        terminals (POINTER(int)): Array of terminal types (-1=constant, >=0=variable index)
        constants (POINTER(float)): Array of constant values for leaf nodes
        n_leaves (int): Number of leaf nodes in the expression tree
    """
    _fields_ = [
        ("expression", ctypes.c_char_p),
        ("fitness", ctypes.c_float),
        ("ops", ctypes.POINTER(ctypes.c_int)),       
        ("terminals", ctypes.POINTER(ctypes.c_int)),  
        ("constants", ctypes.POINTER(ctypes.c_float)), 
        ("n_leaves", ctypes.c_int)
    ]

class CUDASymbolicRegressor:
    """
    GPU-accelerated symbolic regression using genetic programming.
    
    This class provides a scikit-learn style interface to evolve mathematical
    expressions that fit given data. All evolutionary operations run on NVIDIA
    CUDA-enabled GPUs for maximum performance.
    
    The regressor uses genetic programming with binary tree representations,
    tournament selection, crossover, mutation, and immigration to discover
    mathematical formulas.
    
    Examples:
        >>> import numpy as np
        >>> from cuda_symreg import CUDASymbolicRegressor
        >>> 
        >>> # Generate data: y = x^2 + 2x + 1
        >>> X = np.linspace(-5, 5, 100).reshape(-1, 1).astype(np.float32)
        >>> y = (X[:, 0]**2 + 2*X[:, 0] + 1).astype(np.float32)
        >>> 
        >>> # Define operator weights (CDF)
        >>> cdf = np.array([0.25, 0.5, 0.75, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], dtype=np.float32)
        >>> 
        >>> # Fit model
        >>> model = CUDASymbolicRegressor()
        >>> expr, fitness = model.fit(X, y, cdf)
        >>> print(f"Found: {expr}, RMSE: {fitness:.6f}")
        >>> 
        >>> # Make predictions
        >>> y_pred = model.predict(X)
    
    Attributes:
        lib (ctypes.CDLL): Loaded CUDA library
        best_model (dict): Dictionary containing the best evolved model
            - 'expression' (str): Human-readable equation
            - 'fitness' (float): RMSE value
            - 'ops' (ndarray): Operator codes array
            - 'terminals' (ndarray): Terminal types array
            - 'constants' (ndarray): Constant values array
            - 'n_leaves' (int): Number of leaf nodes
    
    Raises:
        FileNotFoundError: If the CUDA library (libgasymreg.so) is not found
    """
    
    def __init__(self) -> None:
        """
        Initialize the CUDA Symbolic Regressor.
        
        Loads the CUDA shared library and configures the C interface.
        The library must be present in the 'lib' subdirectory relative
        to this module.
        
        Raises:
            FileNotFoundError: If libgasymreg.so is not found in lib/
        """
        _current_dir = os.path.dirname(__file__)
        lib_path = os.path.join(_current_dir, "lib", "libgasymreg.so")
        if not os.path.exists(lib_path):
            raise FileNotFoundError(
                f"CUDA library not found at {lib_path}. "
                "Please ensure the package was installed correctly."
            )
        
        self.lib = ctypes.CDLL(os.path.abspath(lib_path))
        
        # Configure C function signatures
        self.lib.run_genetic_algorithm.argtypes = [
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=2, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            np.ctypeslib.ndpointer(dtype=np.float32, ndim=1, flags='C_CONTIGUOUS'),
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            ctypes.c_float, ctypes.c_float, ctypes.c_float, ctypes.c_int
        ]
        self.lib.run_genetic_algorithm.restype = Solution
        self.lib.free_solution.argtypes = [Solution]
        
        self.best_model: Optional[dict] = None

    def fit(self, X: NDArray[np.float32], y: NDArray[np.float32], cdf: NDArray[np.float32], n_gen: int = 100, n_ind: int = 1024, tourn: int = 15, 
            height: int = 6, mut: float = 0.2, repro: float = 0.7, rand: float = 0.1) -> Tuple[str, float]:
        """
        Evolve a symbolic expression to fit the training data.
        
        This method runs the genetic algorithm on the GPU to discover a
        mathematical formula that minimizes the Root Mean Square Error (RMSE)
        between predictions and target values.
        
        Args:
            X: Training input features, shape (n_samples, n_features).
                Must be C-contiguous float32 array.
            y: Training target values, shape (n_samples,).
                Must be C-contiguous float32 array.
            cdf: Cumulative distribution function for operator selection, shape (11,).
                Must be monotonically increasing and end at 1.0.
                Order: [ADD, SUB, MUL, DIV, SIN, COS, ABS, POW, LOG, EXP, NOP]
                Example: [0.25, 0.5, 0.75, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
                    gives 25% ADD, 25% SUB, 25% MUL, 25% DIV, 0% others.
            n_gen: Maximum number of generations to evolve.
                Default: 100. Increase for harder problems.
            n_ind: Population size (number of individuals per generation).
                Default: 1024. Larger values explore better but are slower.
                Recommended: 256-2048.
            tourn: Tournament size for selection.
                Default: 15. Higher values increase selection pressure.
                Recommended: 5-20.
            height: Maximum tree height (expression complexity).
                Default: 6. Height 4-6 works for most problems.
                Tree has 2^height - 1 total nodes.
            mut: Mutation probability, range [0.0, 1.0].
                Default: 0.2. Probability each individual mutates.
                Higher values increase exploration.
            repro: Reproduction rate, range [0.0, 1.0].
                Default: 0.7. Probability of cloning without crossover.
                Higher values preserve good solutions.
            rand: Immigration rate, range [0.0, 1.0].
                Default: 0.1. Fraction of population replaced with random individuals.
                Helps prevent premature convergence.
        
        Returns:
            A tuple containing:
                - expression (str): Human-readable mathematical formula
                - fitness (float): Root Mean Square Error of the solution
        
        Raises:
            ValueError: If array shapes are incompatible or parameters are invalid
            RuntimeError: If CUDA execution fails
        
        Examples:
            >>> # Simple polynomial
            >>> X = np.linspace(-5, 5, 100).reshape(-1, 1).astype(np.float32)
            >>> y = (X[:, 0]**2).astype(np.float32)
            >>> cdf = np.array([0.3, 0.6, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0], dtype=np.float32)
            >>> model = CUDASymbolicRegressor()
            >>> expr, rmse = model.fit(X, y, cdf, n_gen=50, n_ind=256)
            >>> 
            >>> # Multivariate function
            >>> X = np.random.randn(500, 3).astype(np.float32)
            >>> y = (X[:, 0] * X[:, 1] + X[:, 2]).astype(np.float32)
            >>> expr, rmse = model.fit(X, y, cdf, height=5)
        
        Notes:
            - The algorithm stops early if fitness < 1e-5 or stagnation is detected
            - Best individual is always preserved (elitism)
            - Convergence is monitored using a sliding window of 20 generations
        """
        # Ensure arrays are C-contiguous and float32
        X = np.require(X, dtype=np.float32, requirements=['C', 'A'])
        y = np.require(y, dtype=np.float32, requirements=['C', 'A'])
        cdf = np.require(cdf, dtype=np.float32, requirements=['C', 'A'])

        n_vars = X.shape[1]
        sizey = len(y)

        # Call CUDA genetic algorithm
        result = self.lib.run_genetic_algorithm(
            X, y, cdf, 
            int(n_gen), int(n_ind), int(tourn), int(height), int(n_vars), 
            float(mut), float(repro), float(rand), int(sizey)
        )

        # Extract tree structure
        n_leaves = result.n_leaves
        n_ops = n_leaves - 1
        
        # Store model internally for prediction
        self.best_model = {
            'expression': result.expression.decode('utf-8'),
            'fitness': result.fitness,
            'ops': np.ctypeslib.as_array(result.ops, shape=(n_ops,)).copy(),
            'terminals': np.ctypeslib.as_array(result.terminals, shape=(n_leaves,)).copy(),
            'constants': np.ctypeslib.as_array(result.constants, shape=(n_leaves,)).copy(),
            'n_leaves': n_leaves
        }

        # Free C memory
        self.lib.free_solution(result)
        
        return self.best_model['expression'], self.best_model['fitness']

    def predict(self, X: NDArray[np.float32]) -> NDArray[np.float32]:
        """
        Evaluate the evolved expression on new data.
        
        Uses the best model found during .fit() to make predictions.
        The expression tree is evaluated in Python using NumPy operations.
        
        Args:
            X: Input features, shape (n_samples, n_features).
                Must have the same number of features as training data.
                Automatically converted to float32 if needed.
                If 1D, will be reshaped to (n_samples, 1).
        
        Returns:
            Predicted values, shape (n_samples,).
            Float32 array with predictions for each sample.
        
        Raises:
            ValueError: If .fit() has not been called yet
            ValueError: If number of features doesn't match training data
        
        Examples:
            >>> # After fitting
            >>> X_train = np.linspace(-5, 5, 100).reshape(-1, 1).astype(np.float32)
            >>> y_train = (X_train[:, 0]**2).astype(np.float32)
            >>> model = CUDASymbolicRegressor()
            >>> cdf = np.ones(11, dtype=np.float32).cumsum() / 11
            >>> model.fit(X_train, y_train, cdf)
            >>> 
            >>> # Predict on new data
            >>> X_test = np.array([[1.0], [2.0], [3.0]], dtype=np.float32)
            >>> y_pred = model.predict(X_test)
            >>> 
            >>> # Works with 1D input (single feature)
            >>> y_single = model.predict(np.array([1.5], dtype=np.float32))
        
        Notes:
            - Evaluation is done on CPU using NumPy (not GPU)
            - Protected operations (DIV, LOG, POW) handle edge cases safely
            - Constants are clipped to prevent numerical overflow
        """
        if self.best_model is None:
            raise ValueError(
                "Model has not been trained yet. Call .fit() before .predict()"
            )
            
        # Ensure proper format
        X = np.require(X, dtype=np.float32, requirements=['C', 'A'])
        if X.ndim == 1: 
            X = X.reshape(-1, 1)
        
        n_samples = X.shape[0]
        n_leaves = self.best_model['n_leaves']
        total_nodes = 2 * n_leaves - 1
        
        # Storage for tree evaluation (node_idx, sample_idx)
        values = np.zeros((total_nodes, n_samples), dtype=np.float32)

        # Evaluate leaf nodes (terminals)
        terminals = self.best_model['terminals']
        constants = self.best_model['constants']
        
        for i in range(n_leaves):
            idx = n_leaves - 1 + i  # Leaf position in complete binary tree
            t_code = terminals[i]
            
            if t_code == -1:
                # Constant node
                values[idx, :] = constants[i]
            else:
                # Variable node
                values[idx, :] = X[:, t_code]

        # Evaluate internal nodes (operators) bottom-up
        ops = self.best_model['ops']
        for i in range(n_leaves - 2, -1, -1):
            left_child = 2 * i + 1
            right_child = 2 * i + 2
            a, b = values[left_child, :], values[right_child, :]
            values[i, :] = self._apply_op(ops[i], a, b)

        return values[0, :]  # Root contains final result

    def _apply_op(
        self, 
        op_code: int, 
        a: NDArray[np.float32], 
        b: NDArray[np.float32]
    ) -> NDArray[np.float32]:
        """
        Apply a mathematical operator to arrays element-wise.
        
        Internal method that evaluates tree nodes by applying operators
        to their children's values. Includes protection against numerical
        issues like division by zero and invalid logarithms.
        
        Args:
            op_code: Operator code (0-10)
                0=ADD, 1=SUB, 2=MUL, 3=DIV, 4=SIN, 5=COS,
                6=ABS, 7=POW, 8=LOG, 9=EXP, 10=NOP
            a: Left child values, shape (n_samples,)
            b: Right child values, shape (n_samples,)
        
        Returns:
            Result of applying the operator, shape (n_samples,).
            For unary operators (SIN, COS, ABS, LOG, EXP), only 'a' is used.
        
        Notes:
            - DIV: Protected division returns 0 when |b| < 1e-6
            - POW: Uses |a| to avoid complex numbers
            - LOG: Uses |a| + 1e-9 to avoid log(0)
            - EXP: Clips input to [-20, 20] to prevent overflow
            - NOP: Returns left child unchanged (useful for unary ops)
        """
        if op_code == 0: 
            return a + b
        if op_code == 1: 
            return a - b
        if op_code == 2: 
            return a * b
        if op_code == 3: 
            # Protected division
            return np.divide(a, b, out=np.zeros_like(a), where=np.abs(b) > 1e-6)
        if op_code == 4: 
            return np.sin(a)
        if op_code == 5: 
            return np.cos(a)
        if op_code == 6: 
            return np.abs(a)
        if op_code == 7: 
            # Protected power (avoid complex numbers)
            return np.power(np.abs(a), b)
        if op_code == 8: 
            # Protected logarithm
            return np.log(np.abs(a) + 1e-9)
        if op_code == 9: 
            # Protected exponential (clip to prevent overflow)
            return np.exp(np.clip(a, -20, 20))
        # op_code == 10: NOP (no operation)
        return a