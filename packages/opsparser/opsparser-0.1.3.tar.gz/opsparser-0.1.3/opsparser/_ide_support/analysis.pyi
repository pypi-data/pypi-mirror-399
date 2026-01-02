"""分析命令类型注解"""

from typing import Literal, Optional, Any, Union, overload, TypedDict

class ModalPropertiesResult(TypedDict, total=False):
    """Modal properties analysis result dictionary"""
    domainSize: list[int]
    eigenLambda: list[float] 
    eigenOmega: list[float]
    eigenFrequency: list[float]
    eigenPeriod: list[float]
    totalMass: list[float]
    totalFreeMass: list[float]
    centerOfMass: list[float]
    # Modal participation factors
    partiFactorMX: list[float]
    partiFactorMY: list[float]
    partiFactorMZ: list[float]
    partiFactorRMX: list[float]
    partiFactorRMY: list[float]
    partiFactorRMZ: list[float]
    # Modal participation masses
    partiMassMX: list[float]
    partiMassMY: list[float]
    partiMassMZ: list[float]
    partiMassRMX: list[float]
    partiMassRMY: list[float]
    partiMassRMZ: list[float]
    # Cumulative modal participation masses
    partiMassesCumuMX: list[float]
    partiMassesCumuMY: list[float]
    partiMassesCumuMZ: list[float]
    partiMassesCumuRMX: list[float]
    partiMassesCumuRMY: list[float]
    partiMassesCumuRMZ: list[float]
    # Modal participation mass ratios (%)
    partiMassRatiosMX: list[float]
    partiMassRatiosMY: list[float]
    partiMassRatiosMZ: list[float]
    partiMassRatiosRMX: list[float]
    partiMassRatiosRMY: list[float]
    partiMassRatiosRMZ: list[float]
    # Cumulative modal participation mass ratios (%)
    partiMassRatiosCumuMX: list[float]
    partiMassRatiosCumuMY: list[float]
    partiMassRatiosCumuMZ: list[float]
    partiMassRatiosCumuRMX: list[float]
    partiMassRatiosCumuRMY: list[float]
    partiMassRatiosCumuRMZ: list[float]

