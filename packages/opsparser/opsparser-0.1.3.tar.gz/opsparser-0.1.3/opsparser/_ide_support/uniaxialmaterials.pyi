"""材料命令类型注解"""

from typing import overload, Literal, Optional, Any, List

class uniaxialMaterialCommands:
    """材料命令的类型注解"""
    
    # === Uniaxial Materials ===
    @overload
    def uniaxialMaterial(self, material_type: Literal["Elastic"], matTag: int, E: float, eta: Optional[float] = None, Eneg: Optional[float] = None) -> None:
        """Define elastic uniaxial material
        
        Args:
            material_type: Material type 'Elastic'
            matTag: Unique material identifier
            E: Tangent modulus
            eta: Damping tangent (optional, default=0.0)
            Eneg: Tangent in compression (optional, default=E)
            
        Example:
            ops.uniaxialMaterial('Elastic', 1, 29000.0)
            ops.uniaxialMaterial('Elastic', 2, 29000.0, 0.01, 25000.0)
        """
        ...
    
    # Steel01 material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Steel01"], material_tag: int, yield_strength: float, initial_stiffness: float, strain_hardening_ratio: float, a1: Optional[float] = None, a2: Optional[float] = None, a3: Optional[float] = None, a4: Optional[float] = None) -> None:
        """Define Steel01 uniaxial material with isotropic hardening
        
        Args:
            material_type: Material type 'Steel01'
            material_tag: Unique material identifier
            yield_strength: Yield strength (Fy)
            initial_stiffness: Initial elastic tangent (E0)
            strain_hardening_ratio: Strain-hardening ratio (b)
            a1, a2, a3, a4: Optional isotropic hardening parameters
            
        Example:
            ops.uniaxialMaterial('Steel01', 1, 60.0, 29000.0, 0.02)
            ops.uniaxialMaterial('Steel01', 2, 50.0, 29000.0, 0.01, 18.5, 0.925, 0.15)
        """
        ...

    # Steel02 material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Steel02"], material_tag: int, Fy: float, E0: float, b: float, params: List[float], a1: Optional[float] = None, a2: Optional[float] = None, a3: Optional[float] = None, a4: Optional[float] = None, sigInit: Optional[float] = None) -> None:
        """Define Steel02 uniaxial material with Giuffre-Menegotto-Pinto model
        
        Args:
            material_type: Material type 'Steel02'
            material_tag: Unique material identifier
            Fy: Yield strength
            E0: Initial elastic tangent
            b: Strain-hardening ratio
            params: Parameters [R0, cR1, cR2] to control transition from elastic to plastic
            a1, a2, a3, a4: Optional isotropic hardening parameters
            sigInit: Initial stress value (optional)
            
        Example:
            ops.uniaxialMaterial('Steel02', 1, 60.0, 29000.0, 0.02, [20, 0.925, 0.15])
        """
        ...

    # Steel4 material  
    @overload
    def uniaxialMaterial(self, material_type: Literal["Steel4"], material_tag: int, Fy: float, E0: float, **kwargs: Any) -> None:
        """Define Steel4 uniaxial material with combined kinematic and isotropic hardening
        
        Args:
            material_type: Material type 'Steel4'
            material_tag: Unique material identifier
            Fy: Yield strength
            E0: Initial elastic tangent
            kwargs: Additional parameters for kinematic hardening (-kin), isotropic hardening (-iso), 
                   asymmetric behavior (-asym), ultimate strength (-ult), initial stress (-init), 
                   memory configuration (-mem)
            
        Example:
            ops.uniaxialMaterial('Steel4', 1, 60.0, 29000.0, '-kin', 0.02, [20, 0.90, 0.15])
        """
        ...

    # ReinforcingSteel material
    @overload  
    def uniaxialMaterial(self, material_type: Literal["ReinforcingSteel"], material_tag: int, fy: float, fu: float, Es: float, Esh: float, eps_sh: float, eps_ult: float, **kwargs: Any) -> None:
        """Define ReinforcingSteel uniaxial material for reinforced concrete
        
        Args:
            material_type: Material type 'ReinforcingSteel'
            material_tag: Unique material identifier
            fy: Yield stress in tension
            fu: Ultimate stress in tension
            Es: Initial elastic tangent
            Esh: Tangent at initial strain hardening
            eps_sh: Strain corresponding to initial strain hardening
            eps_ult: Strain at peak stress
            kwargs: Optional parameters for buckling (-GABuck, -DMBuck), fatigue (-CMFatigue), 
                   isotropic hardening (-IsoHard), curve parameters (-MPCurveParams)
            
        Example:
            ops.uniaxialMaterial('ReinforcingSteel', 1, 60.0, 90.0, 29000.0, 600.0, 0.008, 0.08)
        """
        ...

    # Dodd_Restrepo material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Dodd_Restrepo"], material_tag: int, Fy: float, Fsu: float, ESH: float, ESU: float, Youngs: float, ESHI: float, FSHI: float, OmegaFac: Optional[float] = None) -> None:
        """Define Dodd-Restrepo steel material
        
        Args:
            material_type: Material type 'Dodd_Restrepo'
            material_tag: Unique material identifier
            Fy: Yield strength
            Fsu: Ultimate tensile strength (UTS)
            ESH: Tensile strain at initiation of strain hardening
            ESU: Tensile strain at the UTS
            Youngs: Modulus of elasticity
            ESHI: Tensile strain for a point on strain hardening curve
            FSHI: Tensile stress at point on strain hardening curve
            OmegaFac: Roundedness factor for Bauschinger curve (optional, default=1.0)
            
        Example:
            ops.uniaxialMaterial('Dodd_Restrepo', 1, 60.0, 90.0, 0.008, 0.08, 29000.0, 0.02, 75.0)
        """
        ...

    # RambergOsgoodSteel material
    @overload
    def uniaxialMaterial(self, material_type: Literal["RambergOsgoodSteel"], material_tag: int, fy: float, E0: float, a: float, n: float) -> None:
        """Define Ramberg-Osgood steel material
        
        Args:
            material_type: Material type 'RambergOsgoodSteel'
            material_tag: Unique material identifier
            fy: Yield strength
            E0: Initial elastic tangent
            a: Yield offset (commonly used value is 0.002)
            n: Parameter to control transition and hardening (commonly ≥ 5)
            
        Example:
            ops.uniaxialMaterial('RambergOsgoodSteel', 1, 60.0, 29000.0, 0.002, 5.0)
        """
        ...

    # SteelMPF material
    @overload
    def uniaxialMaterial(self, material_type: Literal["SteelMPF"], material_tag: int, fyp: float, fyn: float, E0: float, bp: float, bn: float, params: List[float], a1: Optional[float] = None, a2: Optional[float] = None, a3: Optional[float] = None, a4: Optional[float] = None) -> None:
        """Define SteelMPF uniaxial material with Menegotto-Pinto model
        
        Args:
            material_type: Material type 'SteelMPF'
            material_tag: Unique material identifier
            fyp: Yield strength in tension (positive loading direction)
            fyn: Yield strength in compression (negative loading direction)
            E0: Initial tangent modulus
            bp: Strain hardening ratio in tension
            bn: Strain hardening ratio in compression
            params: Parameters [R0, cR1, cR2] to control transition from elastic to plastic
            a1, a2, a3, a4: Optional isotropic hardening parameters
            
        Example:
            ops.uniaxialMaterial('SteelMPF', 1, 60.0, -60.0, 29000.0, 0.02, 0.02, [20, 0.925, 0.15])
        """
        ...

    # Steel01Thermal material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Steel01Thermal"], material_tag: int, Fy: float, E0: float, b: float, a1: Optional[float] = None, a2: Optional[float] = None, a3: Optional[float] = None, a4: Optional[float] = None) -> None:
        """Define Steel01Thermal uniaxial material (thermal version of Steel01)
        
        Args:
            material_type: Material type 'Steel01Thermal'
            material_tag: Unique material identifier
            Fy: Yield strength
            E0: Initial elastic tangent
            b: Strain-hardening ratio
            a1, a2, a3, a4: Optional isotropic hardening parameters
            
        Example:
            ops.uniaxialMaterial('Steel01Thermal', 1, 60.0, 29000.0, 0.02)
        """
        ...

    # === Concrete Materials ===

    # Concrete01 material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Concrete01"], material_tag: int, fpc: float, epsc0: float, fpcu: float, epsU: float) -> None:
        """Define Concrete01 uniaxial material with Kent-Scott-Park model
        
        Args:
            material_type: Material type 'Concrete01'
            material_tag: Unique material identifier
            fpc: Concrete compressive strength at 28 days (compression is negative)
            epsc0: Concrete strain at maximum strength
            fpcu: Concrete crushing strength
            epsU: Concrete strain at crushing strength
            
        Example:
            ops.uniaxialMaterial('Concrete01', 1, -4000.0, -0.002, -800.0, -0.006)
        """
        ...

    # Concrete02 material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Concrete02"], material_tag: int, fpc: float, epsc0: float, fpcu: float, epsU: float, lambda_param: float, ft: float, Ets: float) -> None:
        """Define Concrete02 uniaxial material with Kent-Scott-Park model and tension
        
        Args:
            material_type: Material type 'Concrete02'
            material_tag: Unique material identifier
            fpc: Concrete compressive strength at 28 days (compression is negative)
            epsc0: Concrete strain at maximum strength
            fpcu: Concrete crushing strength
            epsU: Concrete strain at crushing strength
            lambda_param: Ratio between unloading slope at epscu and initial slope
            ft: Tensile strength
            Ets: Tension softening stiffness (absolute value)
            
        Example:
            ops.uniaxialMaterial('Concrete02', 1, -4000.0, -0.002, -800.0, -0.006, 0.1, 400.0, 2000.0)
        """
        ...

    # Concrete04 material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Concrete04"], material_tag: int, fc: float, epsc: float, epscu: float, Ec: float, fct: Optional[float] = None, et: Optional[float] = None, beta: Optional[float] = None) -> None:
        """Define Concrete04 uniaxial material with Popovics model
        
        Args:
            material_type: Material type 'Concrete04'
            material_tag: Unique material identifier
            fc: Concrete compressive strength at 28 days (compression is negative)
            epsc: Concrete strain at maximum strength
            epscu: Concrete strain at crushing strength
            Ec: Initial stiffness
            fct: Maximum tensile strength of concrete (optional)
            et: Ultimate tensile strain of concrete (optional)
            beta: Exponential curve parameter to define residual stress (optional)
            
        Example:
            ops.uniaxialMaterial('Concrete04', 1, -4000.0, -0.002, -0.006, 25000.0)
        """
        ...

    # Concrete06 material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Concrete06"], material_tag: int, fc: float, e0: float, n: float, k: float, alpha1: float, fcr: float, ecr: float, b: float, alpha2: float) -> None:
        """Define Concrete06 uniaxial material with tensile strength and nonlinear tension stiffening
        
        Args:
            material_type: Material type 'Concrete06'
            material_tag: Unique material identifier
            fc: Concrete compressive strength (compression is negative)
            e0: Strain at compressive strength
            n: Compressive shape factor
            k: Post-peak compressive shape factor
            alpha1: Parameter for compressive plastic strain definition
            fcr: Tensile strength
            ecr: Tensile strain at peak stress (fcr)
            b: Exponent of the tension stiffening curve
            alpha2: Parameter for tensile plastic strain definition
            
        Example:
            ops.uniaxialMaterial('Concrete06', 1, -4000.0, -0.002, 2.0, 1.0, 0.08, 400.0, 0.0001, 0.1, 0.08)
        """
        ...

    # Concrete07 material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Concrete07"], material_tag: int, fc: float, epsc: float, Ec: float, ft: float, et: float, xp: float, xn: float, r: float) -> None:
        """Define Concrete07 uniaxial material based on Chang & Mander model
        
        Args:
            material_type: Material type 'Concrete07'
            material_tag: Unique material identifier
            fc: Concrete compressive strength (compression is negative)
            epsc: Concrete strain at maximum compressive strength
            Ec: Initial elastic modulus of the concrete
            ft: Tensile strength of concrete (tension is positive)
            et: Tensile strain at max tensile strength of concrete
            xp: Non-dimensional term defining strain at which straight line descent begins in tension
            xn: Non-dimensional term defining strain at which straight line descent begins in compression
            r: Parameter that controls the nonlinear descending branch
            
        Example:
            ops.uniaxialMaterial('Concrete07', 1, -4000.0, -0.002, 25000.0, 400.0, 0.0001, 10000.0, 2.0, 4.0)
        """
        ...

    # Concrete01WithSITC material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Concrete01WithSITC"], material_tag: int, fpc: float, epsc0: float, fpcu: float, epsU: float, endStrainSITC: Optional[float] = None) -> None:
        """Define Concrete01WithSITC uniaxial material with Stuff In The Cracks effect
        
        Args:
            material_type: Material type 'Concrete01WithSITC'
            material_tag: Unique material identifier
            fpc: Concrete compressive strength at 28 days (compression is negative)
            epsc0: Concrete strain at maximum strength
            fpcu: Concrete crushing strength
            epsU: Concrete strain at crushing strength
            endStrainSITC: End strain for SITC effect (optional, default=0.03)
            
        Example:
            ops.uniaxialMaterial('Concrete01WithSITC', 1, -4000.0, -0.002, -800.0, -0.006)
        """
        ...

    # ConfinedConcrete01 material
    @overload
    def uniaxialMaterial(self, material_type: Literal["ConfinedConcrete01"], material_tag: int, secType: str, fpc: float, Ec: float, epscu_type: str, epscu_val: float, **kwargs: Any) -> None:
        """Define ConfinedConcrete01 uniaxial material for confined concrete
        
        Args:
            material_type: Material type 'ConfinedConcrete01'
            material_tag: Unique material identifier
            secType: Section type ('S1', 'S2', 'S3', 'S4a', 'S4b', 'S5', 'C', 'R')
            fpc: Unconfined cylindrical strength of concrete specimen
            Ec: Initial elastic modulus of unconfined concrete
            epscu_type: Method to define ultimate strain ('-epscu' or '-gamma')
            epscu_val: Value for ultimate strain definition
            kwargs: Additional parameters for geometry, reinforcement, wrapping, etc.
            
        Example:
            ops.uniaxialMaterial('ConfinedConcrete01', 1, 'C', -30.0, 25000.0, '-epscu', 0.05)
        """
        ...

    # ConcreteD material
    @overload
    def uniaxialMaterial(self, material_type: Literal["ConcreteD"], material_tag: int, fc: float, epsc: float, ft: float, epst: float, Ec: float, alphac: float, alphat: float, cesp: Optional[float] = None, etap: Optional[float] = None) -> None:
        """Define ConcreteD uniaxial material based on Chinese design code
        
        Args:
            material_type: Material type 'ConcreteD'
            material_tag: Unique material identifier
            fc: Concrete compressive strength
            epsc: Concrete strain at compressive strength
            ft: Concrete tensile strength
            epst: Concrete strain at tensile strength
            Ec: Concrete initial elastic modulus
            alphac: Compressive descending parameter
            alphat: Tensile descending parameter
            cesp: Plastic parameter (optional, recommended 0.2~0.3, default=0.25)
            etap: Plastic parameter (optional, recommended 1.0~1.3, default=1.15)
            
        Example:
            ops.uniaxialMaterial('ConcreteD', 1, -30.0, -0.002, 3.0, 0.0001, 30000.0, 2.0, 1.5)
        """
        ...

    # FRPConfinedConcrete material
    @overload
    def uniaxialMaterial(self, material_type: Literal["FRPConfinedConcrete"], material_tag: int, fpc1: float, fpc2: float, epsc0: float, D: float, c: float, Ej: float, Sj: float, tj: float, eju: float, S: float, fyl: float, fyh: float, dlong: float, dtrans: float, Es: float, nu0: float, k: float, useBuck: float) -> None:
        """Define FRPConfinedConcrete uniaxial material
        
        Args:
            material_type: Material type 'FRPConfinedConcrete'
            material_tag: Unique material identifier
            fpc1: Concrete core compressive strength
            fpc2: Concrete cover compressive strength
            epsc0: Strain corresponding to unconfined concrete strength
            D: Diameter of the circular section
            c: Dimension of concrete cover
            Ej: Elastic modulus of the FRP jacket
            Sj: Clear spacing of the FRP strips
            tj: Total thickness of the FRP jacket
            eju: Rupture strain of the FRP jacket from tensile coupons
            S: Spacing of the steel spiral/stirrups
            fyl: Yielding strength of longitudinal steel bars
            fyh: Yielding strength of the steel spiral/stirrups
            dlong: Diameter of the longitudinal bars
            dtrans: Diameter of the steel spiral/stirrups
            Es: Elastic modulus of steel
            nu0: Initial Poisson's coefficient for concrete
            k: Reduction factor for the rupture strain of the FRP jacket
            useBuck: FRP jacket failure criterion due to buckling
            
        Example:
            ops.uniaxialMaterial('FRPConfinedConcrete', 1, 30.0, 25.0, 0.002, 300.0, 25.0, 230000.0, 0.0, 1.0, 0.012, 100.0, 400.0, 600.0, 16.0, 8.0, 200000.0, 0.2, 0.75, 1.0)
        """
        ...

    # FRPConfinedConcrete02 material
    @overload
    def uniaxialMaterial(self, material_type: Literal["FRPConfinedConcrete02"], material_tag: int, fc0: float, Ec: float, ec0: float, ft: float, Ets: float, Unit: float, **kwargs: Any) -> None:
        """Define FRPConfinedConcrete02 uniaxial hysteretic material
        
        Args:
            material_type: Material type 'FRPConfinedConcrete02'
            material_tag: Unique material identifier
            fc0: Compressive strength of unconfined concrete (compression is negative)
            Ec: Elastic modulus of unconfined concrete
            ec0: Axial strain corresponding to unconfined concrete strength
            ft: Tensile strength of unconfined concrete
            Ets: Stiffness of tensile softening
            Unit: Unit indicator (1 for SI Metric Units, 0 for US Customary Units)
            kwargs: Optional parameters for FRP jacket (-JacketC) or ultimate values (-Ultimate)
            
        Example:
            ops.uniaxialMaterial('FRPConfinedConcrete02', 1, -30.0, 25000.0, -0.002, 3.0, 1250.0, 1)
        """
        ...

    # ConcreteCM material
    @overload
    def uniaxialMaterial(self, material_type: Literal["ConcreteCM"], material_tag: int, fpcc: float, epcc: float, Ec: float, rc: float, xcrn: float, ft: float, et: float, rt: float, xcrp: float, mon: int, GapClose: Optional[int] = None) -> None:
        """Define ConcreteCM uniaxial hysteretic material
        
        Args:
            material_type: Material type 'ConcreteCM'
            material_tag: Unique material identifier
            fpcc: Compressive strength
            epcc: Strain at compressive strength
            Ec: Initial tangent modulus
            rc: Shape parameter in Tsai's equation for compression
            xcrn: Non-dimensional critical strain on compression envelope
            ft: Tensile strength
            et: Strain at tensile strength
            rt: Shape parameter in Tsai's equation for tension
            xcrp: Non-dimensional critical strain on tension envelope
            mon: Monotonic stress-strain relationship (1 for monotonic, 0 for cyclic)
            GapClose: Gap closure parameter (optional, 0 for less gradual, 1 for more gradual)
            
        Example:
            ops.uniaxialMaterial('ConcreteCM', 1, -30.0, -0.002, 25000.0, 7.0, 3.0, 3.0, 0.0001, 1.2, 10000.0, 0)
        """
        ...

    # TDConcrete material
    @overload
    def uniaxialMaterial(self, material_type: Literal["TDConcrete"], material_tag: int, fc: float, fct: float, Ec: float, beta: float, tD: float, epsshu: float, psish: float, Tcr: float, phiu: float, psicr1: float, psicr2: float, tcast: float) -> None:
        """Define TDConcrete time-dependent uniaxial material
        
        Args:
            material_type: Material type 'TDConcrete'
            material_tag: Unique material identifier
            fc: Concrete compressive strength (compression is negative)
            fct: Concrete tensile strength (tension is positive)
            Ec: Concrete modulus of elasticity
            beta: Tension softening parameter
            tD: Analysis time at initiation of drying (in days)
            epsshu: Ultimate shrinkage strain as per ACI 209R-92 (shrinkage is negative)
            psish: Fitting parameter of the shrinkage time evolution function
            Tcr: Creep model age (in days)
            phiu: Ultimate creep coefficient as per ACI 209R-92
            psicr1: Fitting parameter of the creep time evolution function
            psicr2: Fitting parameter of the creep time evolution function
            tcast: Analysis time corresponding to concrete casting (in days, minimum 2.0)
            
        Example:
            ops.uniaxialMaterial('TDConcrete', 1, -30.0, 3.0, 25000.0, 0.1, 7.0, -0.0003, 0.5, 28.0, 2.35, 10.0, 5.0, 1.0)
        """
        ...

    # TDConcreteEXP material
    @overload
    def uniaxialMaterial(self, material_type: Literal["TDConcreteEXP"], material_tag: int, fc: float, fct: float, Ec: float, beta: float, tD: float, epsshu: float, psish: float, Tcr: float, epscru: float, sigCr: float, psicr1: float, psicr2: float, tcast: float) -> None:
        """Define TDConcreteEXP time-dependent uniaxial material with experimental creep
        
        Args:
            material_type: Material type 'TDConcreteEXP'
            material_tag: Unique material identifier
            fc: Concrete compressive strength (compression is negative)
            fct: Concrete tensile strength (tension is positive)
            Ec: Concrete modulus of elasticity
            beta: Tension softening parameter
            tD: Analysis time at initiation of drying (in days)
            epsshu: Ultimate shrinkage strain as per ACI 209R-92 (shrinkage is negative)
            psish: Fitting parameter of the shrinkage time evolution function
            Tcr: Creep model age (in days)
            epscru: Ultimate creep strain (from experimental measurements)
            sigCr: Concrete compressive stress associated with epscru (input as negative)
            psicr1: Fitting parameter of the creep time evolution function
            psicr2: Fitting parameter of the creep time evolution function
            tcast: Analysis time corresponding to concrete casting (in days, minimum 2.0)
            
        Example:
            ops.uniaxialMaterial('TDConcreteEXP', 1, -30.0, 3.0, 25000.0, 0.1, 7.0, -0.0003, 0.5, 28.0, -0.001, -15.0, 10.0, 5.0, 1.0)
        """
        ...

    # TDConcreteMC10 material
    @overload
    def uniaxialMaterial(self, material_type: Literal["TDConcreteMC10"], material_tag: int, fc: float, fct: float, Ec: float, Ecm: float, beta: float, tD: float, epsba: float, epsbb: float, epsda: float, epsdb: float, phiba: float, phibb: float, phida: float, phidb: float, tcast: float, cem: float) -> None:
        """Define TDConcreteMC10 time-dependent material according to fib Model Code 2010
        
        Args:
            material_type: Material type 'TDConcreteMC10'
            material_tag: Unique material identifier
            fc: Concrete compressive strength (compression is negative)
            fct: Concrete tensile strength (tension is positive)
            Ec: Concrete modulus of elasticity at loading age
            Ecm: Concrete modulus of elasticity at 28 days
            beta: Tension softening parameter
            tD: Analysis time at initiation of drying (in days)
            epsba: Ultimate basic shrinkage strain (input as negative)
            epsbb: Fitting parameter of the basic shrinkage time evolution function
            epsda: Product of ultimate drying shrinkage strain and relative humidity function
            epsdb: Fitting parameter of the basic shrinkage time evolution function
            phiba: Parameter for the effect of compressive strength on basic creep
            phibb: Fitting parameter of the basic creep time evolution function
            phida: Product of the effect of compressive strength and relative humidity on drying creep
            phidb: Fitting parameter of the drying creep time evolution function
            tcast: Analysis time corresponding to concrete casting (in days, minimum 2.0)
            cem: Coefficient dependent on the type of cement
            
        Example:
            ops.uniaxialMaterial('TDConcreteMC10', 1, -30.0, 3.0, 25000.0, 30000.0, 0.1, 7.0, -0.0001, 1.0, -0.0002, 0.5, 1.8, 0.3, 2.3, 1.0, 1.0, 1.0)
        """
        ...

    # TDConcreteMC10NL material
    @overload
    def uniaxialMaterial(self, material_type: Literal["TDConcreteMC10NL"], material_tag: int, fc: float, fcu: float, epscu: float, fct: float, Ec: float, Ecm: float, beta: float, tD: float, epsba: float, epsbb: float, epsda: float, epsdb: float, phiba: float, phibb: float, phida: float, phidb: float, tcast: float, cem: float) -> None:
        """Define TDConcreteMC10NL time-dependent material with non-linear compression
        
        Args:
            material_type: Material type 'TDConcreteMC10NL'
            material_tag: Unique material identifier
            fc: Concrete compressive strength (compression is negative)
            fcu: Concrete crushing strength (compression is negative)
            epscu: Concrete strain at crushing strength (input as negative)
            fct: Concrete tensile strength (tension is positive)
            Ec: Concrete modulus of elasticity at loading age
            Ecm: Concrete modulus of elasticity at 28 days
            beta: Tension softening parameter
            tD: Analysis time at initiation of drying (in days)
            epsba: Ultimate basic shrinkage strain (input as negative)
            epsbb: Fitting parameter of the basic shrinkage time evolution function
            epsda: Product of ultimate drying shrinkage strain and relative humidity function
            epsdb: Fitting parameter of the basic shrinkage time evolution function
            phiba: Parameter for the effect of compressive strength on basic creep
            phibb: Fitting parameter of the basic creep time evolution function
            phida: Product of the effect of compressive strength and relative humidity on drying creep
            phidb: Fitting parameter of the drying creep time evolution function
            tcast: Analysis time corresponding to concrete casting (in days, minimum 2.0)
            cem: Coefficient dependent on the type of cement
            
        Example:
            ops.uniaxialMaterial('TDConcreteMC10NL', 1, -30.0, -6.0, -0.005, 3.0, 25000.0, 30000.0, 0.1, 7.0, -0.0001, 1.0, -0.0002, 0.5, 1.8, 0.3, 2.3, 1.0, 1.0, 1.0)
        """
        ...

    # Elastic-Perfectly Plastic Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["ElasticPP"], matTag: int, E: float, epsyP: float, epsyN: Optional[float] = None, eps0: Optional[float] = None) -> None:
        """Define elastic perfectly-plastic uniaxial material
        
        Args:
            material_type: Material type 'ElasticPP'
            matTag: Unique material identifier
            E: Tangent modulus
            epsyP: Strain at which material reaches plastic state in tension
            epsyN: Strain at which material reaches plastic state in compression (optional, default=epsyP)
            eps0: Initial strain (optional, default=0.0)
            
        Example:
            ops.uniaxialMaterial('ElasticPP', 1, 25000.0, 0.002)
            ops.uniaxialMaterial('ElasticPP', 2, 25000.0, 0.002, -0.001, 0.0001)
        """
        ...

    # Elastic-Perfectly Plastic Gap Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["ElasticPPGap"], matTag: int, E: float, Fy: float, gap: float, eta: Optional[float] = None, damage: Optional[str] = None) -> None:
        """Define elastic perfectly-plastic gap uniaxial material
        
        Args:
            material_type: Material type 'ElasticPPGap'
            matTag: Unique material identifier
            E: Tangent modulus
            Fy: Stress or force at which material reaches plastic state
            gap: Initial gap (strain or deformation)
            eta: Hardening ratio (=Eh/E), which can be negative (optional, default=0.0)
            damage: Damage accumulation option ('noDamage' or 'damage', optional, default='noDamage')
            
        Example:
            ops.uniaxialMaterial('ElasticPPGap', 1, 25000.0, 400.0, 0.001)
            ops.uniaxialMaterial('ElasticPPGap', 2, 25000.0, 400.0, 0.001, 0.1, 'damage')
        """
        ...

    # Elastic-No Tension Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["ENT"], matTag: int, E: float) -> None:
        """Define elastic-no tension uniaxial material
        
        Args:
            material_type: Material type 'ENT'
            matTag: Unique material identifier
            E: Tangent modulus
            
        Example:
            ops.uniaxialMaterial('ENT', 1, 25000.0)
        """
        ...

    # Hysteretic Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Hysteretic"], matTag: int, p1: List[float], p2: List[float], p3: Optional[List[float]], n1: List[float], n2: List[float], n3: Optional[List[float]], pinchX: float, pinchY: float, damage1: float, damage2: float, beta: Optional[float] = None) -> None:
        """Define hysteretic uniaxial material with pinching and damage
        
        Args:
            material_type: Material type 'Hysteretic'
            matTag: Unique material identifier
            p1: [s1p, e1p] stress and strain at first point of positive envelope
            p2: [s2p, e2p] stress and strain at second point of positive envelope
            p3: [s3p, e3p] stress and strain at third point of positive envelope (optional, default=p2)
            n1: [s1n, e1n] stress and strain at first point of negative envelope
            n2: [s2n, e2n] stress and strain at second point of negative envelope
            n3: [s3n, e3n] stress and strain at third point of negative envelope (optional, default=n2)
            pinchX: Pinching factor for strain during reloading
            pinchY: Pinching factor for stress during reloading
            damage1: Damage due to ductility: D1(mu-1)
            damage2: Damage due to energy: D2(Eii/Eult)
            beta: Power for degraded unloading stiffness based on ductility (optional, default=0.0)
            
        Example:
            ops.uniaxialMaterial('Hysteretic', 1, [400.0, 0.002], [500.0, 0.02], None, [-400.0, -0.002], [-500.0, -0.02], None, 1.0, 1.0, 0.0, 0.0)
        """
        ...

    # Parallel Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Parallel"], matTag: int, *args: Any) -> None:
        """Define parallel uniaxial material combining multiple materials
        
        Args:
            material_type: Material type 'Parallel'
            matTag: Unique material identifier
            args: Material tags followed by optional '-factors' and factor values
            
        Example:
            ops.uniaxialMaterial('Parallel', 1, 2, 3, 4)
            ops.uniaxialMaterial('Parallel', 1, 2, 3, 4, '-factors', 1.0, 0.5, -0.2)
        """
        ...

    # Series Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Series"], matTag: int, *matTags: int) -> None:
        """Define series uniaxial material combining multiple materials in series
        
        Args:
            material_type: Material type 'Series'
            matTag: Unique material identifier
            matTags: Material tags of materials making up the series model
            
        Example:
            ops.uniaxialMaterial('Series', 1, 2, 3, 4)
        """
        ...

    # PySimple1 Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["PySimple1"], matTag: int, soilType: int, pult: float, Y50: float, Cd: float, c: Optional[float] = None) -> None:
        """Define PySimple1 uniaxial material for p-y springs
        
        Args:
            material_type: Material type 'PySimple1'
            matTag: Unique material identifier
            soilType: Soil type (1=soft clay Matlock 1970, 2=sand API 1993)
            pult: Ultimate capacity of the p-y material
            Y50: Displacement at which 50% of pult is mobilized
            Cd: Drag resistance factor within fully-mobilized gap as Cd*pult
            c: Viscous damping term on elastic component (optional, default=0.0)
            
        Example:
            ops.uniaxialMaterial('PySimple1', 1, 1, 100.0, 0.02, 0.3)
            ops.uniaxialMaterial('PySimple1', 2, 2, 150.0, 0.01, 0.5, 0.1)
        """
        ...

    # QzSimple1 Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["QzSimple1"], matTag: int, qzType: int, qult: float, Z50: float, suction: Optional[float] = None, c: Optional[float] = None) -> None:
        """Define QzSimple1 uniaxial material for q-z springs
        
        Args:
            material_type: Material type 'QzSimple1'
            matTag: Unique material identifier
            qzType: q-z type (1=clay Reese & O'Neill 1987, 2=sand Vijayvergiya 1977)
            qult: Ultimate capacity of the q-z material
            Z50: Displacement at which 50% of qult is mobilized
            suction: Uplift resistance equal to suction*qult (optional, default=0.0, range 0.0-0.1)
            c: Viscous damping term on elastic component (optional, default=0.0)
            
        Example:
            ops.uniaxialMaterial('QzSimple1', 1, 1, 500.0, 0.005)
            ops.uniaxialMaterial('QzSimple1', 2, 2, 750.0, 0.003, 0.05, 0.1)
        """
        ...

    # PyLiq1 Material - version with element tags
    @overload
    def uniaxialMaterial(self, material_type: Literal["PyLiq1"], matTag: int, soilType: int, pult: float, Y50: float, Cd: float, c: float, pRes: float, ele1: int, ele2: int) -> None:
        """Define PyLiq1 uniaxial material for p-y springs with liquefaction (element version)
        
        Args:
            material_type: Material type 'PyLiq1'
            matTag: Unique material identifier
            soilType: Soil type (1=soft clay Matlock 1970, 2=sand API 1993)
            pult: Ultimate capacity of the p-y material
            Y50: Displacement at which 50% of pult is mobilized
            Cd: Drag resistance factor within fully-mobilized gap
            c: Viscous damping term on elastic component
            pRes: Minimum peak resistance retained as soil liquefies
            ele1: Element tag for first soil element
            ele2: Element tag for second soil element
            
        Example:
            ops.uniaxialMaterial('PyLiq1', 1, 1, 100.0, 0.02, 0.3, 0.0, 20.0, 101, 102)
        """
        ...

    # PyLiq1 Material - version with time series
    @overload
    def uniaxialMaterial(self, material_type: Literal["PyLiq1"], matTag: int, soilType: int, pult: float, Y50: float, Cd: float, c: float, pRes: float, timeSeries_flag: Literal['-timeSeries'], timeSeriesTag: int) -> None:
        """Define PyLiq1 uniaxial material for p-y springs with liquefaction (time series version)
        
        Args:
            material_type: Material type 'PyLiq1'
            matTag: Unique material identifier
            soilType: Soil type (1=soft clay Matlock 1970, 2=sand API 1993)
            pult: Ultimate capacity of the p-y material
            Y50: Displacement at which 50% of pult is mobilized
            Cd: Drag resistance factor within fully-mobilized gap
            c: Viscous damping term on elastic component
            pRes: Minimum peak resistance retained as soil liquefies
            timeSeries_flag: Must be '-timeSeries'
            timeSeriesTag: Tag of time series for mean effective stress
            
        Example:
            ops.uniaxialMaterial('PyLiq1', 1, 1, 100.0, 0.02, 0.3, 0.0, 20.0, '-timeSeries', 1)
        """
        ...

    # Hardening Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Hardening"], matTag: int, E: float, sigmaY: float, H_iso: float, H_kin: float, eta: Optional[float] = None) -> None:
        """Define hardening uniaxial material with combined linear kinematic and isotropic hardening
        
        Args:
            material_type: Material type 'Hardening'
            matTag: Unique material identifier
            E: Tangent stiffness
            sigmaY: Yield stress or force
            H_iso: Isotropic hardening modulus
            H_kin: Kinematic hardening modulus
            eta: Visco-plastic coefficient (optional, default=0.0)
            
        Example:
            ops.uniaxialMaterial('Hardening', 1, 29000.0, 400.0, 1000.0, 500.0)
            ops.uniaxialMaterial('Hardening', 2, 29000.0, 400.0, 1000.0, 500.0, 0.01)
        """
        ...

    # Cast Material (CastFuse)
    @overload
    def uniaxialMaterial(self, material_type: Literal["Cast"], matTag: int, n: int, bo: float, h: float, fy: float, E: float, L: float, b: float, Ro: float, cR1: float, cR2: float, a1: Optional[float] = None, a2: Optional[float] = None, a3: Optional[float] = None, a4: Optional[float] = None) -> None:
        """Define Cast uniaxial material for CSF-brace
        
        Args:
            material_type: Material type 'Cast'
            matTag: Unique material identifier
            n: Number of yield fingers of the CSF-brace
            bo: Width of an individual yielding finger at its base
            h: Thickness of an individual yielding finger
            fy: Yield strength of the steel material
            E: Modulus of elasticity of the steel material
            L: Height of an individual yielding finger
            b: Strain hardening ratio
            Ro: Parameter controlling Bauschinger effect (recommended 10-30)
            cR1: Parameter controlling Bauschinger effect (recommended 0.925)
            cR2: Parameter controlling Bauschinger effect (recommended 0.150)
            a1: Isotropic hardening parameter (optional, default=s2*Pp/Kp)
            a2: Isotropic hardening parameter (optional, default=1.0)
            a3: Isotropic hardening parameter (optional, default=a4*Pp/Kp)
            a4: Isotropic hardening parameter (optional, default=1.0)
            
        Example:
            ops.uniaxialMaterial('Cast', 1, 8, 12.0, 6.0, 345.0, 200000.0, 100.0, 0.02, 20.0, 0.925, 0.15)
        """
        ...

    # ViscousDamper Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["ViscousDamper"], matTag: int, K_el: float, Cd: float, alpha: float, LGap: Optional[float] = None, NM: Optional[int] = None, RelTol: Optional[float] = None, AbsTol: Optional[float] = None, MaxHalf: Optional[int] = None) -> None:
        """Define ViscousDamper uniaxial material (Maxwell Model)
        
        Args:
            material_type: Material type 'ViscousDamper'
            matTag: Unique material identifier
            K_el: Elastic stiffness of linear spring
            Cd: Damping coefficient
            alpha: Velocity exponent
            LGap: Gap length due to pin tolerance (optional, default=0.0)
            NM: Numerical algorithm (1=Dormand-Prince54, 2=Adams-Bashforth-Moulton, 3=Rosenbrock, optional, default=1)
            RelTol: Relative error tolerance (optional, default=1e-6)
            AbsTol: Absolute error tolerance (optional, default=1e-10)
            MaxHalf: Maximum sub-step iterations (optional, default=15)
            
        Example:
            ops.uniaxialMaterial('ViscousDamper', 1, 1000.0, 50.0, 0.5)
            ops.uniaxialMaterial('ViscousDamper', 2, 1000.0, 50.0, 0.5, 0.1, 1, 1e-6, 1e-10, 15)
        """
        ...

    # BilinearOilDamper Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["BilinearOilDamper"], matTag: int, K_el: float, Cd: float, Fr: Optional[float] = None, p: Optional[float] = None, LGap: Optional[float] = None, NM: Optional[int] = None, RelTol: Optional[float] = None, AbsTol: Optional[float] = None, MaxHalf: Optional[int] = None) -> None:
        """Define BilinearOilDamper uniaxial material with relief valve
        
        Args:
            material_type: Material type 'BilinearOilDamper'
            matTag: Unique material identifier
            K_el: Elastic stiffness of linear spring
            Cd: Damping coefficient
            Fr: Damper relief load (optional, default=1.0)
            p: Post-relief viscous damping coefficient ratio (optional, default=1.0)
            LGap: Gap length due to pin tolerance (optional, default=0.0)
            NM: Numerical algorithm (1=Dormand-Prince54, 2=Adams-Bashforth-Moulton, 3=Rosenbrock, optional, default=1)
            RelTol: Relative error tolerance (optional, default=1e-6)
            AbsTol: Absolute error tolerance (optional, default=1e-10)
            MaxHalf: Maximum sub-step iterations (optional, default=15)
            
        Example:
            ops.uniaxialMaterial('BilinearOilDamper', 1, 1000.0, 50.0)
            ops.uniaxialMaterial('BilinearOilDamper', 2, 1000.0, 50.0, 10.0, 0.5, 0.1, 1, 1e-6, 1e-10, 15)
        """
        ...

    # Bilin Material (Modified Ibarra-Medina-Krawinkler with Bilinear Response)
    @overload
    def uniaxialMaterial(self, material_type: Literal["Bilin"], matTag: int, K0: float, as_Plus: float, as_Neg: float, My_Plus: float, My_Neg: float, Lamda_S: float, Lamda_C: float, Lamda_A: float, Lamda_K: float, c_S: float, c_C: float, c_A: float, c_K: float, theta_p_Plus: float, theta_p_Neg: float, theta_pc_Plus: float, theta_pc_Neg: float, Res_Pos: float, Res_Neg: float, theta_u_Plus: float, theta_u_Neg: float, D_Plus: float, D_Neg: float, nFactor: Optional[float] = None) -> None:
        """Define Bilin uniaxial material (Modified Ibarra-Krawinkler deterioration model with bilinear response)
        
        Args:
            material_type: Material type 'Bilin'
            matTag: Unique material identifier
            K0: Elastic stiffness
            as_Plus: Strain hardening ratio for positive loading direction
            as_Neg: Strain hardening ratio for negative loading direction
            My_Plus: Effective yield strength for positive loading direction
            My_Neg: Effective yield strength for negative loading direction (negative value)
            Lamda_S: Cyclic deterioration parameter for strength deterioration
            Lamda_C: Cyclic deterioration parameter for post-capping strength deterioration
            Lamda_A: Cyclic deterioration parameter for acceleration reloading stiffness deterioration
            Lamda_K: Cyclic deterioration parameter for unloading stiffness deterioration
            c_S: Rate of strength deterioration (default=1.0)
            c_C: Rate of post-capping strength deterioration (default=1.0)
            c_A: Rate of accelerated reloading deterioration (default=1.0)
            c_K: Rate of unloading stiffness deterioration (default=1.0)
            theta_p_Plus: Pre-capping rotation for positive loading direction
            theta_p_Neg: Pre-capping rotation for negative loading direction (positive value)
            theta_pc_Plus: Post-capping rotation for positive loading direction
            theta_pc_Neg: Post-capping rotation for negative loading direction (positive value)
            Res_Pos: Residual strength ratio for positive loading direction
            Res_Neg: Residual strength ratio for negative loading direction (positive value)
            theta_u_Plus: Ultimate rotation capacity for positive loading direction
            theta_u_Neg: Ultimate rotation capacity for negative loading direction (positive value)
            D_Plus: Rate of cyclic deterioration in positive loading direction
            D_Neg: Rate of cyclic deterioration in negative loading direction
            nFactor: Elastic stiffness amplification factor (optional, default=0.0)
            
        Example:
            ops.uniaxialMaterial('Bilin', 1, 1000.0, 0.03, 0.03, 400.0, -400.0, 1000.0, 1000.0, 1000.0, 1000.0, 1.0, 1.0, 1.0, 1.0, 0.05, 0.05, 0.3, 0.3, 0.2, 0.2, 0.4, 0.4, 1.0, 1.0)
        """
        ...

    # ModIMKPeakOriented Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["ModIMKPeakOriented"], matTag: int, K0: float, as_Plus: float, as_Neg: float, My_Plus: float, My_Neg: float, Lamda_S: float, Lamda_C: float, Lamda_A: float, Lamda_K: float, c_S: float, c_C: float, c_A: float, c_K: float, theta_p_Plus: float, theta_p_Neg: float, theta_pc_Plus: float, theta_pc_Neg: float, Res_Pos: float, Res_Neg: float, theta_u_Plus: float, theta_u_Neg: float, D_Plus: float, D_Neg: float) -> None:
        """Define ModIMKPeakOriented uniaxial material (Modified Ibarra-Medina-Krawinkler with peak-oriented response)
        
        Args:
            material_type: Material type 'ModIMKPeakOriented'
            matTag: Unique material identifier
            K0: Elastic stiffness
            as_Plus: Strain hardening ratio for positive loading direction
            as_Neg: Strain hardening ratio for negative loading direction
            My_Plus: Effective yield strength for positive loading direction
            My_Neg: Effective yield strength for negative loading direction (negative value)
            Lamda_S: Cyclic deterioration parameter for strength deterioration
            Lamda_C: Cyclic deterioration parameter for post-capping strength deterioration
            Lamda_A: Cyclic deterioration parameter for accelerated reloading stiffness deterioration
            Lamda_K: Cyclic deterioration parameter for unloading stiffness deterioration
            c_S: Rate of strength deterioration (default=1.0)
            c_C: Rate of post-capping strength deterioration (default=1.0)
            c_A: Rate of accelerated reloading deterioration (default=1.0)
            c_K: Rate of unloading stiffness deterioration (default=1.0)
            theta_p_Plus: Pre-capping rotation for positive loading direction
            theta_p_Neg: Pre-capping rotation for negative loading direction (positive value)
            theta_pc_Plus: Post-capping rotation for positive loading direction
            theta_pc_Neg: Post-capping rotation for negative loading direction (positive value)
            Res_Pos: Residual strength ratio for positive loading direction
            Res_Neg: Residual strength ratio for negative loading direction (positive value)
            theta_u_Plus: Ultimate rotation capacity for positive loading direction
            theta_u_Neg: Ultimate rotation capacity for negative loading direction (positive value)
            D_Plus: Rate of cyclic deterioration in positive loading direction
            D_Neg: Rate of cyclic deterioration in negative loading direction
            
        Example:
            ops.uniaxialMaterial('ModIMKPeakOriented', 1, 1000.0, 0.03, 0.03, 400.0, -400.0, 1000.0, 1000.0, 1000.0, 1000.0, 1.0, 1.0, 1.0, 1.0, 0.05, 0.05, 0.3, 0.3, 0.2, 0.2, 0.4, 0.4, 1.0, 1.0)
        """
        ...

    # ModIMKPinching Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["ModIMKPinching"], matTag: int, K0: float, as_Plus: float, as_Neg: float, My_Plus: float, My_Neg: float, FprPos: float, FprNeg: float, A_pinch: float, Lamda_S: float, Lamda_C: float, Lamda_A: float, Lamda_K: float, c_S: float, c_C: float, c_A: float, c_K: float, theta_p_Plus: float, theta_p_Neg: float, theta_pc_Plus: float, theta_pc_Neg: float, Res_Pos: float, Res_Neg: float, theta_u_Plus: float, theta_u_Neg: float, D_Plus: float, D_Neg: float) -> None:
        """Define ModIMKPinching uniaxial material (Modified Ibarra-Medina-Krawinkler with pinched response)
        
        Args:
            material_type: Material type 'ModIMKPinching'
            matTag: Unique material identifier
            K0: Elastic stiffness
            as_Plus: Strain hardening ratio for positive loading direction
            as_Neg: Strain hardening ratio for negative loading direction
            My_Plus: Effective yield strength for positive loading direction
            My_Neg: Effective yield strength for negative loading direction (negative value)
            FprPos: Ratio of reloading force to maximum historic deformation force (positive direction)
            FprNeg: Ratio of reloading force to maximum historic deformation force (negative direction)
            A_pinch: Ratio of reloading stiffness
            Lamda_S: Cyclic deterioration parameter for strength deterioration
            Lamda_C: Cyclic deterioration parameter for post-capping strength deterioration
            Lamda_A: Cyclic deterioration parameter for accelerated reloading stiffness deterioration
            Lamda_K: Cyclic deterioration parameter for unloading stiffness deterioration
            c_S: Rate of strength deterioration (default=1.0)
            c_C: Rate of post-capping strength deterioration (default=1.0)
            c_A: Rate of accelerated reloading deterioration (default=1.0)
            c_K: Rate of unloading stiffness deterioration (default=1.0)
            theta_p_Plus: Pre-capping rotation for positive loading direction
            theta_p_Neg: Pre-capping rotation for negative loading direction (positive value)
            theta_pc_Plus: Post-capping rotation for positive loading direction
            theta_pc_Neg: Post-capping rotation for negative loading direction (positive value)
            Res_Pos: Residual strength ratio for positive loading direction
            Res_Neg: Residual strength ratio for negative loading direction (positive value)
            theta_u_Plus: Ultimate rotation capacity for positive loading direction
            theta_u_Neg: Ultimate rotation capacity for negative loading direction (positive value)
            D_Plus: Rate of cyclic deterioration in positive loading direction
            D_Neg: Rate of cyclic deterioration in negative loading direction
            
        Example:
            ops.uniaxialMaterial('ModIMKPinching', 1, 1000.0, 0.03, 0.03, 400.0, -400.0, 0.5, 0.5, 0.25, 1000.0, 1000.0, 1000.0, 1000.0, 1.0, 1.0, 1.0, 1.0, 0.05, 0.05, 0.3, 0.3, 0.2, 0.2, 0.4, 0.4, 1.0, 1.0)
        """
        ...

    # SAWS Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["SAWS"], matTag: int, F0: float, FI: float, DU: float, S0: float, R1: float, R2: float, R3: float, R4: float, alpha: float, beta: float) -> None:
        """Define SAWS uniaxial material for wood frame hysteretic behavior
        
        Args:
            material_type: Material type 'SAWS'
            matTag: Unique material identifier
            F0: Intercept strength of shear wall spring element for asymptotic line (F0 > FI > 0)
            FI: Intercept strength for pinching branch of hysteretic curve (FI > 0)
            DU: Spring element displacement at ultimate load (DU > 0)
            S0: Initial stiffness of shear wall spring element (S0 > 0)
            R1: Stiffness ratio of asymptotic line (0 < R1 < 1.0)
            R2: Stiffness ratio of descending branch (R2 < 0)
            R3: Stiffness ratio of unloading branch (R3 ≤ 1)
            R4: Stiffness ratio of pinching branch (R4 > 0)
            alpha: Stiffness degradation parameter for shear wall (alpha > 0)
            beta: Stiffness degradation parameter (beta > 0)
            
        Example:
            ops.uniaxialMaterial('SAWS', 1, 100.0, 50.0, 10.0, 1000.0, 0.4, -0.1, 0.8, 0.2, 0.5, 0.3)
        """
        ...

    # BarSlip Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["BarSlip"], matTag: int, fc: float, fy: float, Es: float, fu: float, Eh: float, db: float, ld: float, nb: int, depth: float, height: float, ancLratio: Optional[float] = None, bsFlag: str = ..., type: str = ..., damage: Optional[str] = None, unit: Optional[str] = None) -> None:
        """Define BarSlip uniaxial material for reinforcing bar anchored in beam-column joint
        
        Args:
            material_type: Material type 'BarSlip'
            matTag: Unique material identifier
            fc: Compressive strength of concrete
            fy: Yield strength of reinforcing steel
            Es: Modulus of elasticity of reinforcing steel
            fu: Ultimate strength of reinforcing steel
            Eh: Hardening modulus of reinforcing steel
            db: Diameter of reinforcing steel
            ld: Development length of reinforcing steel
            nb: Number of anchored bars
            depth: Member dimension perpendicular to plane of paper
            height: Height of flexural member perpendicular to reinforcing steel direction
            ancLratio: Ratio of anchorage length to joint dimension (optional, default=1.0)
            bsFlag: Relative bond strength ('Strong' or 'Weak')
            type: Reinforcing bar placement ('beamtop', 'beambot', or 'column')
            damage: Damage type ('Damage' or 'NoDamage', optional, default='Damage')
            unit: Unit system ('psi', 'MPa', 'Pa', 'psf', 'ksi', 'ksf', optional, default='psi'/'MPa')
            
        Example:
            ops.uniaxialMaterial('BarSlip', 1, 4000.0, 60000.0, 29000000.0, 90000.0, 1000000.0, 0.75, 24.0, 4, 24.0, 18.0, 1.0, 'Strong', 'beamtop')
        """
        ...

    # Bond_SP01 Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Bond_SP01"], matTag: int, Fy: float, Sy: float, Fu: float, Su: float, b: float, R: float) -> None:
        """Define Bond_SP01 uniaxial material for strain penetration of fully anchored steel bars
        
        Args:
            material_type: Material type 'Bond_SP01'
            matTag: Unique material identifier
            Fy: Yield strength of reinforcement steel
            Sy: Rebar slip at member interface under yield stress
            Fu: Ultimate strength of reinforcement steel
            Su: Rebar slip at loaded end at bar fracture strength
            b: Initial hardening ratio in monotonic slip vs. bar stress response (0.3~0.5)
            R: Pinching factor for cyclic slip vs. bar response (0.5~1.0)
            
        Example:
            ops.uniaxialMaterial('Bond_SP01', 1, 60000.0, 0.1, 90000.0, 1.0, 0.4, 0.8)
        """
        ...

    # Fatigue Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Fatigue"], matTag: int, otherTag: int, *args: Any) -> None:
        """Define Fatigue uniaxial material using rainflow cycle counting
        
        Args:
            material_type: Material type 'Fatigue'
            matTag: Unique material identifier
            otherTag: Tag of material being wrapped
            args: Optional parameters: '-E0', E0, '-m', m, '-min', min, '-max', max
            
        Example:
            ops.uniaxialMaterial('Fatigue', 1, 2)
            ops.uniaxialMaterial('Fatigue', 2, 3, '-E0', 0.191, '-m', -0.458, '-min', -1e16, '-max', 1e16)
        """
        ...

    # ImpactMaterial 
    @overload
    def uniaxialMaterial(self, material_type: Literal["ImpactMaterial"], matTag: int, K1: float, K2: float, sigy: float, gap: float) -> None:
        """Define ImpactMaterial uniaxial material
        
        Args:
            material_type: Material type 'ImpactMaterial'
            matTag: Unique material identifier
            K1: Initial stiffness
            K2: Secondary stiffness
            sigy: Yield displacement
            gap: Initial gap
            
        Example:
            ops.uniaxialMaterial('ImpactMaterial', 1, 1000.0, 100.0, 0.1, 0.01)
        """
        ...

    # HyperbolicGapMaterial
    @overload
    def uniaxialMaterial(self, material_type: Literal["HyperbolicGapMaterial"], matTag: int, Kmax: float, Kur: float, Rf: float, Fult: float, gap: float) -> None:
        """Define HyperbolicGapMaterial uniaxial material (compression-only gap material)
        
        Args:
            material_type: Material type 'HyperbolicGapMaterial'
            matTag: Unique material identifier
            Kmax: Initial stiffness
            Kur: Unloading/reloading stiffness
            Rf: Failure ratio
            Fult: Ultimate (maximum) passive resistance (input as negative)
            gap: Initial gap (input as negative)
            
        Example:
            ops.uniaxialMaterial('HyperbolicGapMaterial', 1, 20300.0, 20300.0, 0.7, -326.0, -0.0254)
        """
        ...

    # LimitState Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["LimitState"], matTag: int, s1p: float, e1p: float, s2p: float, e2p: float, s3p: float, e3p: float, s1n: float, e1n: float, s2n: float, e2n: float, s3n: float, e3n: float, pinchX: float, pinchY: float, damage1: float, damage2: float, beta: float, curveTag: int, curveType: int) -> None:
        """Define LimitState uniaxial material with hysteretic behavior and limit curve
        
        Args:
            material_type: Material type 'LimitState'
            matTag: Unique material identifier
            s1p, e1p: Stress and strain at first point of positive envelope
            s2p, e2p: Stress and strain at second point of positive envelope
            s3p, e3p: Stress and strain at third point of positive envelope
            s1n, e1n: Stress and strain at first point of negative envelope
            s2n, e2n: Stress and strain at second point of negative envelope
            s3n, e3n: Stress and strain at third point of negative envelope
            pinchX: Pinching factor for strain during reloading
            pinchY: Pinching factor for stress during reloading
            damage1: Damage due to ductility: D1(m-1)
            damage2: Damage due to energy: D2(Ei/Eult)
            beta: Power for degraded unloading stiffness based on ductility
            curveTag: Tag for limit curve defining limit surface
            curveType: Type of limit curve (0=no curve, 1=axial curve, other=any integer)
            
        Example:
            ops.uniaxialMaterial('LimitState', 1, 400.0, 0.002, 500.0, 0.02, 500.0, 0.1, -400.0, -0.002, -500.0, -0.02, -500.0, -0.1, 1.0, 1.0, 0.0, 0.0, 0.0, 1, 1)
        """
        ...

    # MinMax Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["MinMax"], matTag: int, otherTag: int, *args: Any) -> None:
        """Define MinMax uniaxial material with strain limits
        
        Args:
            material_type: Material type 'MinMax'
            matTag: Unique material identifier
            otherTag: Tag of other material
            args: Optional parameters: '-min', minStrain, '-max', maxStrain
            
        Example:
            ops.uniaxialMaterial('MinMax', 1, 2)
            ops.uniaxialMaterial('MinMax', 2, 3, '-min', -0.01, '-max', 0.02)
        """
        ...

    # ElasticBilin Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["ElasticBilin"], matTag: int, EP1: float, EP2: float, epsP2: float, EN1: Optional[float] = None, EN2: Optional[float] = None, epsN2: Optional[float] = None) -> None:
        """Define ElasticBilin uniaxial material (elastic bilinear)
        
        Args:
            material_type: Material type 'ElasticBilin'
            matTag: Unique material identifier
            EP1: Tangent in tension for strains: 0 <= strains <= epsP2
            EP2: Tangent in tension for strains > epsP2
            epsP2: Strain at which material changes tangent in tension
            EN1: Tangent in compression for strains: 0 < strains <= epsN2 (optional, default=EP1)
            EN2: Tangent in compression for strains < epsN2 (optional, default=EP2)
            epsN2: Strain at which material changes tangent in compression (optional, default=-epsP2)
            
        Example:
            ops.uniaxialMaterial('ElasticBilin', 1, 29000.0, 1000.0, 0.005)
            ops.uniaxialMaterial('ElasticBilin', 2, 29000.0, 1000.0, 0.005, 25000.0, 800.0, -0.004)
        """
        ...

    # ElasticMultiLinear Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["ElasticMultiLinear"], matTag: int, *args: Any) -> None:
        """Define ElasticMultiLinear uniaxial material (multi-linear elastic)
        
        Args:
            material_type: Material type 'ElasticMultiLinear'
            matTag: Unique material identifier
            args: Parameters: eta (optional), '-strain', strain_list, '-stress', stress_list
            
        Example:
            ops.uniaxialMaterial('ElasticMultiLinear', 1, '-strain', [-0.01, 0.0, 0.01], '-stress', [-400.0, 0.0, 400.0])
            ops.uniaxialMaterial('ElasticMultiLinear', 2, 0.01, '-strain', [-0.01, 0.0, 0.01], '-stress', [-400.0, 0.0, 400.0])
        """
        ...

    # MultiLinear Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["MultiLinear"], matTag: int, *pts: float) -> None:
        """Define MultiLinear uniaxial material
        
        Args:
            material_type: Material type 'MultiLinear'
            matTag: Unique material identifier
            pts: List of strain and stress points [strain1, stress1, strain2, stress2, ...]
            
        Example:
            ops.uniaxialMaterial('MultiLinear', 1, -0.01, -400.0, 0.0, 0.0, 0.002, 400.0, 0.01, 500.0)
        """
        ...

    # InitStrainMaterial (Initial Strain Material)
    @overload
    def uniaxialMaterial(self, material_type: Literal["InitStrainMaterial"], matTag: int, otherTag: int, initStrain: float) -> None:
        """Define InitStrainMaterial uniaxial material with initial strain
        
        Args:
            material_type: Material type 'InitStrainMaterial'
            matTag: Unique material identifier
            otherTag: Tag of other material
            initStrain: Initial strain
            
        Example:
            ops.uniaxialMaterial('InitStrainMaterial', 1, 2, 0.001)
        """
        ...

    # InitStressMaterial (Initial Stress Material)
    @overload
    def uniaxialMaterial(self, material_type: Literal["InitStressMaterial"], matTag: int, otherTag: int, initStress: float) -> None:
        """Define InitStressMaterial uniaxial material with initial stress
        
        Args:
            material_type: Material type 'InitStressMaterial'
            matTag: Unique material identifier
            otherTag: Tag of other material
            initStress: Initial stress
            
        Example:
            ops.uniaxialMaterial('InitStressMaterial', 1, 2, 100.0)
        """
        ...

    # PathIndependent Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["PathIndependent"], matTag: int, OtherTag: int) -> None:
        """Define PathIndependent uniaxial material
        
        Args:
            material_type: Material type 'PathIndependent'
            matTag: Unique material identifier
            OtherTag: Tag of pre-defined material
            
        Example:
            ops.uniaxialMaterial('PathIndependent', 1, 2)
        """
        ...

    # Pinching4 Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Pinching4"], matTag: int, *args: Any) -> None:
        """Define Pinching4 uniaxial material with pinched load-deformation response and degradation
        
        Args:
            material_type: Material type 'Pinching4'
            matTag: Unique material identifier
            args: Force and deformation envelope points, degradation parameters
                  Format: ePf1, ePd1, ePf2, ePd2, ePf3, ePd3, ePf4, ePd4, 
                         [eNf1, eNd1, eNf2, eNd2, eNf3, eNd3, eNf4, eNd4],
                         rDispP, rForceP, uForceP, [rDispN, rForceN, uForceN],
                         gK1, gK2, gK3, gK4, gKLim, gD1, gD2, gD3, gD4, gDLim,
                         gF1, gF2, gF3, gF4, gFLim, gE, dmgType
            
        Example:
            ops.uniaxialMaterial('Pinching4', 1, 400.0, 0.005, 500.0, 0.02, 500.0, 0.1, 400.0, 0.2, -400.0, -0.005, -500.0, -0.02, -500.0, -0.1, -400.0, -0.2, 0.5, 0.25, 0.05, 0.5, 0.25, 0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 25.0, 'cycle')
        """
        ...

    # ECC01 Material (Engineered Cementitious Composites)
    @overload
    def uniaxialMaterial(self, material_type: Literal["ECC01"], matTag: int, sigt0: float, epst0: float, sigt1: float, epst1: float, epst2: float, sigc0: float, epsc0: float, epsc1: float, alphaT1: float, alphaT2: float, alphaC: float, alphaCU: float, betaT: float, betaC: float) -> None:
        """Define ECC01 uniaxial material for Engineered Cementitious Composites
        
        Args:
            material_type: Material type 'ECC01'
            matTag: Unique material identifier
            sigt0: Tensile cracking stress
            epst0: Strain at tensile cracking stress
            sigt1: Peak tensile stress
            epst1: Strain at peak tensile stress
            epst2: Ultimate tensile strain
            sigc0: Compressive strength
            epsc0: Strain at compressive strength
            epsc1: Ultimate compressive strain
            alphaT1: Exponent of unloading curve in tensile strain hardening region
            alphaT2: Exponent of unloading curve in tensile softening region
            alphaC: Exponent of unloading curve in compressive softening
            alphaCU: Exponent of compressive softening curve (use 1 for linear softening)
            betaT: Parameter to determine permanent strain in tension
            betaC: Parameter to determine permanent strain in compression
            
        Example:
            ops.uniaxialMaterial('ECC01', 1, 3.0, 0.0001, 5.0, 0.001, 0.05, -30.0, -0.002, -0.01, 0.4, 0.1, 0.4, 1.0, 0.05, 0.3)
        """
        ...

    # SelfCentering Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["SelfCentering"], matTag: int, k1: float, k2: float, sigAct: float, beta: float, epsSlip: Optional[float] = None, epsBear: Optional[float] = None, rBear: Optional[float] = None) -> None:
        """Define SelfCentering uniaxial material with flag-shaped behavior
        
        Args:
            material_type: Material type 'SelfCentering'
            matTag: Unique material identifier
            k1: Initial stiffness
            k2: Post-activation stiffness (0 < k2 < k1)
            sigAct: Forward activation stress/force
            beta: Ratio of forward to reverse activation stress/force
            epsSlip: Slip strain/deformation (optional, default=0, no slippage if 0)
            epsBear: Bearing strain/deformation (optional, default=0, no bearing if 0)
            rBear: Ratio of bearing stiffness to initial stiffness k1 (optional, default=k1)
            
        Example:
            ops.uniaxialMaterial('SelfCentering', 1, 1000.0, 100.0, 400.0, 0.5)
            ops.uniaxialMaterial('SelfCentering', 2, 1000.0, 100.0, 400.0, 0.5, 0.01, 0.1, 2.0)
        """
        ...

    # Viscous Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Viscous"], matTag: int, C: float, alpha: float) -> None:
        """Define Viscous uniaxial material with stress = C*(strain-rate)^alpha
        
        Args:
            material_type: Material type 'Viscous'
            matTag: Unique material identifier
            C: Damping coefficient
            alpha: Power factor (=1 means linear damping)
            
        Note:
            This material can only be assigned to truss and zeroLength elements.
            Cannot be combined in parallel/series with other materials.
            
        Example:
            ops.uniaxialMaterial('Viscous', 1, 50.0, 1.0)
            ops.uniaxialMaterial('Viscous', 2, 100.0, 0.5)
        """
        ...

    # BoucWen Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["BoucWen"], matTag: int, alpha: float, ko: float, n: float, gamma: float, beta: float, Ao: float, deltaA: float, deltaNu: float, deltaEta: float) -> None:
        """Define BoucWen uniaxial material with smooth hysteretic behavior and degradation
        
        Args:
            material_type: Material type 'BoucWen'
            matTag: Unique material identifier
            alpha: Ratio of post-yield stiffness to initial elastic stiffness (0 < alpha < 1)
            ko: Initial elastic stiffness
            n: Parameter controlling transition from linear to nonlinear range (n ≥ 1)
            gamma: Parameter controlling shape of hysteresis loop
            beta: Parameter controlling shape of hysteresis loop
            Ao: Parameter controlling tangent stiffness
            deltaA: Parameter controlling tangent stiffness
            deltaNu: Parameter controlling material degradation
            deltaEta: Parameter controlling material degradation
            
        Example:
            ops.uniaxialMaterial('BoucWen', 1, 0.1, 1000.0, 1.0, 0.5, 0.5, 1.0, 0.0, 0.0, 0.0)
        """
        ...

    # BWBN Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["BWBN"], matTag: int, alpha: float, ko: float, n: float, gamma: float, beta: float, Ao: float, q: float, zetas: float, p: float, Shi: float, deltaShi: float, lambda_val: float, tol: float, maxIter: int) -> None:
        """Define BWBN uniaxial material with Bouc-Wen pinching hysteretic behavior
        
        Args:
            material_type: Material type 'BWBN'
            matTag: Unique material identifier
            alpha: Ratio of post-yield stiffness to initial elastic stiffness (0 < alpha < 1)
            ko: Initial elastic stiffness
            n: Parameter controlling transition from linear to nonlinear range (n ≥ 1)
            gamma: Parameter controlling shape of hysteresis loop
            beta: Parameter controlling shape of hysteresis loop
            Ao: Parameter controlling tangent stiffness
            q: Parameter controlling pinching
            zetas: Parameter controlling pinching
            p: Parameter controlling pinching
            Shi: Parameter controlling pinching
            deltaShi: Parameter controlling pinching
            lambda_val: Parameter controlling pinching
            tol: Tolerance
            maxIter: Maximum iterations
            
        Example:
            ops.uniaxialMaterial('BWBN', 1, 0.1, 1000.0, 1.0, 0.5, 0.5, 1.0, 0.25, 0.5, 1000.0, 0.25, 0.025, 0.5, 1e-8, 50)
        """
        ...

    # KikuchiAikenHDR Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["KikuchiAikenHDR"], matTag: int, tp: str, ar: float, hr: float, *args: Any) -> None:
        """Define KikuchiAikenHDR uniaxial material for high damping rubber bearings
        
        Args:
            material_type: Material type 'KikuchiAikenHDR'
            matTag: Unique material identifier
            tp: Rubber type ('X0.6', 'X0.6-0MPa', 'X0.4', 'X0.4-0MPa', 'X0.3', 'X0.3-0MPa')
            ar: Area of rubber [m^2] (SI units required)
            hr: Total thickness of rubber [m] (SI units required)
            args: Optional parameters: '-coGHU', cg, ch, cu, '-coMSS', rs, rf
            
        Example:
            ops.uniaxialMaterial('KikuchiAikenHDR', 1, 'X0.6', 1.0, 0.1)
            ops.uniaxialMaterial('KikuchiAikenHDR', 2, 'X0.4', 1.0, 0.1, '-coGHU', 1.0, 1.0, 1.0, '-coMSS', 0.25, 0.1989)
        """
        ...

    # KikuchiAikenLRB Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["KikuchiAikenLRB"], matTag: int, type: int, ar: float, hr: float, gr: float, ap: float, tp: float, alph: float, beta: float, *args: Any) -> None:
        """Define KikuchiAikenLRB uniaxial material for lead-rubber bearings
        
        Args:
            material_type: Material type 'KikuchiAikenLRB'
            matTag: Unique material identifier
            type: Rubber type (1=lead-rubber bearing up to 400% shear strain)
            ar: Area of rubber [m^2] (SI units required)
            hr: Total thickness of rubber [m] (SI units required)
            gr: Shear modulus of rubber [N/m^2] (SI units required)
            ap: Area of lead plug [m^2] (SI units required)
            tp: Yield stress of lead plug [N/m^2] (SI units required)
            alph: Shear modulus of lead plug [N/m^2] (SI units required)
            beta: Ratio of initial stiffness to yielding stiffness
            args: Optional parameters: '-T', temp, '-coKQ', rk, rq, '-coMSS', rs, rf
            
        Example:
            ops.uniaxialMaterial('KikuchiAikenLRB', 1, 1, 1.0, 0.1, 400000.0, 0.05, 10000000.0, 130000000.0, 10.0)
            ops.uniaxialMaterial('KikuchiAikenLRB', 2, 1, 1.0, 0.1, 400000.0, 0.05, 10000000.0, 130000000.0, 10.0, '-T', 23.0, '-coKQ', 1.0, 1.0)
        """
        ...

    # AxialSp Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["AxialSp"], matTag: int, sce: float, fty: float, fcy: float, *args: float) -> None:
        """Define AxialSp uniaxial material for axial stress-strain curve of elastomeric bearings
        
        Args:
            material_type: Material type 'AxialSp'
            matTag: Unique material identifier
            sce: Compressive modulus
            fty: Yield stress under tension (fty > 0)
            fcy: Yield stress under compression (fcy < 0)
            args: Optional parameters: bte, bty, bcy, fcr
                  bte: Reduction rate for tensile elastic range (0 ≤ bty < bte ≤ 1.0)
                  bty: Reduction rate for tensile yielding (0 ≤ bty < bte ≤ 1.0)
                  bcy: Reduction rate for compressive yielding (0 ≤ bcy ≤ 1.0)
                  fcr: Target point stress (fcy ≤ fcr ≤ 0.0)
            
        Example:
            ops.uniaxialMaterial('AxialSp', 1, 1000.0, 10.0, -50.0)
            ops.uniaxialMaterial('AxialSp', 2, 1000.0, 10.0, -50.0, 0.8, 0.5, 0.3, -10.0)
        """
        ...

    # AxialSpHD Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["AxialSpHD"], matTag: int, sce: float, fty: float, fcy: float, *args: float) -> None:
        """Define AxialSpHD uniaxial material for elastomeric bearings with hardening behavior
        
        Args:
            material_type: Material type 'AxialSpHD'
            matTag: Unique material identifier
            sce: Compressive modulus
            fty: Yield stress under tension (fty > 0)
            fcy: Yield stress under compression (fcy < 0)
            args: Optional parameters: bte, bty, bth, bcy, fcr, ath
                  bte: Reduction rate for tensile elastic range
                  bty: Reduction rate for tensile yielding
                  bth: Reduction rate for tensile hardening
                  bcy: Reduction rate for compressive yielding
                  fcr: Target point stress
                  ath: Hardening strain ratio to yield strain
            
        Example:
            ops.uniaxialMaterial('AxialSpHD', 1, 1000.0, 10.0, -50.0)
            ops.uniaxialMaterial('AxialSpHD', 2, 1000.0, 10.0, -50.0, 0.8, 0.5, 0.4, 0.3, -10.0, 2.0)
        """
        ...

    # PinchingLimitStateMaterial - Mode 1 (Direct Input)
    @overload
    def uniaxialMaterial(self, material_type: Literal["PinchingLimitStateMaterial"], matTag: int, nodeT: int, nodeB: int, driftAxis: int, Kelas: float, crvTyp: int, crvTag: int, YpinchUPN: float, YpinchRPN: float, XpinchRPN: float, YpinchUNP: float, YpinchRNP: float, XpinchRNP: float, dmgStrsLimE: float, dmgDispMax: float, dmgE1: float, dmgE2: float, dmgE3: float, dmgE4: float, dmgELim: float, dmgR1: float, dmgR2: float, dmgR3: float, dmgR4: float, dmgRLim: float, dmgRCyc: float, dmgS1: float, dmgS2: float, dmgS3: float, dmgS4: float, dmgSLim: float, dmgSCyc: float) -> None:
        """Define PinchingLimitStateMaterial uniaxial material (Mode 1: Direct Input)
        
        Args:
            material_type: Material type 'PinchingLimitStateMaterial'
            matTag: Unique material identifier
            nodeT: Node tag at extreme end of flexural frame member
            nodeB: Node tag at other extreme end of flexural frame member
            driftAxis: Drift axis for lateral-strength degradation (1=x, 2=y, 3=z)
            Kelas: Initial material elastic stiffness (>0)
            crvTyp: Type of limit curve (0=none, 1=axial, 2=RotationShearCurve)
            crvTag: Tag for limit curve object
            YpinchUPN: Unloading force pinching factor for negative direction (0-1)
            YpinchRPN: Reloading force pinching factor for negative direction (-1 to 1)
            XpinchRPN: Reloading displacement pinching factor for negative direction (-1 to 1)
            YpinchUNP: Unloading force pinching factor for positive direction (0-1)
            YpinchRNP: Reloading force pinching factor for positive direction (-1 to 1)
            XpinchRNP: Reloading displacement pinching factor for positive direction (-1 to 1)
            dmgStrsLimE: Force limit for elastic stiffness damage
            dmgDispMax: Ultimate drift at failure
            dmgE1, dmgE2, dmgE3, dmgE4: Elastic stiffness damage factors
            dmgELim: Elastic stiffness damage limit (0-1)
            dmgR1, dmgR2, dmgR3, dmgR4: Reloading stiffness damage factors
            dmgRLim: Reloading stiffness damage limit (0-1)
            dmgRCyc: Cyclic reloading stiffness damage index (0-1)
            dmgS1, dmgS2, dmgS3, dmgS4: Backbone strength damage factors
            dmgSLim: Backbone strength damage limit (0-1)
            dmgSCyc: Cyclic backbone strength damage index (0-1)
            
        Example:
            ops.uniaxialMaterial('PinchingLimitStateMaterial', 1, 1, 2, 1, 1000.0, 2, 1, 0.8, 0.5, 0.5, 0.8, 0.5, 0.5, 400.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        """
        ...

    # CFSWSWP Material (Wood-Sheathed Cold-Formed Steel Shear Wall Panel)
    @overload
    def uniaxialMaterial(self, material_type: Literal["CFSWSWP"], matTag: int, height: float, width: float, fut: float, tf: float, Ife: float, Ifi: float, ts: float, np: float, ds: float, Vs: float, sc: float, nc: float, type: int, openingArea: float, openingLength: float) -> None:
        """Define CFSWSWP uniaxial material for wood-sheathed cold-formed steel shear wall panel
        
        Args:
            material_type: Material type 'CFSWSWP'
            matTag: Unique material identifier
            height: SWP height [mm]
            width: SWP width [mm]
            fut: Tensile strength of framing members [MPa]
            tf: Framing thickness [mm]
            Ife: Moment of inertia of double end-stud [mm^4]
            Ifi: Moment of inertia of intermediate stud [mm^4]
            ts: Sheathing thickness [mm]
            np: Sheathing number (one or two sides sheathed)
            ds: Screws diameter [mm]
            Vs: Screws shear strength [N]
            sc: Screw spacing on SWP perimeter [mm]
            nc: Total number of screws on SWP perimeter
            type: Wood sheathing type (1=DFP, 2=OSB, 3=CSP)
            openingArea: Total area of openings [mm^2]
            openingLength: Cumulative length of openings [mm]
            
        Note:
            Results are in Newton and Meter units.
            
        Example:
            ops.uniaxialMaterial('CFSWSWP', 1, 2440.0, 1220.0, 345.0, 1.5, 1000000.0, 500000.0, 12.7, 1.0, 4.8, 1000.0, 150.0, 32.0, 2, 0.0, 0.0)
        """
        ...

    # CFSSSWP Material (Steel-Sheathed Cold-Formed Steel Shear Wall Panel)
    @overload
    def uniaxialMaterial(self, material_type: Literal["CFSSSWP"], matTag: int, height: float, width: float, fuf: float, fyf: float, tf: float, Af: float, fus: float, fys: float, ts: float, np: float, ds: float, Vs: float, sc: float, dt: float, openingArea: float, openingLength: float) -> None:
        """Define CFSSSWP uniaxial material for steel-sheathed cold-formed steel shear wall panel
        
        Args:
            material_type: Material type 'CFSSSWP'
            matTag: Unique material identifier
            height: SWP height [mm]
            width: SWP width [mm]
            fuf: Tensile strength of framing members [MPa]
            fyf: Yield strength of framing members [MPa]
            tf: Framing thickness [mm]
            Af: Framing cross section area [mm^2]
            fus: Tensile strength of steel sheet sheathing [MPa]
            fys: Yield strength of steel sheet sheathing [MPa]
            ts: Sheathing thickness [mm]
            np: Sheathing number (one or two sides sheathed)
            ds: Screws diameter [mm]
            Vs: Screws shear strength [N]
            sc: Screw spacing on SWP perimeter [mm]
            dt: Anchor bolt diameter [mm]
            openingArea: Total area of openings [mm^2]
            openingLength: Cumulative length of openings [mm]
            
        Note:
            Results are in Newton and Meter units.
            
        Example:
            ops.uniaxialMaterial('CFSSSWP', 1, 2440.0, 1220.0, 345.0, 230.0, 1.5, 150.0, 345.0, 230.0, 0.76, 1.0, 4.8, 1000.0, 150.0, 12.0, 0.0, 0.0)
        """
        ...

    # Backbone Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Backbone"], matTag: int, backboneTag: int) -> None:
        """Define Backbone uniaxial material using hysteretic backbone object
        
        Args:
            material_type: Material type 'Backbone'
            matTag: Unique material identifier
            backboneTag: Tag of predefined backbone function
            
        Note:
            This is a path-independent material with no state information stored.
            
        Example:
            ops.uniaxialMaterial('Backbone', 1, 1)
        """
        ...

    # Masonry Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Masonry"], matTag: int, Fm: float, Ft: float, Um: float, Uult: float, Ucl: float, Emo: float, L: float, a1: float, a2: float, D1: float, D2: float, Ach: float, Are: float, Ba: float, Gun: float, Gplu: float, Gplr: float, Exp1: float, Exp2: float, IENV: int) -> None:
        """Define Masonry uniaxial material with hysteretic constitutive model
        
        Args:
            material_type: Material type 'Masonry'
            matTag: Unique material identifier
            Fm: Compression strength of masonry (Fm < 0)
            Ft: Tension strength of masonry (Ft > 0)
            Um: Strain at maximum strength (Um < 0)
            Uult: Maximum compression strain (Uult < 0)
            Ucl: Crack closing strain (Ucl > 0)
            Emo: Initial elastic modulus
            L: Initial length (just add 1.0)
            a1: Initial strut area as ratio of initial area (=1)
            a2: Ratio of residual strut area to initial strut area
            D1: Strain where strut degradation starts (D1 < 0)
            D2: Strain where strut degradation ends (D2 < 0)
            Ach: Hysteresis parameter (0.3 to 0.6)
            Are: Strain reloading factor (0.2 to 0.4)
            Ba: Hysteresis parameter (1.5 to 2.0)
            Gun: Stiffness unloading factor (1.5 to 2.5)
            Gplu: Hysteresis parameter (0.5 to 0.7)
            Gplr: Hysteresis parameter (1.1 to 1.5)
            Exp1: Hysteresis parameter (1.5 to 2.0)
            Exp2: Hysteresis parameter (1.0 to 1.5)
            IENV: Envelope type (0=Sargin, 1=Parabolic)
            
        Example:
            ops.uniaxialMaterial('Masonry', 1, -10.0, 1.0, -0.003, -0.02, 0.001, 15000.0, 1.0, 1.0, 0.8, -0.005, -0.015, 0.4, 0.3, 1.8, 2.0, 0.6, 1.3, 1.8, 1.2, 0)
        """
        ...

    # Pipe Material
    @overload
    def uniaxialMaterial(self, material_type: Literal["Pipe"], matTag: int, nt: int, *args: float) -> None:
        """Define Pipe uniaxial material with temperature-dependent properties
        
        Args:
            material_type: Material type 'Pipe'
            matTag: Unique material identifier
            nt: Number of temperature points
            args: Temperature-dependent material properties as groups of (T, E, nu, alpT)
                  T: Temperature
                  E: Young's modulus
                  nu: Poisson's ratio
                  alpT: Thermal expansion coefficient
            
        Note:
            Should be used with Elastic Pipe Element.
            Properties are interpolated based on average element temperature.
            
        Example:
            ops.uniaxialMaterial('Pipe', 1, 2, 20.0, 200000.0, 0.3, 1.2e-5, 100.0, 180000.0, 0.32, 1.4e-5)
        """
        ...

    # Generic uniaxial material fallback
    @overload
    def uniaxialMaterial(
        self,
        material_type: Literal[
            "Elastic", "Steel02", "Steel4", "TDConcrete", "TDConcreteEXP",
            "TDConcreteMC10", "TDConcreteMC10NL", "ElasticPP", "ElasticPPGap",
            "ENT", "Hysteretic", "Parallel", "Series", "PySimple1", "QzSimple1",
            "PyLiq1", "TzSimple1", "QzSimple1", "PyLiq1", "TzLiq1", "QzLiq1",
            "Hardening", "Cast", "ViscousDamper", "BilinearOilDamper", "Bilin",
            "ModIMKPeakOriented", "ModIMKPinching", "SAWS", "BarSlip", "Bond_SP01",
            "Fatigue", "ImpactMaterial", "HyperbolicGapMaterial", "LimitState", "MinMax", "ElasticBilin",
            "ElasticMultiLinear", "MultiLinear", "InitStrainMaterial", "InitStressMaterial",
            "PathIndependent", "Pinching4", "ECC01", "SelfCentering", "Viscous", "BoucWen",
            "BWBN", "KikuchiAikenHDR", "KikuchiAikenLRB", "AxialSp", "AxialSpHD",
            "PinchingLimitStateMaterial", "CFSWSWP", "CFSSSWP", "Backbone", "Masonry", "Pipe"
        ],
        material_tag: int,
        *args: Any
        ) -> None:
        """Define uniaxial material (generic fallback)
        
        Args:
            material_type:
                # Steel materials
                "Steel01", "Steel02", "Steel4", "ReinforcingSteel", "Dodd_Restrepo",
                "RambergOsgoodSteel", "SteelMPF", "Steel01Thermal",

                # Concrete materials
                "Concrete01", "Concrete02", "Concrete04", "Concrete06", "Concrete07",
                "Concrete01WithSITC", "ConfinedConcrete01", "ConcreteD", "FRPConfinedConcrete",
                "FRPConfinedConcrete02", "ConcreteCM", "TDConcrete", "TDConcreteEXP",
                "TDConcreteMC10", "TDConcreteMC10NL",

                # Standard uniaxial materials
                "Elastic", "ElasticPP", "ElasticPPGap", "ENT", "Hysteretic", "Parallel", "Series",

                # PyTzQz uniaxial materials
                "PySimple1", "TzSimple1", "QzSimple1", "PyLiq1", "TzLiq1", "QzLiq1",

                # Other uniaxial materials
                "Hardening", "Cast", "ViscousDamper", "BilinearOilDamper", "Bilin",
                "ModIMKPeakOriented", "ModIMKPinching", "SAWS", "BarSlip", "Bond_SP01",
                "Fatigue", "ImpactMaterial", "HyperbolicGapMaterial", "LimitState", "MinMax", "ElasticBilin",
                "ElasticMultiLinear", "MultiLinear", "InitStrainMaterial", "InitStressMaterial",
                "PathIndependent", "Pinching4", "ECC01", "SelfCentering", "Viscous", "BoucWen",
                "BWBN", "KikuchiAikenHDR", "KikuchiAikenLRB", "AxialSp", "AxialSpHD",
                "PinchingLimitStateMaterial", "CFSWSWP", "CFSSSWP", "Backbone", "Masonry", "Pipe"
            material_tag: material tag
            args: Material properties
            
        Example:
            ops.uniaxialMaterial('Elastic', 1, 29000.0)

            ops.uniaxialMaterial('Steel01', 2, 60.0, 29000.0, 0.02)

            ops.uniaxialMaterial('Concrete01', 3, -4000.0, -0.002, -800.0, -0.006, 0.1, 400.0, 2000.0)

            ops.uniaxialMaterial('PySimple1', 4, 1, 100.0, 0.02, 0.3)

            ops.uniaxialMaterial('PyLiq1', 5, 1, 100.0, 0.02, 0.3, 0.0, 20.0, 101, 102)
        """
        ...