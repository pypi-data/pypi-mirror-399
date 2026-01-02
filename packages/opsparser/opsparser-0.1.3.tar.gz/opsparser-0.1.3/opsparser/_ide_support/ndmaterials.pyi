"""nD Material commands type annotations"""

from typing import overload, Literal, Optional, Any, List

class nDMaterialCommands:
    """Type annotations for nD material commands"""
    
    # === nD Material Commands ===
    
    @overload
    def nDMaterial(self, material_type: Literal["ElasticIsotropic"], matTag: int, E: float, nu: float, rho: float = 0.0) -> None:
        """Define elastic isotropic material
        
        Args:
            material_type: Material type 'ElasticIsotropic'
            matTag: Material tag identifier
            E: Elastic modulus
            nu: Poisson's ratio
            rho: Mass density (optional, default=0.0)
            
        Valid formulations:
            - 'ThreeDimensional'
            - 'PlaneStrain'
            - 'Plane Stress'
            - 'AxiSymmetric'
            - 'PlateFiber'
            
        Example:
            ops.nDMaterial('ElasticIsotropic', 1, 29000.0, 0.3)
            ops.nDMaterial('ElasticIsotropic', 2, 29000.0, 0.3, 2.4e-4)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["ElasticOrthotropic"], matTag: int, Ex: float, Ey: float, Ez: float, nu_xy: float, nu_yz: float, nu_zx: float, Gxy: float, Gyz: float, Gzx: float, rho: float = 0.0) -> None:
        """Define elastic orthotropic material
        
        Args:
            material_type: Material type 'ElasticOrthotropic'
            matTag: Material tag identifier
            Ex: Elastic modulus in x direction
            Ey: Elastic modulus in y direction
            Ez: Elastic modulus in z direction
            nu_xy: Poisson's ratio in xy plane
            nu_yz: Poisson's ratio in yz plane
            nu_zx: Poisson's ratio in zx plane
            Gxy: Shear modulus in xy plane
            Gyz: Shear modulus in yz plane
            Gzx: Shear modulus in zx plane
            rho: Mass density (optional, default=0.0)
            
        Valid formulations:
            - 'ThreeDimensional'
            - 'PlaneStrain'
            - 'Plane Stress'
            - 'AxiSymmetric'
            - 'BeamFiber'
            - 'PlateFiber'
            
        Example:
            ops.nDMaterial('ElasticOrthotropic', 1, 30000, 15000, 15000, 0.3, 0.2, 0.2, 5000, 3000, 3000)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["J2Plasticity"], matTag: int, K: float, G: float, sig0: float, sigInf: float, delta: float, H: float) -> None:
        """Define J2 plasticity material (von Mises yield criterion)
        
        Args:
            material_type: Material type 'J2Plasticity'
            matTag: Material tag identifier
            K: Bulk modulus
            G: Shear modulus
            sig0: Initial yield stress
            sigInf: Final saturation yield stress
            delta: Exponential hardening parameter
            H: Linear hardening parameter
            
        Valid formulations:
            - 'ThreeDimensional'
            - 'PlaneStrain'
            - 'Plane Stress'
            - 'AxiSymmetric'
            - 'PlateFiber'
            
        Example:
            ops.nDMaterial('J2Plasticity', 1, 166667, 80000, 250, 500, 16.67, 1000)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["DruckerPrager"], matTag: int, K: float, G: float, sigmaY: float, rho: float, rhoBar: float, Kinf: float, Ko: float, delta1: float, delta2: float, H: float, theta: float, density: float, atmPressure: float = 101e3) -> None:
        """Define Drucker-Prager material
        
        Args:
            material_type: Material type 'DruckerPrager'
            matTag: Material tag identifier
            K: Bulk modulus
            G: Shear modulus
            sigmaY: Yield stress
            rho: Frictional strength parameter
            rhoBar: Controls evolution of plastic volume change
            Kinf: Nonlinear isotropic strain hardening parameter
            Ko: Nonlinear isotropic strain hardening parameter
            delta1: Nonlinear isotropic strain hardening parameter
            delta2: Tension softening parameter
            H: Linear hardening parameter
            theta: Controls relative proportions of isotropic and kinematic hardening
            density: Material mass density
            atmPressure: Atmospheric pressure for update of elastic bulk and shear moduli (optional, default=101e3)
            
        Valid formulations:
            - 'ThreeDimensional'
            - 'PlaneStrain'
            
        Example:
            ops.nDMaterial('DruckerPrager', 1, 166667, 80000, 100, 0.3, 0.1, 1000, 100, 1.0, 0.1, 1000, 0.5, 2.0e-4)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["PlaneStress"], matTag: int, mat3DTag: int) -> None:
        """Define plane stress material wrapper
        
        Args:
            material_type: Material type 'PlaneStress'
            matTag: Material tag identifier
            mat3DTag: Tag of previously defined 3D nDMaterial
            
        Valid formulations:
            - 'Plane Stress'
            
        Example:
            ops.nDMaterial('PlaneStress', 1, 10)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["PlaneStrain"], matTag: int, mat3DTag: int) -> None:
        """Define plane strain material wrapper
        
        Args:
            material_type: Material type 'PlaneStrain'
            matTag: Material tag identifier
            mat3DTag: Tag of previously defined 3D nDMaterial
            
        Valid formulations:
            - 'PlaneStrain'
            
        Example:
            ops.nDMaterial('PlaneStrain', 1, 10)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["MultiaxialCyclicPlasticity"], matTag: int, rho: float, K: float, G: float, Su: float, Ho: float, h: float, m: float, beta: float, KCoeff: float) -> None:
        """Define multiaxial cyclic plasticity material for clays
        
        Args:
            material_type: Material type 'MultiaxialCyclicPlasticity'
            matTag: Material tag identifier
            rho: Density
            K: Bulk modulus
            G: Maximum (small strain) shear modulus
            Su: Undrained shear strength, size of bounding surface
            Ho: Linear kinematic hardening modulus of bounding surface
            h: Hardening parameter
            m: Hardening parameter
            beta: Integration parameter, usually beta=0.5
            KCoeff: Coefficient of earth pressure, K0
            
        Example:
            ops.nDMaterial('MultiaxialCyclicPlasticity', 1, 1.8e-4, 100000, 40000, 50, 2000, 0.01, 1.0, 0.5, 0.5)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["BoundingCamClay"], matTag: int, massDensity: float, C: float, bulkMod: float, OCR: float, mu_o: float, alpha: float, lambda_: float, h: float, m: float) -> None:
        """Define bounding surface Cam Clay material
        
        Args:
            material_type: Material type 'BoundingCamClay'
            matTag: Material tag identifier
            massDensity: Mass density
            C: Ellipsoidal axis ratio (defines shape of ellipsoidal loading/bounding surfaces)
            bulkMod: Initial bulk modulus
            OCR: Overconsolidation ratio
            mu_o: Initial shear modulus
            alpha: Pressure-dependency parameter for moduli (greater than or equal to zero)
            lambda_: Soil compressibility index for virgin loading
            h: Hardening parameter for plastic response inside of bounding surface (if h=0, no hardening)
            m: Hardening parameter (exponent) for plastic response inside of bounding surface (if m=0, only linear hardening)
            
        Valid formulations:
            - 'ThreeDimensional'
            - 'PlaneStrain'
            
        Example:
            ops.nDMaterial('BoundingCamClay', 1, 1.8e-4, 0.8, 200000, 2.0, 40000, 0.25, 0.19, 0.01, 1.0)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["PlateFiber"], matTag: int, threeDTag: int) -> None:
        """Define plate fiber material wrapper
        
        Args:
            material_type: Material type 'PlateFiber'
            matTag: Material tag identifier
            threeDTag: Material tag for a previously-defined three-dimensional material
            
        Example:
            ops.nDMaterial('PlateFiber', 1, 10)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["FSAM"], matTag: int, rho: float, sXTag: int, sYTag: int, concTag: int, rouX: float, rouY: float, nu: float, alfadow: float) -> None:
        """Define FSAM material (Fixed-Strut-Angle-Model)
        
        Args:
            material_type: Material type 'FSAM'
            matTag: Material tag identifier
            rho: Material density
            sXTag: Tag of uniaxialMaterial simulating horizontal (x) reinforcement
            sYTag: Tag of uniaxialMaterial simulating vertical (y) reinforcement
            concTag: Tag of uniaxialMaterial simulating concrete, shall be used with uniaxialMaterial ConcreteCM
            rouX: Reinforcing ratio in horizontal (x) direction (rouX = As,x/Agross,x)
            rouY: Reinforcing ratio in vertical (y) direction (rouY = As,y/Agross,y)
            nu: Concrete friction coefficient (0.0 < nu < 1.5)
            alfadow: Stiffness coefficient of reinforcement dowel action (0.0 < alfadow < 0.05)
            
        Example:
            ops.nDMaterial('FSAM', 1, 2.4e-4, 2, 3, 4, 0.001, 0.001, 0.3, 0.01)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["ManzariDafalias"], matTag: int, G0: float, nu: float, e_init: float, Mc: float, c: float, lambda_c: float, e0: float, ksi: float, P_atm: float, m: float, h0: float, ch: float, nb: float, A0: float, nd: float, z_max: float, cz: float, Den: float) -> None:
        """Define Manzari-Dafalias material model
        
        Args:
            material_type: Material type 'ManzariDafalias'
            matTag: Material tag identifier
            G0: Shear modulus constant
            nu: Poisson ratio
            e_init: Initial void ratio
            Mc: Critical state stress ratio
            c: Ratio of critical state stress ratio in extension and compression
            lambda_c: Critical state line constant
            e0: Critical void ratio at p=0
            ksi: Critical state line constant
            P_atm: Atmospheric pressure
            m: Yield surface constant (radius of yield surface in stress ratio space)
            h0: Constant parameter
            ch: Constant parameter
            nb: Bounding surface parameter
            A0: Dilatancy parameter
            nd: Dilatancy surface parameter
            z_max: Fabric-dilatancy tensor parameter
            cz: Fabric-dilatancy tensor parameter
            Den: Mass density of the material
            
        Example:
            ops.nDMaterial('ManzariDafalias', 1, 125, 0.05, 0.934, 1.25, 0.712, 0.019, 0.934, 0.7, 101, 0.01, 7.05, 0.968, 1.1, 2.64, 3.5, 4.0, 600, 1.42e-4)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["PM4Sand"], matTag: int, D_r: float, G_o: float, h_po: float, Den: float, P_atm: float = 101.0, h_o: float = 0.5, e_max: float = 0.8, e_min: float = 0.5, n_b: float = 0.5, n_d: float = 0.1, A_do: float = -1.0, z_max: float = -1.0, c_z: float = 250.0, c_e: float = -1.0, phi_cv: float = 33.0, nu: float = 0.3, g_degr: float = -1.0, c_dr: float = -1.0, c_kaf: float = -1.0, Q_bolt: float = 10.0, R_bolt: float = 1.5, m_par: float = 0.01, F_sed: float = 0.04, p_sed: float = 2.0) -> None:
        """Define PM4Sand material model
        
        Args:
            material_type: Material type 'PM4Sand'
            matTag: Material tag identifier
            D_r: Relative density, in fraction
            G_o: Shear modulus constant
            h_po: Contraction rate parameter
            Den: Mass density of the material
            P_atm: Atmospheric pressure (optional, default=101.0)
            h_o: Variable that adjusts the ratio of plastic modulus to elastic modulus (optional, default=0.5)
            e_max: Maximum void ratio (optional, default=0.8)
            e_min: Minimum void ratio (optional, default=0.5)
            n_b: Bounding surface parameter (optional, default=0.5)
            n_d: Dilatancy surface parameter (optional, default=0.1)
            A_do: Dilatancy parameter, will be computed at initialization if input value is negative (optional, default=-1.0)
            z_max: Fabric-dilatancy tensor parameter (optional, default=-1.0)
            c_z: Fabric-dilatancy tensor parameter (optional, default=250.0)
            c_e: Variable that adjusts the rate of strain accumulation in cyclic loading (optional, default=-1.0)
            phi_cv: Critical state effective friction angle (optional, default=33.0)
            nu: Poisson's ratio (optional, default=0.3)
            g_degr: Variable that adjusts degradation of elastic modulus with accumulation of fabric (optional, default=-1.0)
            c_dr: Variable that controls the rotated dilatancy surface (optional, default=-1.0)
            c_kaf: Variable that controls the effect that sustained static shear stresses have on plastic modulus (optional, default=-1.0)
            Q_bolt: Critical state line parameter (optional, default=10.0)
            R_bolt: Critical state line parameter (optional, default=1.5)
            m_par: Yield surface constant (radius of yield surface in stress ratio space) (optional, default=0.01)
            F_sed: Variable that controls the minimum value the reduction factor of the elastic moduli can get during reconsolidation (optional, default=0.04)
            p_sed: Mean effective stress up to which reconsolidation strains are enhanced (optional, default=2.0)
            
        Valid formulations:
            - 'PlaneStrain'
            
        Example:
            ops.nDMaterial('PM4Sand', 1, 0.65, 476, 0.53, 1.42e-4)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["PM4Silt"], matTag: int, S_u: float, Su_Rat: float, G_o: float, h_po: float, Den: float, Su_factor: float = 1.0, Patm: float = 101.0, nu: float = 0.3, nG: float = 0.75, h0: float = 0.5, eInit: float = 0.90, lambda_: float = 0.060, phicv: float = 32.0, nb_wet: float = 0.8, nb_dry: float = 0.5, nd: float = 0.3, Ado: float = 0.8, ru_max: float = 0.95, zmax: float = 20.0, cz: float = 100.0, ce: float = 0.1, Cgd: float = 3.0, ckaf: float = 4.0, m_m: float = 0.01, CG_consol: float = 2.0) -> None:
        """Define PM4Silt material model
        
        Args:
            material_type: Material type 'PM4Silt'
            matTag: Material tag identifier
            S_u: Undrained shear strength
            Su_Rat: Undrained shear strength ratio
            G_o: Shear modulus constant
            h_po: Contraction rate parameter
            Den: Mass density of the material
            Su_factor: Undrained shear strength reduction factor (optional, default=1.0)
            Patm: Atmospheric pressure (optional, default=101.0)
            nu: Poisson's ratio (optional, default=0.3)
            nG: Shear modulus exponent (optional, default=0.75)
            h0: Variable that adjusts the ratio of plastic modulus to elastic modulus (optional, default=0.5)
            eInit: Initial void ratio (optional, default=0.90)
            lambda_: The slope of critical state line in e-ln(p) space (optional, default=0.060)
            phicv: Critical state effective friction angle (optional, default=32.0)
            nb_wet: Bounding surface parameter for loose of critical state conditions (optional, default=0.8)
            nb_dry: Bounding surface parameter for dense of critical state conditions (optional, default=0.5)
            nd: Dilatancy surface parameter (optional, default=0.3)
            Ado: Dilatancy parameter (optional, default=0.8)
            ru_max: Maximum pore pressure ratio based on p' (optional, default=0.95)
            zmax: Fabric-dilatancy tensor parameter (optional, default=20.0)
            cz: Fabric-dilatancy tensor parameter (optional, default=100.0)
            ce: Variable that adjusts the rate of strain accumulation in cyclic loading (optional, default=0.1)
            Cgd: Variable that adjusts degradation of elastic modulus with accumulation of fabric (optional, default=3.0)
            ckaf: Variable that controls the effect that sustained static shear stresses have on plastic modulus (optional, default=4.0)
            m_m: Yield surface constant (radius of yield surface in stress ratio space) (optional, default=0.01)
            CG_consol: Reduction factor of elastic modulus for reconsolidation (optional, default=2.0)
            
        Example:
            ops.nDMaterial('PM4Silt', 1, 50.0, 0.3, 400.0, 0.8, 1.8e-4)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["stressDensity"], matTag: int, mDen: float, eNot: float, A: float, n: float, nu: float, a1: float, b1: float, a2: float, b2: float, a3: float, b3: float, fd: float, muNot: float, muCyc: float, sc: float, M: float, patm: float, ssls: List[float] = [0.877, 0.877, 0.873, 0.870, 0.860, 0.850, 0.833], hsl: float = 0.895, p1: float = 1.0) -> None:
        """Define stress density material model for sand behavior
        
        Args:
            material_type: Material type 'stressDensity'
            matTag: Material tag identifier
            mDen: Mass density
            eNot: Initial void ratio
            A: Constant for elastic shear modulus
            n: Pressure dependency exponent for elastic shear modulus
            nu: Poisson's ratio
            a1: Peak stress ratio coefficient (etaMax = a1 + b1*Is)
            b1: Peak stress ratio coefficient (etaMax = a1 + b1*Is)
            a2: Max shear modulus coefficient (Gn_max = a2 + b2*Is)
            b2: Max shear modulus coefficient (Gn_max = a2 + b2*Is)
            a3: Min shear modulus coefficient (Gn_min = a3 + b3*Is)
            b3: Min shear modulus coefficient (Gn_min = a3 + b3*Is)
            fd: Degradation constant
            muNot: Dilatancy coefficient (monotonic loading)
            muCyc: Dilatancy coefficient (cyclic loading)
            sc: Dilatancy strain
            M: Critical state stress ratio
            patm: Atmospheric pressure (in appropriate units)
            ssls: Void ratio of quasi steady state (QSS-line) at pressures [pmin, 10kPa, 30kPa, 50kPa, 100kPa, 200kPa, 400kPa] (optional)
            hsl: Void ratio of upper reference state (UR-line) for all pressures (optional, default=0.895)
            p1: Pressure corresponding to ssl1 (optional, default=1.0 kPa)
            
        Valid formulations:
            - 'ThreeDimensional'
            - 'PlaneStrain'
            
        Example:
            ops.nDMaterial('stressDensity', 1, 1.7, 0.7, 100, 0.5, 0.3, 0.704, 0.041, 150, 0.0, 20, 0.0, 0.15, 0.21, 0.07, 0.008, 1.25, 101)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["AcousticMedium"], matTag: int, K: float, rho: float) -> None:
        """Define acoustic medium nD material
        
        Args:
            material_type: Material type 'AcousticMedium'
            matTag: Material tag identifier
            K: Bulk modulus of the acoustic medium
            rho: Mass density of the acoustic medium
            
        Example:
            ops.nDMaterial('AcousticMedium', 1, 2.2e9, 1000.0)
        """
        ...

    # === Tsinghua Sand Models ===
    @overload
    def nDMaterial(self, material_type: Literal["CycLiqCP"], matTag: int, G0: float, kappa: float, h: float, Mfc: float, dre1: float, Mdc: float, dre2: float, rdr: float, alpha: float, dir: float, ein: float, rho: float) -> None:
        """Define CycLiqCP material for large post-liquefaction deformation
        
        Args:
            material_type: Material type 'CycLiqCP'
            matTag: Material tag identifier
            G0: A constant related to elastic shear modulus
            kappa: Bulk modulus
            h: Model parameter for plastic modulus
            Mfc: Stress ratio at failure in triaxial compression
            dre1: Coefficient for reversible dilatancy generation
            Mdc: Stress ratio at which the reversible dilatancy sign changes
            dre2: Coefficient for reversible dilatancy release
            rdr: Reference shear strain length
            alpha: Parameter controlling the decrease rate of irreversible dilatancy
            dir: Coefficient for irreversible dilatancy potential
            ein: Initial void ratio
            rho: Saturated mass density
            
        Valid formulations:
            - 'ThreeDimensional'
            - 'PlaneStrain'
            
        Example:
            ops.nDMaterial('CycLiqCP', 1, 75, 2e5, 0.9, 1.25, 2.0, 1.25, -2.0, 0.01, 0.6, 0.9, 0.8, 1.8e-4)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["CycLiqCPSP"], matTag: int, G0: float, kappa: float, h: float, M: float, dre1: float, dre2: float, rdr: float, alpha: float, dir: float, lambdac: float, ksi: float, e0: float, np: float, nd: float, ein: float, rho: float) -> None:
        """Define CycLiqCPSP material for large post-liquefaction deformation with critical state
        
        Args:
            material_type: Material type 'CycLiqCPSP'
            matTag: Material tag identifier
            G0: A constant related to elastic shear modulus
            kappa: Bulk modulus
            h: Model parameter for plastic modulus
            M: Critical state stress ratio
            dre1: Coefficient for reversible dilatancy generation
            dre2: Coefficient for reversible dilatancy release
            rdr: Reference shear strain length
            alpha: Parameter controlling the decrease rate of irreversible dilatancy
            dir: Coefficient for irreversible dilatancy potential
            lambdac: Critical state constant
            ksi: Critical state constant
            e0: Void ratio at pc=0
            np: Material constant for peak mobilized stress ratio
            nd: Material constant for reversible dilatancy generation stress ratio
            ein: Initial void ratio
            rho: Saturated mass density
            
        Valid formulations:
            - 'ThreeDimensional'
            - 'PlaneStrain'
            
        Example:
            ops.nDMaterial('CycLiqCPSP', 1, 75, 2e5, 0.9, 1.25, 2.0, -2.0, 0.01, 0.6, 0.9, 0.025, 0.7, 0.9, 4.0, 0.0, 0.8, 1.8e-4)
        """
        ...

    # === Contact Materials ===
    @overload
    def nDMaterial(self, material_type: Literal["ContactMaterial2D"], matTag: int, mu: float, G: float, c: float, t: float) -> None:
        """Define 2D contact material with frictional interface behavior
        
        Args:
            material_type: Material type 'ContactMaterial2D'
            matTag: Material tag identifier
            mu: Interface frictional coefficient
            G: Interface stiffness parameter
            c: Interface cohesive intercept
            t: Interface tensile strength
            
        Note:
            Works with SimpleContact2D and BeamContact2D element objects.
            Uses regularized Coulomb frictional law for sticking, slip, and separation.
            
        Example:
            ops.nDMaterial('ContactMaterial2D', 1, 0.3, 1e6, 0.0, 0.0)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["ContactMaterial3D"], matTag: int, mu: float, G: float, c: float, t: float) -> None:
        """Define 3D contact material with frictional interface behavior
        
        Args:
            material_type: Material type 'ContactMaterial3D'
            matTag: Material tag identifier
            mu: Interface frictional coefficient
            G: Interface stiffness parameter
            c: Interface cohesive intercept
            t: Interface tensile strength
            
        Note:
            Works with SimpleContact3D and BeamContact3D element objects.
            Uses regularized Coulomb frictional law for sticking, slip, and separation.
            
        Example:
            ops.nDMaterial('ContactMaterial3D', 1, 0.3, 1e6, 0.0, 0.0)
        """
        ...

    # === Concrete Wall Materials ===
    @overload
    def nDMaterial(self, material_type: Literal["PlateFromPlaneStress"], matTag: int, pre_def_matTag: int, OutofPlaneModulus: float) -> None:
        """Define multi-dimensional concrete material from plane stress material
        
        Args:
            material_type: Material type 'PlateFromPlaneStress'
            matTag: New material tag identifier deriving from pre-defined PlaneStress material
            pre_def_matTag: Tag of previously defined PlaneStress material
            OutofPlaneModulus: Shear modulus for out of plane stresses
            
        Example:
            ops.nDMaterial('PlateFromPlaneStress', 1, 10, 1e6)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["PlateRebar"], matTag: int, pre_def_matTag: int, sita: float) -> None:
        """Define multi-dimensional reinforcement material
        
        Args:
            material_type: Material type 'PlateRebar'
            matTag: New material tag identifier deriving from pre-defined uniaxial material
            pre_def_matTag: Tag of previously defined uniaxial material
            sita: Angle of reinforcement layer in degrees (90=longitudinal, 0=transverse)
            
        Example:
            ops.nDMaterial('PlateRebar', 1, 10, 90.0)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["PlasticDamageConcretePlaneStress"], matTag: int, E: float, nu: float, ft: float, fc: float, beta: Optional[float] = None, Ap: Optional[float] = None, An: Optional[float] = None, Bn: Optional[float] = None) -> None:
        """Define plastic damage concrete plane stress material
        
        Args:
            material_type: Material type 'PlasticDamageConcretePlaneStress'
            matTag: Material tag identifier
            E: Elastic modulus
            nu: Poisson's ratio
            ft: Tensile strength
            fc: Compressive strength
            beta: Optional parameter (default=None)
            Ap: Optional parameter (default=None)
            An: Optional parameter (default=None)
            Bn: Optional parameter (default=None)
            
        Example:
            ops.nDMaterial('PlasticDamageConcretePlaneStress', 1, 30000, 0.2, 3.0, 30.0)
        """
        ...

    # === Initial State Analysis Materials ===
    @overload
    def nDMaterial(self, material_type: Literal["InitialStateAnalysisWrapper"], matTag: int, nDMatTag: int, nDim: int) -> None:
        """Define initial state analysis wrapper material
        
        Args:
            material_type: Material type 'InitialStateAnalysisWrapper'
            matTag: Material tag identifier
            nDMatTag: Tag of the associated nDMaterial object
            nDim: Number of dimensions (2 for 2D, 3 for 3D)
            
        Note:
            Allows use of InitialStateAnalysis command for setting initial conditions.
            Can be used with any nDMaterial to develop initial stress field while maintaining original geometry.
            No valid recorder queries available for this wrapper.
            
        Example:
            ops.nDMaterial('InitialStateAnalysisWrapper', 1, 10, 2)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["InitStressNDMaterial"], matTag: int, otherTag: int, initStress: float, nDim: int) -> None:
        """Define initial stress material wrapper
        
        Args:
            material_type: Material type 'InitStressNDMaterial'
            matTag: Material tag identifier
            otherTag: Tag of the other material
            initStress: Initial stress
            nDim: Number of dimensions (e.g. if plane strain nDim=2)
            
        Note:
            Stress-strain behavior defined by another material.
            Strain corresponding to initial stress calculated from other material.
            
        Example:
            ops.nDMaterial('InitStressNDMaterial', 1, 10, 100.0, 2)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["InitStrainNDMaterial"], matTag: int, otherTag: int, initStrain: float, nDim: int) -> None:
        """Define initial strain material wrapper
        
        Args:
            material_type: Material type 'InitStrainNDMaterial'
            matTag: Material tag identifier
            otherTag: Tag of the other material
            initStrain: Initial strain
            nDim: Number of dimensions
            
        Note:
            Stress-strain behavior defined by another material.
            Stress corresponding to initial strain calculated from other material.
            
        Example:
            ops.nDMaterial('InitStrainNDMaterial', 1, 10, 0.001, 2)
        """
        ...

    # === UC San Diego Models ===
    @overload
    def nDMaterial(self, material_type: Literal["PressureIndependMultiYield"], matTag: int, nd: float, rho: float, refShearModul: float, refBulkModul: float, cohesi: float, peakShearStra: float, frictionAng: float = 0.0, refPress: float = 100.0, pressDependCoe: float = 0.0, noYieldSurf: float = 20.0, yieldSurf: Optional[List[float]] = None) -> None:
        """Define pressure independent multi-yield material for organic soils or clay under undrained conditions
        
        Args:
            material_type: Material type 'PressureIndependMultiYield'
            matTag: Material tag identifier
            nd: Number of dimensions (2 for plane-strain, 3 for 3D analysis)
            rho: Saturated soil mass density
            refShearModul: Reference low-strain shear modulus Gr, specified at reference mean effective confining pressure
            refBulkModul: Reference bulk modulus Br, specified at reference mean effective confining pressure
            cohesi: Apparent cohesion at zero effective confinement
            peakShearStra: Octahedral shear strain at which maximum shear strength is reached
            frictionAng: Friction angle at peak shear strength in degrees (optional, default=0.0)
            refPress: Reference mean effective confining pressure (optional, default=100.0 kPa)
            pressDependCoe: Positive constant defining variations of G and B as function of instantaneous effective confinement (optional, default=0.0)
            noYieldSurf: Number of yield surfaces, must be less than 40 (optional, default=20.0)
            yieldSurf: User-defined yield surfaces as pairs of shear strain and modulus ratio values (optional, default=None)
            
        Note:
            Plasticity exhibits only in deviatoric stress-strain response.
            Volumetric stress-strain response is linear-elastic and independent of deviatoric response.
            
        Example:
            ops.nDMaterial('PressureIndependMultiYield', 1, 2, 1.8e-4, 7.5e4, 2.0e5, 81, 0.1)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["PressureDependMultiYield"], matTag: int, nd: float, rho: float, refShearModul: float, refBulkModul: float, frictionAng: float, peakShearStra: float, refPress: float, pressDependCoe: float, PTAng: float, contrac: float, dilat1: float, dilat2: float, liquefac1: float, liquefac2: float, liquefac3: float, noYieldSurf: float = 20.0, yieldSurf: list[float] |None = None, e: float = 0.6, cs1: float = 0.9, cs2: float = 0.02, cs3: float = 0.7, pa: float = 101.0, c: float = 0.3) -> None:
        """Define pressure dependent multi-yield material for pressure sensitive soil under general loading
        
        Args:
            material_type: Material type 'PressureDependMultiYield'
            matTag: Material tag identifier
            nd: Number of dimensions (2 for plane-strain, 3 for 3D analysis)
            rho: Saturated soil mass density
            refShearModul: Reference low-strain shear modulus Gr
            refBulkModul: Reference bulk modulus Br
            frictionAng: Friction angle at peak shear strength in degrees
            peakShearStra: Octahedral shear strain at which maximum shear strength is reached
            refPress: Reference mean effective confining pressure
            pressDependCoe: Positive constant defining variations of G and B as function of instantaneous effective confinement
            PTAng: Phase transformation angle in degrees
            contrac: Non-negative constant defining rate of shear-induced volume decrease (contraction)
            dilat1: Non-negative constant defining rate of shear-induced volume increase (dilation)
            dilat2: Non-negative constant defining rate of shear-induced volume increase (dilation)
            liquefac1: Parameter controlling liquefaction-induced plastic shear strain accumulation - effective confining pressure
            liquefac2: Parameter controlling liquefaction-induced plastic shear strain accumulation - maximum plastic shear strain at zero confinement
            liquefac3: Parameter controlling liquefaction-induced plastic shear strain accumulation - biased plastic shear strain factor
            noYieldSurf: Number of yield surfaces, must be less than 40 (optional, default=20.0)
            yieldSurf: User-defined yield surfaces as pairs of shear strain and modulus ratio values (optional, default=None)
            e: Initial void ratio (optional, default=0.6)
            cs1: Critical state parameter (optional, default=0.9)
            cs2: Critical state parameter (optional, default=0.02)
            cs3: Critical state parameter (optional, default=0.7)
            pa: Atmospheric pressure for normalization (optional, default=101.0)
            c: Numerical constant (optional, default=0.3)
            
        Note:
            Simulates dilatancy and non-flow liquefaction (cyclic mobility) in sands or silts.
            
        Example:
            ops.nDMaterial('PressureDependMultiYield', 1, 2, 1.7e-4, 9.0e4, 2.2e5, 31, 0.1, 101, 0.5, 26, 0.07, 0.4, 3.0, 1.0, 0.0, 5.0)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["PressureDependMultiYield02"], matTag: int, nd: float, rho: float, refShearModul: float, refBulkModul: float, frictionAng: float, peakShearStra: float, refPress: float, pressDependCoe: float, PTAng: float, contrac0: float, contrac2: float, dilat0: float, dilat2: float, noYieldSurf: float = 20.0, yieldSurf: Optional[List[float]] = None, contrac1: float = 5.0, dilat1: float = 3.0, liquefac0: float = 1.0, liquefac1: float = 0.0, e: float = 0.6, cs1: float = 0.9, cs2: float = 0.02, cs3: float = 0.7, pa: float = 101.0, c: float = 0.1) -> None:
        """Define pressure dependent multi-yield material 02 with K-sigma effect and dilation history
        
        Args:
            material_type: Material type 'PressureDependMultiYield02'
            matTag: Material tag identifier
            nd: Number of dimensions (2 for plane-strain, 3 for 3D analysis)
            rho: Saturated soil mass density
            refShearModul: Reference low-strain shear modulus Gr
            refBulkModul: Reference bulk modulus Br
            frictionAng: Friction angle at peak shear strength in degrees
            peakShearStra: Octahedral shear strain at which maximum shear strength is reached
            refPress: Reference mean effective confining pressure
            pressDependCoe: Positive constant defining variations of G and B as function of instantaneous effective confinement
            PTAng: Phase transformation angle in degrees
            contrac0: Non-negative constant defining rate of shear-induced volume decrease
            contrac2: Non-negative constant reflecting K-sigma effect
            dilat0: Non-negative constant defining rate of shear-induced volume increase
            dilat2: Non-negative constant reflecting K-sigma effect
            noYieldSurf: Number of yield surfaces, must be less than 40 (optional, default=20.0)
            yieldSurf: User-defined yield surfaces (optional, default=None)
            contrac1: Non-negative constant reflecting dilation history on contraction tendency (optional, default=5.0)
            dilat1: Non-negative constant defining rate of shear-induced volume increase (optional, default=3.0)
            liquefac0: Damage parameter for accumulated permanent shear strain as function of dilation history (optional, default=1.0)
            liquefac1: Damage parameter for biased accumulation of permanent shear strain (optional, default=0.0)
            e: Initial void ratio (optional, default=0.6)
            cs1: Critical state parameter (optional, default=0.9)
            cs2: Critical state parameter (optional, default=0.02)
            cs3: Critical state parameter (optional, default=0.7)
            pa: Atmospheric pressure for normalization (optional, default=101.0)
            c: Numerical constant (optional, default=0.1)
            
        Note:
            Modified from PressureDependMultiYield with additional K-sigma parameters and dilation history effects.
            
        Example:
            ops.nDMaterial('PressureDependMultiYield02', 1, 2, 1.7e-4, 9.0e4, 2.2e5, 31, 0.1, 101, 0.5, 26, 0.07, 0.4, 0.4, 3.0)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["PressureDependMultiYield03"], matTag: int, nd: float, rho: float, refShearModul: float, refBulkModul: float, frictionAng: float, peakShearStra: float, refPress: float, pressDependCoe: float, PTAng: float, ca: float, cb: float, cc: float, cd: float, ce: float, da: float, db: float, dc: float, noYieldSurf: float = 20.0, yieldSurf: Optional[List[float]] = None, liquefac1: float = 1.0, liquefac2: float = 0.0, pa: float = 101.0, s0: float = 1.73) -> None:
        """Define pressure dependent multi-yield material 03 with liquefaction triggering guidelines
        
        Args:
            material_type: Material type 'PressureDependMultiYield03'
            matTag: Material tag identifier
            nd: Number of dimensions (2 for plane-strain, 3 for 3D analysis)
            rho: Saturated soil mass density
            refShearModul: Reference low-strain shear modulus Gr
            refBulkModul: Reference bulk modulus Br
            frictionAng: Friction angle at peak shear strength in degrees
            peakShearStra: Octahedral shear strain at which maximum shear strength is reached
            refPress: Reference mean effective confining pressure
            pressDependCoe: Positive constant defining variations of G and B
            PTAng: Phase transformation angle in degrees
            ca: Model parameter
            cb: Model parameter
            cc: Model parameter
            cd: Model parameter
            ce: Model parameter
            da: Model parameter
            db: Model parameter
            dc: Model parameter
            noYieldSurf: Number of yield surfaces (optional, default=20.0)
            yieldSurf: User-defined yield surfaces (optional, default=None)
            liquefac1: Liquefaction parameter (optional, default=1.0)
            liquefac2: Liquefaction parameter (optional, default=0.0)
            pa: Atmospheric pressure (optional, default=101.0)
            s0: Material parameter (optional, default=1.73)
            
        Note:
            Modified from PressureDependMultiYield02 to comply with established guidelines on liquefaction triggering.
            Considers dependence on number of loading cycles, effective overburden stress (K-sigma), and static shear stress (K-alpha).
            
        Example:
            ops.nDMaterial('PressureDependMultiYield03', 1, 2, 1.7e-4, 9.0e4, 2.2e5, 31, 0.1, 101, 0.5, 26, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
        """
        ...

    @overload
    def nDMaterial(self, material_type: Literal["FluidSolidPorous"], matTag: int, nd: float, soilMatTag: int, combinedBulkModul: float, pa: float = 101.0) -> None:
        """Define fluid solid porous material for saturated porous media under undrained conditions
        
        Args:
            material_type: Material type 'FluidSolidPorous'
            matTag: Material tag identifier
            nd: Number of dimensions (2 for plane-strain, 3 for 3D analysis)
            soilMatTag: Material tag for the solid phase material (previously defined)
            combinedBulkModul: Combined undrained bulk modulus Bc relating changes in pore pressure and volumetric strain
            pa: Atmospheric pressure for normalization (optional, default=101.0)
            
        Note:
            Couples responses of fluid and solid phases.
            Fluid phase response is only volumetric and linear elastic.
            Solid phase can be any NDMaterial.
            Combined bulk modulus may be approximated as Bc ≈ Bf/n where Bf is bulk modulus of fluid phase and n is initial porosity.
            
        Example:
            ops.nDMaterial('FluidSolidPorous', 1, 2, 10, 2.2e6)
        """
        ...

    # Generic nD material fallback
    @overload
    def nDMaterial(
        self,
        material_type: Literal[
            "ElasticIsotropic", "ElasticOrthotropic", "J2Plasticity", "DruckerPrager", "PlaneStress", "PlaneStrain", "MultiaxialCyclicPlasticity",
            "BoundingCamClay", "PlateFiber", "FSAM", "ManzariDafalias", "PM4Sand", "PM4Silt", "StressDensityModel", "AcousticMedium",
            "CycLiqCP", "CycLiqCPSP", "ContactMaterial2D", "ContactMaterial3D", "PlateFromPlaneStress", "PlateRebar", "PlasticDamageConcretePlaneStress",
            "InitialStateAnalysisWrapper", "InitStressNDMaterial", "InitStrainNDMaterial", "PressureIndependMultiYield", "PressureDependMultiYield",
            "PressureDependMultiYield02", "PressureDependMultiYield03", "FluidSolidPorous"
            ],
            material_tag: int,
            *args: Any
        ) -> None:
        """Define nDmaterial
        
        Supported material types:
            # Standard Models
            ElasticIsotropic, ElasticOrthotropic, J2Plasticity, DruckerPrager,
            PlaneStress, PlaneStrain, MultiaxialCyclicPlasticity, BoundingCamClay,
            PlateFiber, FSAM, ManzariDafalias, PM4Sand, PM4Silt, stressDensity,
            AcousticMedium
            
            # Tsinghua Sand Models
            CycLiqCP, CycLiqCPSP
            
            # Contact Materials
            ContactMaterial2D, ContactMaterial3D
            
            # Concrete Wall Materials
            PlateFromPlaneStress, PlateRebar, PlasticDamageConcretePlaneStress
            
            # Initial State Analysis
            InitialStateAnalysisWrapper, InitStressNDMaterial, InitStrainNDMaterial
            
            # UC San Diego Models
            PressureIndependMultiYield, PressureDependMultiYield,
            PressureDependMultiYield02, PressureDependMultiYield03
            
            # Saturated Undrained Soil
            FluidSolidPorous
        
        Args:
            material_type: Material type
            material_tag: Material tag
            *args: Material properties (varies by material type)
            
        Example:
            ops.nDMaterial('ElasticIsotropic', 1, 29000.0)
        """
        ... 