class AnalysisCommands:
    """分析命令的类型注解"""
    
    # Constraint handlers
    @overload
    def constraints(self, constraintType: Literal["Plain"]) -> None:
        """Plain constraint handler - enforces homogeneous single point constraints and identity matrix multi-point constraints
        
        Args:
            constraintType: Must be "Plain"
            
        Note:
            Can only enforce homogeneous single point constraints (fix command) and 
            multi-point constraints where constraint matrix equals identity (equalDOF command)
            
        Example:
            ops.constraints('Plain')
        """
        ...
    
    @overload
    def constraints(self, constraintType: Literal["Lagrange"], alphaS: float = 1.0, alphaM: float = 1.0) -> None:
        """Lagrange multiplier constraint handler - enforces constraints by introducing Lagrange multipliers
        
        Args:
            constraintType: Must be "Lagrange"
            alphaS: Factor on single points (default: 1.0)
            alphaM: Factor on multi-points (default: 1.0)
            
        Note:
            Introduces new unknowns to system equations. System is NOT symmetric positive definite.
            
        Examples:
            ops.constraints('Lagrange')
            ops.constraints('Lagrange', 1.0, 1.0)
        """
        ...
    
    @overload
    def constraints(self, constraintType: Literal["Penalty"], alphaS: float = 1.0, alphaM: float = 1.0) -> None:
        """Penalty method constraint handler - enforces constraints using penalty method
        
        Args:
            constraintType: Must be "Penalty"
            alphaS: Factor on single points (default: 1.0)
            alphaM: Factor on multi-points (default: 1.0)
            
        Note:
            Constraint enforcement depends on penalty values. Too small = weak enforcement,
            too large = conditioning problems.
            
        Examples:
            ops.constraints('Penalty')
            ops.constraints('Penalty', 1.0e12, 1.0e12)
        """
        ...
    
    @overload
    def constraints(self, constraintType: Literal["Transformation"]) -> None:
        """Transformation method constraint handler - enforces constraints using transformation method
        
        Args:
            constraintType: Must be "Transformation"
            
        Note:
            Single-point constraints are enforced directly. Great care needed with multiple constraints:
            - Use fix command for fixed nodes, not equalDOF
            - Ensure retained nodes aren't constrained elsewhere
            - Avoid constraining nodes to multiple other nodes
            
        Example:
            ops.constraints('Transformation')
        """
        ...
    
    @overload  
    def constraints(self, constraintType: Literal["Plain", "Penalty", "Lagrange", "Transformation"], *constraintArgs: float) -> None:
        """Define constraint handler - determines how constraint equations are enforced
        
        Args:
            constraintType: Type of constraint handler ("Plain" | "Penalty" | "Lagrange" | "Transformation")
            constraintArgs: Handler-specific parameters
            
        Available constraint types:
            - Plain: For homogeneous single point and identity matrix multi-point constraints
            - Lagrange: Uses Lagrange multipliers (introduces new unknowns) - alphaS, alphaM
            - Penalty: Uses penalty method (constraint enforcement depends on penalty values) - alphaS, alphaM  
            - Transformation: Uses transformation method (direct enforcement)
            
        Examples:
            ops.constraints('Plain')
            ops.constraints('Lagrange', 1.0, 1.0)
            ops.constraints('Penalty', 1.0e12, 1.0e12)
            ops.constraints('Transformation')
        """
        ...
    
    # DOF numberers
    @overload
    def numberer(self, numberer_type: Literal["Plain"]) -> None:
        """Plain DOF numberer - simple node ordering based on domain order
        
        Args:
            numberer_type: Must be "Plain"
            
        Note:
            Takes whatever order the domain gives nodes. Fine for small problems and 
            sparse matrix solvers, but poor choice for large models with other solvers.
            
        Example:
            ops.numberer('Plain')
        """
        ...
    
    @overload
    def numberer(self, numberer_type: Literal["RCM"]) -> None:
        """RCM DOF numberer - uses reverse Cuthill-McKee scheme
        
        Args:
            numberer_type: Must be "RCM"
            
        Note:
            Uses reverse Cuthill-McKee scheme to order matrix equations.
            Better performance than Plain for large models.
            
        Example:
            ops.numberer('RCM')
        """
        ...
    
    @overload
    def numberer(self, numberer_type: Literal["AMD"]) -> None:
        """AMD DOF numberer - uses approximate minimum degree scheme
        
        Args:
            numberer_type: Must be "AMD"
            
        Note:
            Uses approximate minimum degree scheme to order matrix equations.
            Good performance for large sparse systems.
            
        Example:
            ops.numberer('AMD')
        """
        ...
    
    @overload
    def numberer(self, numberer_type: Literal["ParallelPlain"]) -> None:
        """Parallel Plain DOF numberer - parallel version of Plain numberer
        
        Args:
            numberer_type: Must be "ParallelPlain"
            
        Warning:
            Use ONLY for parallel models. Don't use for non-parallel models 
            (e.g., parametric studies).
            
        Example:
            ops.numberer('ParallelPlain')
        """
        ...
    
    @overload
    def numberer(self, numberer_type: Literal["ParallelRCM"]) -> None:
        """Parallel RCM DOF numberer - parallel version of RCM numberer
        
        Args:
            numberer_type: Must be "ParallelRCM"
            
        Warning:
            Use ONLY for parallel models. Don't use for non-parallel models 
            (e.g., parametric studies).
            
        Example:
            ops.numberer('ParallelRCM')
        """
        ...
    
    @overload
    def numberer(self, numberer_type: Literal["Plain", "RCM", "AMD", "ParallelPlain", "ParallelRCM"], *args: Any) -> None:
        """Define DOF numberer - determines mapping between DOFs and equation numbers
        
        Args:
            numberer_type: Numberer type ("Plain" | "RCM" | "AMD" | "ParallelPlain" | "ParallelRCM")
            args: Numberer-specific parameters (currently unused)
            
        Available numberer types:
            - Plain: Simple ordering based on domain order (good for small problems)
            - RCM: Reverse Cuthill-McKee scheme (better for large models)
            - AMD: Approximate minimum degree scheme (good for sparse systems)
            - ParallelPlain: Parallel version of Plain (parallel models only)
            - ParallelRCM: Parallel version of RCM (parallel models only)
            
        Examples:
            ops.numberer('Plain')

            ops.numberer('RCM')

            ops.numberer('AMD')

            ops.numberer('ParallelPlain')  # Only for parallel models

            ops.numberer('ParallelRCM')    # Only for parallel models
        """
        ...
    
    # System of equations
    @overload
    def system(self, system_type: Literal["BandGen"]) -> None:
        """BandGeneral SOE - for matrix systems with banded profile
        
        Args:
            system_type: Must be "BandGen"
            
        Note:
            Uses Lapack routines DGBSV and SGBTRS. Suitable for banded matrices.
            Storage size = bandwidth × number of unknowns.
            
        Example:
            ops.system('BandGen')
            
        Typical structural examples:
            - Truss structures with regular connectivity
            - Frame structures with systematic node numbering
        """
        ...
    
    @overload
    def system(self, system_type: Literal["BandSPD"]) -> None:
        """BandSPD SOE - for symmetric positive definite matrices with banded profile
        
        Args:
            system_type: Must be "BandSPD"
            
        Note:
            Uses Lapack routines DPBSV and DPBTRS. More efficient than BandGen for SPD systems.
            Storage size = (bandwidth/2) × number of unknowns.
            
        Example:
            ops.system('BandSPD')
            
        Typical structural examples:
            - Static analysis of frame structures
            - Elastic beam/shell structures without damping
        """
        ...
    
    @overload
    def system(self, system_type: Literal["ProfileSPD"]) -> None:
        """ProfileSPD SOE - symmetric positive definite with skyline storage
        
        Args:
            system_type: Must be "ProfileSPD"
            
        Note:
            Uses skyline storage scheme. Stores only values below first non-zero in each column.
            More memory efficient than banded solvers for irregular structures.
            
        Example:
            ops.system('ProfileSPD')
            
        Typical structural examples:
            - Irregular finite element meshes
            - Complex geometric structures with varying connectivity
        """
        ...
    
    @overload
    def system(self, system_type: Literal["SuperLU"]) -> None:
        """SuperLU SOE - sparse matrix solver using SuperLU library
        
        Args:
            system_type: Must be "SuperLU"
            
        Note:
            Efficient for large sparse systems. Good general-purpose solver.
            
        Example:
            ops.system('SuperLU')
            
        Typical structural examples:
            - Large finite element models
            - Complex 3D structures with many elements
        """
        ...
    
    @overload
    def system(self, system_type: Literal["UmfPack"]) -> None:
        """UmfPack SOE - sparse matrix solver using UmfPack library
        
        Args:
            system_type: Must be "UmfPack"
            
        Note:
            Alternative sparse solver, often faster than SuperLU for certain problems.
            
        Example:
            ops.system('UmfPack')
            
        Typical structural examples:
            - Large structural systems
            - Problems with high sparsity patterns
        """
        ...
    
    @overload
    def system(self, system_type: Literal["FullGeneral"]) -> None:
        """FullGeneral SOE - full matrix storage (USE WITH CAUTION)
        
        Args:
            system_type: Must be "FullGeneral"
            
        Warning:
            Uses nxn memory storage. Should ALMOST NEVER be used due to high memory 
            requirements and slow performance. Only for examining global system matrix.
            
        Example:
            ops.system('FullGeneral')
            
        Typical structural examples:
            - Very small models for debugging
            - Educational purposes to examine system matrix
        """
        ...
    
    @overload
    def system(self, system_type: Literal["SparseSYM"]) -> None:
        """SparseSYM SOE - sparse symmetric solver with row-oriented solution
        
        Args:
            system_type: Must be "SparseSYM"
            
        Note:
            Specialized for symmetric sparse systems with row-oriented solution method.
            
        Example:
            ops.system('SparseSYM')
            
        Typical structural examples:
            - Symmetric structural systems
            - Static analysis without damping effects
        """
        ...
    
    @overload
    def system(self, system_type: Literal["Mumps"], *args: Union[str, float, int]) -> None:
        """MUMPS solver - parallel sparse direct solver (PARALLEL MODELS ONLY)
        
        Args:
            system_type: Must be "Mumps"
            args: Optional MUMPS control parameters
            
        Parameters:
            -ICNTL14 <value>: Controls percentage increase in estimated working space (default: 20.0)
            -ICNTL7 <value>: Symmetric permutation for pivot ordering (default: 7=automatic)
                0=AMD, 1=user set, 2=AMF, 3=SCOTCH, 4=PORD, 5=Metis, 6=AMD with QADM, 7=automatic
            
        Warning:
            Use ONLY for parallel models. Don't use for non-parallel models (e.g., parametric studies).
            
        Examples:
            ops.system('Mumps')

            ops.system('Mumps', '-ICNTL14', 20.0, '-ICNTL7', 7)
            
        Typical structural examples:
            - Large-scale parallel finite element models
            - Distributed structural analysis
        """
        ...
    
    @overload
    def system(self, system_type: Literal["BandGen", "BandSPD", "ProfileSPD", "SuperLU", "UmfPack", "FullGeneral", "SparseSYM", "Mumps"], *args: Union[str, float, int]) -> None:
        """Define system of equations solver - constructs LinearSOE and LinearSolver objects
        
        Args:
            system_type: System solver type
            args: Solver-specific parameters
            
        Available system types:
            - BandGen: Banded general matrices (Lapack DGBSV/SGBTRS)
            - BandSPD: Banded symmetric positive definite (Lapack DPBSV/DPBTRS)
            - ProfileSPD: Skyline storage for SPD systems
            - SuperLU: Sparse general solver (good for large systems)
            - UmfPack: Alternative sparse solver (often faster)
            - FullGeneral: Full matrix storage (avoid unless necessary)
            - SparseSYM: Sparse symmetric with row-oriented solution
            - Mumps: Parallel sparse direct solver (parallel models only)
            
        Performance recommendations:
            - Small banded systems: BandSPD > BandGen
            - Large sparse systems: SuperLU/UmfPack > others
            - Irregular structures: ProfileSPD > Banded solvers
            - Parallel models: Mumps
            - Avoid: FullGeneral (memory intensive)
            
        Examples:
            ops.system('BandSPD')                    # For banded SPD systems

            ops.system('SuperLU')                    # For large sparse systems

            ops.system('Mumps', '-ICNTL14', 20.0)   # For parallel models
        """
        ...
    
    # Convergence tests
    @overload
    def test(self, test_type: Literal["NormUnbalance"], tol: float, iter: int, pFlag: int = 0, nType: int = 2, maxIncr: int = -1) -> None:
        """NormUnbalance test - uses norm of right hand side (residual) for convergence
        
        Args:
            test_type: Must be "NormUnbalance"
            tol: Tolerance criteria for convergence
            iter: Maximum number of iterations
            pFlag: Print flag (0=nothing, 1=norms, 2=final info, 4=detailed, 5=ignore failure)
            nType: Norm type (0=max-norm, 1=1-norm, 2=2-norm)
            maxIncr: Maximum times of error increasing
            
        Note:
            Not suitable with Penalty method due to additional large forces.
            
        Example:
            ops.test('NormUnbalance', 1.0e-6, 100, 1, 2)
        """
        ...
    
    @overload
    def test(self, test_type: Literal["NormDispIncr"], tol: float, iter: int, pFlag: int = 0, nType: int = 2) -> None:
        """NormDispIncr test - uses norm of displacement increment for convergence
        
        Args:
            test_type: Must be "NormDispIncr"
            tol: Tolerance criteria for convergence
            iter: Maximum number of iterations
            pFlag: Print flag (0=nothing, 1=norms, 2=final info, 4=detailed, 5=ignore failure)
            nType: Norm type (0=max-norm, 1=1-norm, 2=2-norm)
            
        Note:
            When using Lagrange method, Lagrange multipliers appear in solution vector.
            
        Example:
            ops.test('NormDispIncr', 1.0e-6, 100)
        """
        ...
    
    @overload
    def test(self, test_type: Literal["EnergyIncr"], tol: float, iter: int, pFlag: int = 0, nType: int = 2) -> None:
        """EnergyIncr test - uses dot product of solution vector and residual for convergence
        
        Args:
            test_type: Must be "EnergyIncr"
            tol: Tolerance criteria for convergence
            iter: Maximum number of iterations
            pFlag: Print flag (0=nothing, 1=norms, 2=final info, 4=detailed, 5=ignore failure)
            nType: Norm type (0=max-norm, 1=1-norm, 2=2-norm)
            
        Note:
            Problems with Penalty method (large forces) and Lagrange method (multipliers in solution).
            
        Example:
            ops.test('EnergyIncr', 1.0e-8, 100)
        """
        ...
    
    @overload
    def test(self, test_type: Literal["RelativeNormUnbalance"], tol: float, iter: int, pFlag: int = 0, nType: int = 2) -> None:
        """RelativeNormUnbalance test - uses relative norm of residual for convergence
        
        Args:
            test_type: Must be "RelativeNormUnbalance"
            tol: Tolerance criteria for convergence
            iter: Maximum number of iterations
            pFlag: Print flag (0=nothing, 1=norms, 2=final info, 4=detailed, 5=ignore failure)
            nType: Norm type (0=max-norm, 1=1-norm, 2=2-norm)
            
        Note:
            Not suitable with Penalty method due to additional large forces.
            
        Example:
            ops.test('RelativeNormUnbalance', 1.0e-6, 100)
        """
        ...
    
    @overload
    def test(self, test_type: Literal["RelativeNormDispIncr"], tol: float, iter: int, pFlag: int = 0, nType: int = 2) -> None:
        """RelativeNormDispIncr test - uses relative norm of displacement increment
        
        Args:
            test_type: Must be "RelativeNormDispIncr"
            tol: Tolerance criteria for convergence
            iter: Maximum number of iterations
            pFlag: Print flag (0=nothing, 1=norms, 2=final info, 4=detailed, 5=ignore failure)
            nType: Norm type (0=max-norm, 1=1-norm, 2=2-norm)
            
        Example:
            ops.test('RelativeNormDispIncr', 1.0e-6, 100)
        """
        ...
    
    @overload
    def test(self, test_type: Literal["RelativeTotalNormDispIncr"], tol: float, iter: int, pFlag: int = 0, nType: int = 2) -> None:
        """RelativeTotalNormDispIncr test - uses ratio of current norm to total norm
        
        Args:
            test_type: Must be "RelativeTotalNormDispIncr"
            tol: Tolerance criteria for convergence
            iter: Maximum number of iterations
            pFlag: Print flag (0=nothing, 1=norms, 2=final info, 4=detailed, 5=ignore failure)
            nType: Norm type (0=max-norm, 1=1-norm, 2=2-norm)
            
        Note:
            Uses ratio of current norm to sum of all norms since last convergence.
            
        Example:
            ops.test('RelativeTotalNormDispIncr', 1.0e-6, 100)
        """
        ...
    
    @overload
    def test(self, test_type: Literal["RelativeEnergyIncr"], tol: float, iter: int, pFlag: int = 0, nType: int = 2) -> None:
        """RelativeEnergyIncr test - uses relative energy increment for convergence
        
        Args:
            test_type: Must be "RelativeEnergyIncr"
            tol: Tolerance criteria for convergence
            iter: Maximum number of iterations
            pFlag: Print flag (0=nothing, 1=norms, 2=final info, 4=detailed, 5=ignore failure)
            nType: Norm type (0=max-norm, 1=1-norm, 2=2-norm)
            
        Example:
            ops.test('RelativeEnergyIncr', 1.0e-8, 100)
        """
        ...
    
    @overload
    def test(self, test_type: Literal["FixedNumIter"], iter: int, pFlag: int = 0, nType: int = 2) -> None:
        """FixedNumIter test - performs fixed number of iterations without convergence check
        
        Args:
            test_type: Must be "FixedNumIter"
            iter: Fixed number of iterations to perform
            pFlag: Print flag (0=nothing, 1=norms, 2=final info, 4=detailed, 5=ignore failure)
            nType: Norm type (0=max-norm, 1=1-norm, 2=2-norm)
            
        Note:
            No convergence checking - always performs exactly 'iter' iterations.
            
        Example:
            ops.test('FixedNumIter', 10)
        """
        ...
    
    @overload
    def test(self, test_type: Literal["NormDispAndUnbalance"], tolIncr: float, tolR: float, iter: int, pFlag: int = 0, nType: int = 2, maxincr: int = -1) -> None:
        """NormDispAndUnbalance test - requires BOTH displacement and residual convergence
        
        Args:
            test_type: Must be "NormDispAndUnbalance"
            tolIncr: Tolerance for displacement increments
            tolR: Tolerance for residual (unbalanced forces)
            iter: Maximum number of iterations
            pFlag: Print flag (0=nothing, 1=norms, 2=final info, 4=detailed, 5=ignore failure)
            nType: Norm type (0=max-norm, 1=1-norm, 2=2-norm)
            maxincr: Maximum times of error increasing
            
        Note:
            Most stringent test - both displacement AND force criteria must be satisfied.
            
        Example:
            ops.test('NormDispAndUnbalance', 1.0e-6, 1.0e-6, 100)
        """
        ...
    
    @overload
    def test(self, test_type: Literal["NormDispOrUnbalance"], tolIncr: float, tolR: float, iter: int, pFlag: int = 0, nType: int = 2, maxincr: int = -1) -> None:
        """NormDispOrUnbalance test - requires EITHER displacement OR residual convergence
        
        Args:
            test_type: Must be "NormDispOrUnbalance"
            tolIncr: Tolerance for displacement increments  
            tolR: Tolerance for residual (unbalanced forces)
            iter: Maximum number of iterations
            pFlag: Print flag (0=nothing, 1=norms, 2=final info, 4=detailed, 5=ignore failure)
            nType: Norm type (0=max-norm, 1=1-norm, 2=2-norm)
            maxincr: Maximum times of error increasing
            
        Note:
            Less stringent - converges when EITHER displacement OR force criteria is satisfied.
            
        Example:
            ops.test('NormDispOrUnbalance', 1.0e-6, 1.0e-6, 100)
        """
        ...
    
    @overload
    def test(self, test_type: Literal["NormUnbalance", "NormDispIncr", "EnergyIncr", "RelativeNormUnbalance", "RelativeNormDispIncr", "RelativeTotalNormDispIncr", "RelativeEnergyIncr", "FixedNumIter", "NormDispAndUnbalance", "NormDispOrUnbalance"], *args: Union[float, int]) -> None:
        """Define convergence test - determines when nonlinear solution has converged
        
        Args:
            test_type: Type of convergence test
            args: Test-specific parameters
            
        Available test types:
            - NormUnbalance: Uses residual norm (avoid with Penalty method)
            - NormDispIncr: Uses displacement increment norm
            - EnergyIncr: Uses energy increment (dot product of solution and residual)
            - RelativeNormUnbalance: Relative residual norm 
            - RelativeNormDispIncr: Relative displacement increment norm
            - RelativeTotalNormDispIncr: Ratio to total accumulated norm
            - RelativeEnergyIncr: Relative energy increment
            - FixedNumIter: Fixed iterations without convergence check
            - NormDispAndUnbalance: Both displacement AND residual must converge
            - NormDispOrUnbalance: Either displacement OR residual must converge
            
        Common parameters:
            - tol: Convergence tolerance (typically 1e-6 to 1e-8)
            - iter: Maximum iterations (typically 25-100)
            - pFlag: Print level (0=silent, 1=norms, 2=summary, 4=detailed, 5=ignore failure)
            - nType: Norm type (0=max, 1=1-norm, 2=2-norm)
            
        Selection guidelines:
            - General use: NormDispIncr or NormUnbalance
            - Penalty constraints: Use NormDispIncr (NOT NormUnbalance)
            - Lagrange constraints: Be aware of multipliers in solution
            - Strict convergence: NormDispAndUnbalance
            - Debugging: FixedNumIter with detailed print flags
            
        Examples:
            ops.test('NormDispIncr', 1.0e-6, 100)           # Standard displacement test

            ops.test('NormUnbalance', 1.0e-6, 100, 1)       # Residual test with output

            ops.test('NormDispAndUnbalance', 1e-6, 1e-6, 50) # Dual criteria test
            
            ops.test('FixedNumIter', 10, 2)                 # Fixed iterations with summary
        """
        ...

    
    # Solution algorithms
    @overload
    def algorithm(self, algorithm_type: Literal["Linear"], secant: bool = False, initial: bool = False, factorOnce: bool = False) -> None:
        """Linear algorithm - takes one iteration to solve the system
        
        Args:
            algorithm_type: Must be "Linear"
            secant: Use secant stiffness instead of tangent
            initial: Use initial stiffness
            factorOnce: Factor matrix only once (highly recommended for elastic systems)
            
        Note:
            For elastic systems, use factorOnce=True for significant performance improvement.
            Do NOT use factorOnce for nonlinear systems where tangent changes.
            
        Examples:
            ops.algorithm('Linear')                          # Standard linear
            
            ops.algorithm('Linear', factorOnce=True)         # Efficient for elastic systems
        """
        ...
    
    @overload
    def algorithm(self, algorithm_type: Literal["Newton"], secant: bool = False, initial: bool = False, initialThenCurrent: bool = False) -> None:
        """Newton-Raphson algorithm - most robust method for nonlinear equations
        
        Args:
            algorithm_type: Must be "Newton"
            secant: Use secant stiffness instead of tangent
            initial: Use initial stiffness throughout
            initialThenCurrent: Use initial stiffness on first step, then current stiffness
            
        Note:
            Most widely used and robust method for nonlinear algebraic equations.
            Forms and factors tangent matrix at each iteration.
            
        Examples:
            ops.algorithm('Newton')                          # Standard Newton-Raphson

            ops.algorithm('Newton', initial=True)            # Use initial stiffness
        """
        ...
    
    @overload
    def algorithm(self, algorithm_type: Literal["NewtonLineSearch"], Bisection: bool = False, Secant: bool = False, RegulaFalsi: bool = False, InitialInterpolated: bool = False, tol: float = 0.8, maxIter: int = 10, minEta: float = 0.1, maxEta: float = 10.0) -> None:
        """Newton with Line Search - Newton algorithm with line search for improved convergence
        
        Args:
            algorithm_type: Must be "NewtonLineSearch"
            Bisection: Use Bisection line search method
            Secant: Use Secant line search method
            RegulaFalsi: Use RegulaFalsi line search method
            InitialInterpolated: Use InitialInterpolated line search method
            tol: Tolerance for line search (default: 0.8)
            maxIter: Maximum line search iterations (default: 10)
            minEta: Minimum eta value for line search (default: 0.1)
            maxEta: Maximum eta value for line search (default: 10.0)
            
        Note:
            Introduces line search to Newton algorithm to solve nonlinear residual equation.
            Helps with convergence in difficult nonlinear problems.
            
        Examples:
            ops.algorithm('NewtonLineSearch')                                    # Default line search

            ops.algorithm('NewtonLineSearch', Bisection=True, tol=0.5)          # Bisection method
        """
        ...
    
    @overload
    def algorithm(self, algorithm_type: Literal["ModifiedNewton"], secant: bool = False, initial: bool = False) -> None:
        """Modified Newton algorithm - uses tangent from initial guess throughout
        
        Args:
            algorithm_type: Must be "ModifiedNewton"
            secant: Use secant stiffness instead of tangent
            initial: Use initial stiffness
            
        Note:
            Uses tangent at initial guess for all iterations instead of current tangent.
            More efficient than Newton but may converge slower.
            
        Examples:
            ops.algorithm('ModifiedNewton')                  # Standard modified Newton

            ops.algorithm('ModifiedNewton', initial=True)    # Use initial stiffness
        """
        ...
    
    @overload
    def algorithm(self, algorithm_type: Literal["KrylovNewton"], iterate: Literal["current", "initial", "noTangent"] = "current", increment: Literal["current", "initial", "noTangent"] = "current", maxDim: int = 3) -> None:
        """Krylov-Newton algorithm - uses Krylov subspace acceleration
        
        Args:
            algorithm_type: Must be "KrylovNewton"
            iterate: Tangent to iterate on ("current", "initial", "noTangent")
            increment: Tangent to increment on ("current", "initial", "noTangent")
            maxDim: Max iterations until tangent reform and acceleration restart
            
        Note:
            Uses Krylov subspace accelerator to accelerate ModifiedNewton convergence.
            
        Examples:
            ops.algorithm('KrylovNewton')                                        # Default settings

            ops.algorithm('KrylovNewton', 'initial', 'current', 5)              # Custom settings
        """
        ...
    
    @overload
    def algorithm(self, algorithm_type: Literal["SecantNewton"], iterate: Literal["current", "initial", "noTangent"] = "current", increment: Literal["current", "initial", "noTangent"] = "current", maxDim: int = 3) -> None:
        """Secant Newton algorithm - uses two-term update acceleration
        
        Args:
            algorithm_type: Must be "SecantNewton"
            iterate: Tangent to iterate on ("current", "initial", "noTangent")
            increment: Tangent to increment on ("current", "initial", "noTangent")
            maxDim: Max iterations until tangent reform and acceleration restart
            
        Note:
            Uses two-term update to accelerate ModifiedNewton convergence.
            Uses Crisfield's recommended cut-out values (R1=3.5, R2=0.3).
            
        Examples:
            ops.algorithm('SecantNewton')                                        # Default settings

            ops.algorithm('SecantNewton', 'initial', 'initial', 4)              # Custom settings
        """
        ...
    
    @overload
    def algorithm(self, algorithm_type: Literal["RaphsonNewton"], iterate: Literal["current", "initial", "noTangent"] = "current", increment: Literal["current", "initial", "noTangent"] = "current") -> None:
        """Raphson Newton algorithm - uses Raphson accelerator
        
        Args:
            algorithm_type: Must be "RaphsonNewton"
            iterate: Tangent to iterate on ("current", "initial", "noTangent")
            increment: Tangent to increment on ("current", "initial", "noTangent")
            
        Note:
            Uses Raphson accelerator to improve convergence.
            
        Examples:
            ops.algorithm('RaphsonNewton')                                       # Default settings

            ops.algorithm('RaphsonNewton', 'initial', 'current')                # Custom tangent usage
        """
        ...
    
    @overload
    def algorithm(self, algorithm_type: Literal["PeriodicNewton"], iterate: Literal["current", "initial", "noTangent"] = "current", increment: Literal["current", "initial", "noTangent"] = "current", maxDim: int = 3) -> None:
        """Periodic Newton algorithm - uses periodic accelerator
        
        Args:
            algorithm_type: Must be "PeriodicNewton"
            iterate: Tangent to iterate on ("current", "initial", "noTangent")
            increment: Tangent to increment on ("current", "initial", "noTangent")
            maxDim: Max iterations until tangent reform and acceleration restart
            
        Note:
            Uses periodic accelerator for convergence improvement.
            
        Examples:
            ops.algorithm('PeriodicNewton')                                      # Default settings

            ops.algorithm('PeriodicNewton', 'current', 'initial', 5)            # Custom settings
        """
        ...
    
    @overload
    def algorithm(self, algorithm_type: Literal["BFGS"], secant: bool = False, initial: bool = False, count: int = 10) -> None:
        """BFGS algorithm - quasi-Newton method with matrix updates
        
        Args:
            algorithm_type: Must be "BFGS"
            secant: Use secant stiffness instead of tangent
            initial: Use initial stiffness
            count: Number of iterations before reset
            
        Note:
            One of the most effective quasi-Newton methods. Computes new search directions
            based on initial jacobian and trial solutions. Does not require tangent matrix
            reformation at every iteration.
            
        Examples:
            ops.algorithm('BFGS')                            # Standard BFGS

            ops.algorithm('BFGS', count=15)                  # Custom iteration count
        """
        ...
    
    @overload
    def algorithm(self, algorithm_type: Literal["Broyden"], secant: bool = False, initial: bool = False, count: int = 10) -> None:
        """Broyden algorithm - rank-one updates for unsymmetric systems
        
        Args:
            algorithm_type: Must be "Broyden"
            secant: Use secant stiffness instead of tangent
            initial: Use initial stiffness
            count: Number of iterations before reset
            
        Note:
            For general unsymmetric systems. Performs successive rank-one updates
            of tangent at first iteration of current time step.
            
        Examples:
            ops.algorithm('Broyden')                         # Standard Broyden

            ops.algorithm('Broyden', initial=True, count=8)  # Custom settings
        """
        ...
    
    @overload
    def algorithm(self, algorithm_type: Literal["Linear", "Newton", "NewtonLineSearch", "ModifiedNewton", "KrylovNewton", "SecantNewton", "RaphsonNewton", "PeriodicNewton", "BFGS", "Broyden"], *args: Any) -> None:
        """Define solution algorithm - determines sequence of steps for nonlinear equation solving
        
        Args:
            algorithm_type: Type of solution algorithm
            args: Algorithm-specific parameters
            
        Available algorithm types:
            - Linear: One iteration solver (use factorOnce=True for elastic systems)
            - Newton: Most robust, reforms tangent each iteration (recommended for most problems)
            - NewtonLineSearch: Newton with line search (for difficult convergence)
            - ModifiedNewton: Uses initial tangent throughout (faster but slower convergence)
            - KrylovNewton: Krylov subspace acceleration of ModifiedNewton
            - SecantNewton: Two-term update acceleration of ModifiedNewton  
            - RaphsonNewton: Raphson accelerator
            - PeriodicNewton: Periodic accelerator
            - BFGS: Quasi-Newton with matrix updates (efficient for smooth nonlinear problems)
            - Broyden: Rank-one updates for unsymmetric systems
            
        Selection guidelines:
            - General nonlinear: Newton (most robust)
            - Elastic/linear: Linear with factorOnce=True
            - Convergence problems: NewtonLineSearch
            - Computational efficiency: ModifiedNewton, BFGS, or Broyden
            - Acceleration needed: KrylovNewton, SecantNewton, or PeriodicNewton
            - Smooth nonlinear: BFGS
            - Unsymmetric systems: Broyden
            
        Performance comparison:
            - Robustness: Newton > NewtonLineSearch > ModifiedNewton > Quasi-Newton
            - Speed: Linear > ModifiedNewton > Quasi-Newton > Newton > NewtonLineSearch
            - Memory: All similar except accelerated methods use more storage
            
        Examples:
            ops.algorithm('Newton')                                              # Most common choice

            ops.algorithm('Linear', factorOnce=True)                            # For elastic analysis

            ops.algorithm('NewtonLineSearch', Bisection=True, tol=0.5)          # For convergence issues

            ops.algorithm('BFGS', count=15)                                     # Efficient quasi-Newton
        """
        ...
    
    
    # Integrators
    @overload
    def integrator(self, integrator_type: Literal["LoadControl"], incr: float, numIter: int = 1, minIncr: Optional[float] = None, maxIncr: Optional[float] = None) -> None:
        """LoadControl integrator - classical load control method for static analysis
        
        Args:
            integrator_type: Must be "LoadControl"
            incr: Load factor increment λ
            numIter: Desired number of iterations in solution algorithm (default: 1)
            minIncr: Minimum allowed stepsize λ_min (default: incr)
            maxIncr: Maximum allowed stepsize λ_max (default: incr)
            
        Note:
            Change in applied loads depends on active load patterns. For load patterns 
            with Linear time series (factor=1.0), this is classical load control.
            Optional arguments help optimize step size for convergence speed.
            
        Examples:
            ops.integrator('LoadControl', 0.1)                    # Basic load control
            
            ops.integrator('LoadControl', 0.1, 5, 0.01, 0.5)     # With adaptive step size
        """
        ...
    
    @overload
    def integrator(self, integrator_type: Literal["DisplacementControl"], nodeTag: int, dof: int, incr: float, numIter: int = 1, dUmin: Optional[float] = None, dUmax: Optional[float] = None) -> None:
        """DisplacementControl integrator - controls displacement increment at specific DOF
        
        Args:
            integrator_type: Must be "DisplacementControl"
            nodeTag: Tag of node whose response controls solution
            dof: Degree of freedom at the node (1 through ndf)
            incr: First displacement increment ΔU_dof
            numIter: Desired number of iterations in solution algorithm (default: 1)
            dUmin: Minimum allowed stepsize ΔU_min (default: incr)
            dUmax: Maximum allowed stepsize ΔU_max (default: incr)
            
        Note:
            Seeks to determine time step that results in prescribed displacement increment
            for particular DOF at a node. Useful for displacement-controlled tests.
            
        Examples:
            ops.integrator('DisplacementControl', 1, 1, 0.01)              # Node 1, DOF 1

            ops.integrator('DisplacementControl', 5, 2, 0.005, 3, 0.001, 0.02)  # With limits
        """
        ...
    
    @overload
    def integrator(self, integrator_type: Literal["ParallelDisplacementControl"], nodeTag: int, dof: int, incr: float, numIter: int = 1, dUmin: Optional[float] = None, dUmax: Optional[float] = None) -> None:
        """Parallel DisplacementControl integrator - parallel version of displacement control
        
        Args:
            integrator_type: Must be "ParallelDisplacementControl"
            nodeTag: Tag of node whose response controls solution
            dof: Degree of freedom at the node (1 through ndf)
            incr: First displacement increment ΔU_dof
            numIter: Desired number of iterations in solution algorithm (default: 1)
            dUmin: Minimum allowed stepsize ΔU_min (default: incr)
            dUmax: Maximum allowed stepsize ΔU_max (default: incr)
            
        Warning:
            Use ONLY for parallel models. Don't use for non-parallel models (e.g., parametric studies).
            
        Example:
            ops.integrator('ParallelDisplacementControl', 1, 1, 0.01)  # Parallel displacement control
        """
        ...
    
    @overload
    def integrator(self, integrator_type: Literal["MinUnbalDispNorm"], dlambda1: float, Jd: int = 1, minLambda: Optional[float] = None, maxLambda: Optional[float] = None, det: bool = False) -> None:
        """MinUnbalDispNorm integrator - minimum unbalanced displacement norm method
        
        Args:
            integrator_type: Must be "MinUnbalDispNorm"
            dlambda1: First load increment (pseudo-time step) at first iteration
            Jd: Factor relating first load increment at subsequent time steps (default: 1)
            minLambda: Minimum load increment (default: dlambda1)
            maxLambda: Maximum load increment (default: dlambda1)
            det: Determinant flag (default: False)
            
        Example:
            ops.integrator('MinUnbalDispNorm', 0.1, 2, 0.01, 0.5)
        """
        ...
    
    @overload
    def integrator(self, integrator_type: Literal["ArcLength"], s: float, alpha: float) -> None:
        """ArcLength integrator - arc-length control method for static analysis
        
        Args:
            integrator_type: Must be "ArcLength"
            s: The arc length parameter
            alpha: Scaling factor on reference loads
            
        Note:
            Seeks to determine time step that satisfies constraint equation.
            Useful for tracing complete load-displacement curves including post-peak behavior.
            
        Example:
            ops.integrator('ArcLength', 0.1, 1.0)             # Standard arc-length
        """
        ...
    
    @overload
    def integrator(self, integrator_type: Literal["CentralDifference"]) -> None:
        """Central Difference integrator - explicit method for transient analysis
        
        Args:
            integrator_type: Must be "CentralDifference"
            
        Note:
            Explicit integration method using equilibrium at time t to calculate U(t+Δt).
            For diagonal mass matrix without damping, use diagonal solver.
            Stability requirement: Δt/T_n < 1/π
            
        Example:
            ops.integrator('CentralDifference')
        """
        ...
    
    @overload
    def integrator(self, integrator_type: Literal["Newmark"], gamma: float, beta: float, form: Optional[Literal["D", "V", "A"]] = None) -> None:
        """Newmark integrator - implicit method for transient analysis
        
        Args:
            integrator_type: Must be "Newmark"
            gamma: γ factor for integration
            beta: β factor for integration
            form: Primary variable ('D'=displacement, 'V'=velocity, 'A'=acceleration)
            
        Note:
            Common parameter sets:
            - Average Acceleration: γ=0.5, β=0.25 (unconditionally stable)
            - Linear Acceleration: γ=0.5, β=1/6
            - For β=0 with acceleration unknowns: explicit Central Difference
            - γ > 0.5 introduces numerical damping ∝ (γ - 0.5)
            - Unconditionally stable if β ≥ γ/2 ≥ 0.25
            
        Examples:
            ops.integrator('Newmark', 0.5, 0.25)              # Average acceleration (most common)

            ops.integrator('Newmark', 0.5, 1/6)               # Linear acceleration

            ops.integrator('Newmark', 0.6, 0.3, 'D')          # With damping, displacement form
        """
        ...
    
    @overload
    def integrator(self, integrator_type: Literal["HHT"], alpha: float, gamma: Optional[float] = None, beta: Optional[float] = None) -> None:
        """Hilber-Hughes-Taylor integrator - implicit method with energy dissipation
        
        Args:
            integrator_type: Must be "HHT"
            alpha: α factor (should be between 0.67 and 1.0)
            gamma: γ factor (default: 1.5 - alpha for second-order accuracy)
            beta: β factor (default: (2-alpha)²/4 for unconditional stability)
            
        Note:
            Allows energy dissipation and second-order accuracy. Smaller α = greater damping.
            α = 1.0 corresponds to Newmark method.
            Default values ensure second-order accuracy and unconditional stability.
            
        Examples:
            ops.integrator('HHT', 0.9)                        # Standard HHT with some damping

            ops.integrator('HHT', 0.8, 0.7, 0.4)             # Custom parameters
        """
        ...
    
    @overload
    def integrator(self, integrator_type: Literal["GeneralizedAlpha"], alphaM: float, alphaF: float, gamma: Optional[float] = None, beta: Optional[float] = None) -> None:
        """Generalized Alpha integrator - implicit method with high frequency dissipation
        
        Args:
            integrator_type: Must be "GeneralizedAlpha"
            alphaM: α_M factor for mass matrix
            alphaF: α_F factor for force vector
            gamma: γ factor (default: 0.5 + alphaM - alphaF for second-order accuracy)
            beta: β factor (default: ((1 + alphaM - alphaF)²)/4 for stability)
            
        Note:
            Like HHT, allows high frequency dissipation and second-order accuracy.
            αM = αF = 1.0 gives Newmark method, αM = 1.0 gives HHT method.
            Unconditionally stable if αM ≥ αF ≥ 0.5 and β ≥ 0.25 + 0.5(αM - αF).
            
        Examples:
            ops.integrator('GeneralizedAlpha', 1.0, 0.8)           # Standard generalized-α

            ops.integrator('GeneralizedAlpha', 0.9, 0.8, 0.6, 0.3) # Custom parameters
        """
        ...
    
    @overload
    def integrator(self, integrator_type: Literal["TRBDF2"]) -> None:
        """TRBDF2 integrator - composite scheme alternating between methods
        
        Args:
            integrator_type: Must be "TRBDF2"
            
        Note:
            Composite scheme alternating between Trapezoidal and 3-point backward Euler.
            Attempts to conserve energy and momentum better than Newmark.
            Implementation uses double the time step described in Bathe 2007.
            
        Example:
            ops.integrator('TRBDF2')
        """
        ...
    
    @overload
    def integrator(self, integrator_type: Literal["ExplicitDifference"]) -> None:
        """Explicit Difference integrator - explicit method for transient analysis
        
        Args:
            integrator_type: Must be "ExplicitDifference"
            
        Note:
            Explicit method requiring no matrix factorization. Modal damping preferred over
            Rayleigh damping. No zero elements allowed on mass matrix diagonal.
            Use diagonal solver with lumped mass matrix.
            Stability: Δt ≤ (√(ζ²+1) - ζ) × 2/ω
            
        Example:
            ops.integrator('ExplicitDifference')
        """
        ...
    
    @overload
    def integrator(self, integrator_type: Literal["LoadControl", "DisplacementControl", "ParallelDisplacementControl", "MinUnbalDispNorm", "ArcLength", "CentralDifference", "Newmark", "HHT", "GeneralizedAlpha", "TRBDF2", "ExplicitDifference"], *args: Union[int, float, str]) -> None:
        """Define integrator - determines meaning of terms in system equation Ax=B
        
        Args:
            integrator_type: Type of integrator
            args: Integrator-specific parameters
            
        Available integrator types:
        
        === Static Analysis Integrators ===
            - LoadControl: Classical load control (specify load increment)
            - DisplacementControl: Control displacement at specific DOF
            - ParallelDisplacementControl: Parallel version of displacement control (parallel only)
            - MinUnbalDispNorm: Minimum unbalanced displacement norm method
            - ArcLength: Arc-length control for complete load-displacement curves
            
        === Transient Analysis Integrators ===
            - CentralDifference: Explicit method (stability: Δt/T_n < 1/π)
            - Newmark: Most common implicit method (γ=0.5, β=0.25 recommended)
            - HHT: Implicit with energy dissipation (α between 0.67-1.0)
            - GeneralizedAlpha: High frequency dissipation (αM ≥ αF ≥ 0.5)
            - TRBDF2: Energy/momentum conserving composite scheme
            - ExplicitDifference: Explicit method requiring diagonal mass matrix
            
        Selection guidelines:
            Static analysis:
                - Force-controlled: LoadControl
                - Displacement-controlled: DisplacementControl  
                - Snap-through/post-peak: ArcLength
                - Advanced static: MinUnbalDispNorm
                
            Transient analysis:
                - General purpose: Newmark with γ=0.5, β=0.25
                - High frequency content: HHT or GeneralizedAlpha
                - Fast explicit: CentralDifference or ExplicitDifference
                - Energy conservation: TRBDF2
                
        Stability considerations:
            - Implicit methods: Generally unconditionally stable for linear problems
            - Explicit methods: Conditionally stable (time step limited by smallest element)
            - Newmark: Unconditionally stable if β ≥ γ/2 ≥ 0.25
            - For nonlinear problems: Time step may need reduction regardless of method
            
        Examples:
            # Static analysis

            ops.integrator('LoadControl', 0.1)                                   # Load control

            ops.integrator('DisplacementControl', 1, 1, 0.01)                    # Displacement control

            ops.integrator('ArcLength', 0.1, 1.0)                               # Arc-length
            
            # Transient analysis  

            ops.integrator('Newmark', 0.5, 0.25)                                # Average acceleration

            ops.integrator('HHT', 0.9)                                          # HHT with damping

            ops.integrator('GeneralizedAlpha', 1.0, 0.8)                        # Generalized-α

            ops.integrator('CentralDifference')                                 # Explicit method
        """
        ...
    
    
    # Analysis types
    def analysis(self, analysis_type: Literal["Static", "Transient", "VariableTransient", "PFEM"]) -> None:
        """Define analysis type - constructs Analysis object to determine analysis type
        
        Args:
            analysis_type: Type of analysis to be performed
            
        Available analysis types:
            - Static: For static analysis
            - Transient: For transient analysis with constant time step
            - VariableTransient: For transient analysis with variable time step
            - PFEM: For PFEM (Particle Finite Element Method) analysis
            
        Note:
            If component objects are not defined beforehand, the command automatically creates 
            default component objects and issues warning messages. The number of warnings 
            depends on the number of undefined component objects.
            
        Analysis object functions:
            - Determines predictive step for time t+dt
            - Specifies tangent matrix and residual vector at any iteration
            - Determines corrective step based on displacement increment dU
            
        Examples:
            ops.analysis('Static')           # Static analysis

            ops.analysis('Transient')       # Constant time step transient

            ops.analysis('VariableTransient') # Variable time step transient

            ops.analysis('PFEM')            # PFEM analysis
        """
        ...
    
    # Eigenvalue analysis
    @overload
    def eigen(self, numEigenvalues: int) -> list[float]:
        """Eigenvalue analysis with default solver
        
        Args:
            numEigenvalues: Number of eigenvalues required
            
        Returns:
            List of eigenvalues
            
        Note:
            Uses default '-genBandArpack' solver. Eigenvectors are stored at nodes and can be 
            accessed using Node Recorder, nodeEigenvector command, or Print command.
            
        Example:
            eigenvalues = ops.eigen(5)
        """
        ...
    
    @overload
    def eigen(self, solver: Literal["-genBandArpack"], numEigenvalues: int) -> list[float]:
        """Eigenvalue analysis with genBandArpack solver
        
        Args:
            solver: Must be "-genBandArpack"
            numEigenvalues: Number of eigenvalues required
            
        Returns:
            List of eigenvalues
            
        Note:
            Default solver, able to solve for N-1 eigenvalues where N is number of inertial DOFs.
            
        Example:
            eigenvalues = ops.eigen('-genBandArpack', 10)
        """
        ...
    
    @overload
    def eigen(self, solver: Literal["-fullGenLapack"], numEigenvalues: int) -> list[float]:
        """Eigenvalue analysis with fullGenLapack solver
        
        Args:
            solver: Must be "-fullGenLapack"
            numEigenvalues: Number of eigenvalues required
            
        Returns:
            List of eigenvalues
            
        Warning:
            VERY SLOW for moderate to large models. Use when default Arpack solver 
            runs into N-1 eigenvalue limitation.
            
        Example:
            eigenvalues = ops.eigen('-fullGenLapack', 50)
        """
        ...
    
    @overload
    def eigen(self, *args: Union[str, int]) -> list[float]:
        """Eigenvalue analysis - compute eigenvalues and eigenvectors
        
        Args:
            args: Either (numEigenvalues) or (solver, numEigenvalues)
            
        Parameters:
            numEigenvalues (int): Number of eigenvalues required
            solver (str): Optional solver type
                - '-genBandArpack': Default solver (fast, limited to N-1 eigenvalues)
                - '-fullGenLapack': Full solver (very slow, no eigenvalue limit)
                
        Returns:
            List of eigenvalues in ascending order
            
        Note:
            Eigenvectors are stored at nodes and can be retrieved using:
            - Node Recorder for time history
            - nodeEigenvector command for direct access
            - Print command for output
            
        Solver selection:
            - Default (-genBandArpack): Fast, suitable for most problems
            - Limited to N-1 eigenvalues where N = number of inertial DOFs
            - Use -fullGenLapack when hitting this limitation
            - -fullGenLapack is VERY SLOW for moderate to large models
            
        Examples:
            eigenvalues = ops.eigen(5)                           # 5 modes, default solver
            
            eigenvalues = ops.eigen('-genBandArpack', 10)        # 10 modes, explicit default
            
            eigenvalues = ops.eigen('-fullGenLapack', 50)        # 50 modes, full solver
        """
        ...
    
    # Analysis execution
    @overload
    def analyze(self, numIncr: int) -> int:
        """Perform static analysis
        
        Args:
            numIncr: Number of analysis steps to perform
            
        Returns:
            Analysis status (0=success, <0 if failure)
            
        Note:
            For static analysis, each step applies load increment according to integrator.
            
        Example:
            status = ops.analyze(10)        # 10 load steps
        """
        ...
    
    @overload
    def analyze(self, numIncr: int, dt: float) -> int:
        """Perform transient analysis with constant time step
        
        Args:
            numIncr: Number of analysis steps to perform
            dt: Time-step increment
            
        Returns:
            Analysis status (0=success, <0 if failure)
            
        Note:
            For transient analysis with constant time step.
            Total analysis time = numIncr × dt
            
        Example:
            status = ops.analyze(1000, 0.01)  # 1000 steps of 0.01 time units
        """
        ...
    
    @overload
    def analyze(self, numIncr: int, dt: float, dtMin: float, dtMax: float, Jd: int) -> int:
        """Perform variable transient analysis
        
        Args:
            numIncr: Number of analysis steps to perform
            dt: Initial time-step increment
            dtMin: Minimum time step size
            dtMax: Maximum time step size
            Jd: Desired number of iterations per step for time step adjustment
            
        Returns:
            Analysis status (0=success, <0 if failure)
            
        Note:
            For VariableTransient analysis. Time step is automatically adjusted based on:
            - If convergence takes more iterations than Jd: reduce time step
            - If convergence takes fewer iterations than Jd: increase time step
            - Time step bounded by [dtMin, dtMax]
            
        Example:
            # Variable time step: initial=0.01, range=[0.001, 0.1], target=5 iterations
            status = ops.analyze(500, 0.01, 0.001, 0.1, 5)
        """
        ...
    
    @overload
    def analyze(self) -> int:
        """Perform PFEM analysis
        
        Returns:
            Analysis status (0=success, <0 if failure)
            
        Note:
            For PFEM analysis, no parameters required.
            
        Example:
            status = ops.analyze()          # PFEM analysis
        """
        ...
    
    @overload
    def analyze(self, *args: Union[int, float]) -> int:
        """Perform analysis - execute the analysis procedure
        
        Args:
            args: Analysis parameters depending on analysis type
            
        Parameters:
            For Static analysis:
                numIncr (int): Number of analysis steps
                
            For Transient analysis:
                numIncr (int): Number of analysis steps
                dt (float): Time-step increment
                
            For VariableTransient analysis:
                numIncr (int): Number of analysis steps 
                dt (float): Initial time-step increment
                dtMin (float): Minimum time step
                dtMax (float): Maximum time step
                Jd (int): Desired iterations per step for time step control
                
            For PFEM analysis:
                No parameters required
                
        Returns:
            Analysis status:
                0: Successful completion
                <0: Analysis failure (negative value indicates error type)
                
        Usage by analysis type:
            Static: Each step applies load increment per integrator settings
            Transient: Constant time step integration over specified duration
            VariableTransient: Adaptive time stepping based on convergence behavior
            PFEM: Particle finite element method analysis
            
        Time step control (VariableTransient):
            - Current time step adjusted based on previous step convergence
            - If iterations > Jd: reduce time step (toward dtMin)
            - If iterations < Jd: increase time step (toward dtMax) 
            - Helps maintain computational efficiency while ensuring convergence
            
        Examples:
            # Static analysis

            status = ops.analyze(10)                           # 10 load increments
            
            # Transient analysis

            status = ops.analyze(1000, 0.01)                   # 1000 steps, dt=0.01
            
            # Variable transient analysis

            status = ops.analyze(500, 0.01, 0.001, 0.1, 5)    # Adaptive time stepping
            
            # PFEM analysis

            status = ops.analyze()                             # No parameters needed
            
            # Error handling

            if status < 0:
                print("Analysis failed with error code:", status)
        """
        ...
    
    # Rayleigh damping
    def rayleigh(self, alphaM: float, betaK: float, betaKinit: float = 0.0, betaKcomm: float = 0.0) -> None:
        """Assign Rayleigh damping to all previously-defined elements and nodes
        
        Args:
            alphaM: Factor applied to elements or nodes mass matrix (α_M)
            betaK: Factor applied to elements current stiffness matrix (β_K)
            betaKinit: Factor applied to elements initial stiffness matrix (β_Kinit, default: 0.0)
            betaKcomm: Factor applied to elements committed stiffness matrix (β_Kcomm, default: 0.0)
            
        Damping Matrix Formula:
            D = α_M × M + β_K × K_curr + β_Kinit × K_init + β_Kcomm × K_commit
            
            Where:
            - M: Mass matrix
            - K_curr: Current stiffness matrix
            - K_init: Initial stiffness matrix  
            - K_commit: Committed stiffness matrix
            
        Parameter Selection:
            Classical Rayleigh damping uses only alphaM and betaK:
            D = α_M × M + β_K × K_curr
            
            For specified damping ratios ζ₁, ζ₂ at frequencies ω₁, ω₂:
            α_M = 2 × ζ₁ × ζ₂ × (ω₁ × ω₂) / (ζ₁ × ω₂ + ζ₂ × ω₁)
            β_K = 2 × (ζ₁ × ω₂ + ζ₂ × ω₁) / (ω₁ × ω₂ × (ω₁ + ω₂))
            
        Usage Guidelines:
            - alphaM: Provides damping proportional to mass (affects all frequencies)
            - betaK: Provides damping proportional to current stiffness
            - betaKinit: Uses initial stiffness (before any degradation)
            - betaKcomm: Uses committed stiffness from previous converged state
            
        Common Applications:
            - Classical Rayleigh: Use alphaM and betaK only
            - Nonlinear analysis: Consider betaKinit to avoid stiffness degradation effects
            - Complex systems: Use betaKcomm for stable committed state reference
            
        Examples:
            # Classical Rayleigh damping (2% at first two modes)

            ops.rayleigh(0.1, 0.0002)
            
            # With all four components specified

            ops.rayleigh(0.1, 0.0002, 0.0001, 0.0)
            
            # Using initial stiffness proportional damping

            ops.rayleigh(0.05, 0.0, 0.0003, 0.0)
            
            # Example calculation for 2% damping at 1 Hz and 10 Hz

            # ω₁ = 2π×1 = 6.28 rad/s, ω₂ = 2π×10 = 62.8 rad/s, ζ = 0.02

            # alphaM = 2×0.02×0.02×(6.28×62.8)/(0.02×62.8 + 0.02×6.28) ≈ 0.057

            # betaK = 2×(0.02×62.8 + 0.02×6.28)/(6.28×62.8×(6.28+62.8)) ≈ 0.00014

                         ops.rayleigh(0.057, 0.00014)
        """
        ...
    
    @overload
    def modalProperties(self, option: Literal["-print"]) -> None:
        """Compute modal properties with console output
        
        Args:
            option: Must be "-print" to output report to console
            
        Example:
            ops.modalProperties('-print')
        """
        ...
    
    @overload
    def modalProperties(self, file_option: Literal["-file"], reportFileName: str) -> None:
        """Compute modal properties with file output
        
        Args:
            file_option: Must be "-file" 
            reportFileName: Filename for the report (created/overwritten)
            
        Example:
            ops.modalProperties('-file', 'modal_report.txt')
        """
        ...
    
    @overload
    def modalProperties(self, option: Literal["-unorm"]) -> None:
        """Compute modal properties using displacement-normalized eigenvectors
        
        Args:
            option: Must be "-unorm" for displacement normalization
            
        Note:
            By default uses mass-normalized eigenvectors. Use -unorm for 
            displacement-normalized version where largest component equals 1.
            
        Example:
            ops.modalProperties('-unorm')
        """
        ...
    
    @overload
    def modalProperties(self, option: Literal["-return"]) -> ModalPropertiesResult:
        """Compute modal properties and return results as dictionary
        
        Args:
            option: Must be "-return" to return dictionary
            
        Returns:
            Dictionary containing all modal properties results
            
        Example:
            props = ops.modalProperties('-return')

            periods = props['eigenPeriod']
        """
        ...
    
    @overload
    def modalProperties(self, *options: Union[str]) -> Optional[ModalPropertiesResult]:
        """Compute modal properties of model after eigen analysis
        
        Args:
            options: Optional flags that can be combined in any order
            
        Available options:
            '-print': Print report to console
            '-file' <filename>: Print report to file (filename must follow -file)
            '-unorm': Use displacement-normalized eigenvectors instead of mass-normalized
            '-return': Return results as dictionary (available in version 3.4.0.3+)
            
        Returns:
            ModalPropertiesResult dictionary if '-return' is used, None otherwise
            
        Modal Properties Computed:
            - domainSize: Model dimensionality
            - eigenLambda/Omega/Frequency/Period: Eigenvalue analysis results
            - totalMass: Total mass for each DOF (free + fixed)
            - totalFreeMass: Total mass for free DOFs only
            - centerOfMass: Mass center coordinates
            - partiFactorXX: Modal participation factors
            - partiMassXX: Modal participation masses
            - partiMassesCumuXX: Cumulative modal participation masses
            - partiMassRatiosXX: Modal participation mass ratios (%)
            - partiMassRatiosCumuXX: Cumulative mass ratios (%)
            
        DOF Notation:
            1D problems: MX
            2D problems: MX, MY, RMZ  
            3D problems: MX, MY, MZ, RMX, RMY, RMZ
            
        Usage Notes:
            - Must call eigen command first
            - Accounts for both nodal and element (distributed) masses
            - Works with lumped or consistent element mass matrices
            - Supports 2D (ndm=2, ndf=2/3) and 3D (ndm=3, ndf=3/4/6) problems
            - Computes rotational masses from both direct input and gyration effects
            - Default eigenvector normalization depends on eigen solver:
              * -genBandArpack: mass-normalized (generalized mass = identity)
              * -fullGenLapack: displacement-normalized (max component = 1)
            - Use -unorm to force displacement normalization with -genBandArpack
            
        Examples:
            # Basic computation

            ops.modalProperties()
            
            # With console output

            ops.modalProperties('-print')
            
            # Save to file

            ops.modalProperties('-file', 'modal_analysis.txt')
            
            # Use displacement normalization

            ops.modalProperties('-unorm')

            
            # Return results as dictionary

            results = ops.modalProperties('-return')

            periods = results['eigenPeriod']

            factors_x = results['partiFactorMX']
            
            # Combine options

            ops.modalProperties('-print', '-unorm')

            ops.modalProperties('-file', 'report.txt', '-unorm')
            
            # Full analysis with return

            props = ops.modalProperties('-print', '-file', 'detailed.txt', '-return')

            if props:
                print(f"First period: {props['eigenPeriod'][0]:.3f} s")
        """
        ...
    
    # Response spectrum analysis
    @overload
    def responseSpectrumAnalysis(self, tsTag: int, direction: int) -> None:
        """Response spectrum analysis using time series for spectrum definition
        
        Args:
            tsTag: Tag of previously defined timeSeries with Tn/Sa values
            direction: 1-based index of excited DOF (1-3 for 2D, 1-6 for 3D)
            
        Example:
            ops.responseSpectrumAnalysis(1, 1)  # Use timeSeries 1, excite X-direction
        """
        ...
    
    @overload
    def responseSpectrumAnalysis(self, tsTag: int, direction: int, scale_option: Literal["-scale"], scale: float) -> None:
        """Response spectrum analysis with time series and scale factor
        
        Args:
            tsTag: Tag of previously defined timeSeries with Tn/Sa values
            direction: 1-based index of excited DOF
            scale_option: Must be "-scale"
            scale: Scale factor for modal displacements (future implementation)
            
        Example:
            ops.responseSpectrumAnalysis(1, 1, '-scale', 1.0)
        """
        ...
    
    @overload
    def responseSpectrumAnalysis(self, tsTag: int, direction: int, mode_option: Literal["-mode"], mode: int) -> None:
        """Response spectrum analysis for single mode using time series
        
        Args:
            tsTag: Tag of previously defined timeSeries with Tn/Sa values
            direction: 1-based index of excited DOF
            mode_option: Must be "-mode"
            mode: 1-based index of mode to process
            
        Example:
            ops.responseSpectrumAnalysis(1, 1, '-mode', 3)  # Process only mode 3
        """
        ...
    
    @overload
    def responseSpectrumAnalysis(self, direction: int, tn_option: Literal["-Tn"], Tn: list[float], sa_option: Literal["-Sa"], Sa: list[float]) -> None:
        """Response spectrum analysis using period and acceleration lists
        
        Args:
            direction: 1-based index of excited DOF (1-3 for 2D, 1-6 for 3D)
            tn_option: Must be "-Tn"
            Tn: List of periods for response spectrum function
            sa_option: Must be "-Sa" 
            Sa: List of accelerations for response spectrum function
            
        Example:
            periods = [0.1, 0.2, 0.5, 1.0, 2.0]

            accels = [0.8, 1.0, 0.6, 0.4, 0.2]

            ops.responseSpectrumAnalysis(1, '-Tn', periods, '-Sa', accels)
        """
        ...
    
    @overload
    def responseSpectrumAnalysis(self, *args: Union[int, str, float, list[float]]) -> None:
        """Response spectrum analysis - perform modal response spectrum analysis
        
        Args:
            args: Analysis parameters in two possible formats
            
        Format 1 - Using TimeSeries:
            tsTag (int): Tag of previously defined timeSeries with Tn/Sa values
            direction (int): 1-based index of excited DOF
            Optional: '-scale', scale (float) - scale factor (future use)
            Optional: '-mode', mode (int) - process single mode only
            
        Format 2 - Using Lists:
            direction (int): 1-based index of excited DOF
            '-Tn', Tn (list[float]): Periods of response spectrum function
            '-Sa', Sa (list[float]): Accelerations of response spectrum function
            Optional: '-scale', scale (float) - scale factor (future use)
            Optional: '-mode', mode (int) - process single mode only
            
        Direction Mapping:
            2D problems (ndm=2): 1=X, 2=Y, 3=RZ
            3D problems (ndm=3): 1=X, 2=Y, 3=Z, 4=RX, 5=RY, 6=RZ
            
        Prerequisites:
            1. Must call eigen command first
            2. Must call modalProperties command first
            
        Analysis Process:
            - Performs N linear analysis steps (N = number of eigenvalues)
            - Computes modal displacements for each mode
            - Calls all defined recorders after each step
            - Modal combination is user's responsibility via Python scripting
            
        Scale Factor (Future Implementation):
            - Currently placeholder, not functional
            - Intended for nonlinear models as linear perturbation
            - Will allow very small modal displacements that don't alter nonlinear state
            
        Examples:
            # Using timeSeries (basic)

            ops.responseSpectrumAnalysis(1, 1)                    # TimeSeries 1, X-direction
            
            # Using timeSeries with options

            ops.responseSpectrumAnalysis(1, 2, '-mode', 3)        # TimeSeries 1, Y-dir, mode 3

            ops.responseSpectrumAnalysis(1, 1, '-scale', 1.0)     # With scale factor
            
            # Using period/acceleration lists

            periods = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0]

            accels = [0.8, 1.2, 1.0, 0.6, 0.4, 0.2]

            ops.responseSpectrumAnalysis(1, '-Tn', periods, '-Sa', accels)
            
            # Lists with single mode

            ops.responseSpectrumAnalysis(1, '-Tn', periods, '-Sa', accels, '-mode', 2)
            
            # Complete workflow example

            # 1. Eigenvalue analysis

            eigenvals = ops.eigen(10)
            
            # 2. Modal properties

            props = ops.modalProperties('-return')
            
            # 3. Response spectrum analysis  

            periods = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0]

            spectrum = [1.0, 1.5, 1.8, 1.2, 0.8, 0.4]

            ops.responseSpectrumAnalysis(1, '-Tn', periods, '-Sa', spectrum)
            
            # Modal combination would be done in Python:

            # modal_responses = [recorded results for each mode]

            # srss_response = sqrt(sum(r**2 for r in modal_responses))
        """
        ... 

        