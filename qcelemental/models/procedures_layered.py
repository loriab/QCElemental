from enum import Enum
from typing import Any, Dict, List, Optional, Literal, Union

from pydantic import Field, field_validator, FieldValidationInfo

from .types import Array
from .common_models import ProtoModel, DriverEnum, Model, Provenance
from .molecule import Molecule
from .results import AtomicInput, AtomicResultProperties, AtomicResultProtocols, AtomicResult


class AtomicSpecification(ProtoModel):
    """Specification for a single point QC calculation"""

    keywords: Dict[str, Any] = Field({}, description="The program specific keywords to be used.")
    program: str = Field(..., description="The program for which the Specification is intended.")

    schema_name: Literal["qcschema_atomicspecification"] = "qcschema_atomicspecification"
    driver: DriverEnum = Field(..., description=DriverEnum.__doc__)
    model: Model = Field(..., description=Model.__doc__)
    protocols: AtomicResultProtocols = Field(AtomicResultProtocols(), description=AtomicResultProtocols.__doc__)


class BsseEnum(str, Enum):
    """Available basis-set superposition error (BSSE) treatments."""

    nocp = "nocp"  # plain supramolecular interaction energy
    cp = "cp"      # counterpoise correction
    vmfc = "vmfc"  # Valiron-Mayer function counterpoise


class ManyBodyKeywords(ProtoModel):

    bsse_type: List[BsseEnum] = Field(
        [BsseEnum.cp],
        description="Requested BSSE treatments. First in list determines which interaction or total "
            "energy/gradient/Hessian returned.",
    )
    return_total_data: Optional[bool] = Field(
        None,
        validate_default=True,
        description="When True, returns the total data (energy/gradient/Hessian) of the system, otherwise returns "
            "interaction data. Default is False for energies, True for gradients and Hessians. Note that the calculation "
            "of counterpoise corrected total energies implies the calculation of the energies of monomers in the monomer "
            "basis, hence specifying ``return_total_data = True`` may carry out more computations than "
            "``return_total_data = False``. For gradients and Hessians, ``return_total_data = False`` is rarely useful.",
    )
    short_circuit_mbe: bool = Field(
        False,
        description="When True, compute each n-body level in the many-body expansion up through ``max_nbody``. When "
            "False, only compute enough for the overall interaction energy. This keyword is irrelevant for a "
            "two-fragment system. But for the interaction energy of a three-fragment system, for example, 2-body "
            "subsystems can be skipped with ``mbe_intermediate_data= False``.",
    )  # TODO NYI psi-side ie_only
#ALT    max_nbody: int = Field(
#ALT        -1,
    max_nbody: Optional[int] = Field(
        None,
        validate_default=True,
        description="Maximum number of bodies to include in the many-body treatment. Possible: max_nbody <= nfragments. "
            "Default: max_nbody = nfragments.",
    )
    levels: Optional[Dict[Union[int, Literal["supersystem"]], str]] = Field(
        None,
        description="Dictionary of different levels of theory for different levels of expansion. Note that the primary "
            "method_string is not used when this keyword is given. ``supersystem`` computes all higher order n-body "
            "effects up to the number of fragments. Note that if both this and max_nbody are provided, they must be "
            "consistent. Examples: "
            "* {1: 'ccsd(t)', 2: 'mp2', 'supersystem': 'scf'} "
            "* {1: 2, 2: 'ccsd(t)/cc-pvdz', 3: 'mp2'} ",
    )
    embedding_charges: Dict[int, List[float]] = Field(
        {},
        description="Atom-centered point charges to be used on molecule fragments whose basis sets are not included in "
            "the computation. Keys: 1-based index of fragment. Values: list of atom charges for that fragment.",
        json_schema_extra={
            "shape": ["nfr", "<varies: nat in ifr>"],
        },
    )

    @field_validator("bsse_type", mode="before")
    @classmethod
    def set_bsse_type(cls, v: Any) -> List[BsseEnum]:
        if not isinstance(v, list):
            v = [v]
        # emulate ordered set
        return list(dict.fromkeys([bt.lower() for bt in v]))


#    molecule: Any = Field(..., description="The target molecule, if not the last molecule defined.")
#    basis: str = "(auto)"
#    method: str = "(auto)"
#    driver: DriverEnum = Field(..., description="The computation driver; i.e., energy, gradient, hessian.")
#    keywords: Dict[str, Any] = Field({}, description="The computation keywords/options.")



    #task_list: Dict[str, MBETaskComputers] = {}



class ManyBodySpecification(ProtoModel):
#class ManyBodySpecification(SpecificationBase):

    schema_name: Literal["qcschema_manybodyspecification"] = "qcschema_manybodyspecification"
    #provenance: Provenance = Field(Provenance(**provenance_stamp(__name__)), description=Provenance.__doc__)
    keywords: ManyBodyKeywords = Field(
        ...,
        description="The many-body-specific keywords to be used.",
    )
    #program: str = Field(..., description="The program for which the Specification is intended.")
    driver: DriverEnum = Field(
        ...,
        description="The computation driver; i.e., energy, gradient, hessian.",
    )
    specification: AtomicSpecification = Field(
        ...,
        description="??? TODO expand to cbs, fd",
    )

    #@field_validator("return_total_data") #, mode="before")
    #@classmethod
    #def set_return_total_data(cls, v: Any, info) -> List[BsseEnum]:
    #    raise ValueError("here")
    #    #if not isinstance(v, list):
    #    #    v = [v]
    #    ## emulate ordered set
    #    #return list(dict.fromkeys([bt.lower() for bt in v]))


class ManyBodyInput(ProtoModel):
#class ManyBodyInput(InputBase):

    schema_name: Literal["qcschema_manybodyinput"] = "qcschema_manybodyinput"
    #provenance: Provenance = Field(Provenance(**provenance_stamp(__name__)), description=Provenance.__doc__)
    specification: ManyBodySpecification = Field(
        ...,
        description="???",
    )
    molecule: Molecule = Field(
        ...,
        description="Target molecule for many body expansion (MBE) or interaction energy (IE) analysis.",
    )
#    nfragments: int = Field(
#        -1,
#        validate_default=True,
#        description="Number of distinct fragments comprising full molecular supersystem.",
#    )
#    max_nbody: int = Field(
#        -1,
#        validate_default=True,
#        description="Maximum number of bodies to include in the many-body treatment. Possible: max_nbody <= nfragments. "
#            "Default: max_nbody = nfragments.",
#    )
#    return_total_data: Optional[bool] = Field(
#        None,
#        validate_default=True,
#        description="When True, returns the total data (energy/gradient/Hessian) of the system, otherwise returns "
#            "interaction data. Default is False for energies, True for gradients and Hessians. Note that the calculation "
#            "of counterpoise corrected total energies implies the calculation of the energies of monomers in the monomer "
#            "basis, hence specifying ``return_total_data = True`` may carry out more computations than "
#            "``return_total_data = False``. For gradients and Hessians, ``return_total_data = False`` is rarely useful.",
#    )  # TODO switch to computes, not returns
#    nbodies_per_mc_level: List[List[Union[int, Literal["supersystem"]]]] = Field(
#        [],
#        description="Distribution of active n-body levels among model chemistry levels. All bodies in range "
#            "[1, self.max_nbody] must be present exactly once. Number of items in outer list is how many different "
#            "modelchems. Each inner list specifies what n-bodies to be run at the corresponding modelchem (e.g., "
#            "`[[1, 2]]` has max_nbody=2 and 1-body and 2-body contributions computed at the same level of theory; "
#            "`[[1], [2]]` has max_nbody=2 and 1-body and 2-body contributions computed at different levels of theory. "
#            "An entry 'supersystem' means all higher order n-body effects up to the number of fragments. The n-body "
#            "levels are effectively sorted in the outer list, and any 'supersystem' element is at the end.",
#        json_schema_extra={
#            "shape": ["nmc", "<varies>"],
#        },
#    )
#
#    @field_validator("nfragments")
#    @classmethod
#    def set_nfragments(cls, v: int, info: FieldValidationInfo) -> int:
#        return len(info.data["molecule"].fragments)
#
#    @field_validator("max_nbody")
#    @classmethod
#    def set_max_nbody(cls, v: int, info: FieldValidationInfo) -> int:
#        if v == -1:
#            return info.data["nfragments"]
#        else:
#            return min(v, info.data["nfragments"])
#
#    @field_validator("return_total_data")
#    @classmethod
#    def set_return_total_data(cls, v: Optional[bool], info: FieldValidationInfo) -> bool:
#        print(f"FFFF {info=}")
#        print(f"GGGG {info.data['specification']=}") #['driver']=}")
#        print(f"HHHH {info.data['specification'].driver=}")
#        print(f"{v=}")
#        driver = info.data['specification'].driver
#        user_rtd = info.data['specification'].keywords.return_total_data
#        print(f"{user_rtd=}")
#        #if v is not None:
#        #    rtd = v
#        if user_rtd is not None:
#            rtd = user_rtd
#        elif info.data["specification"].driver in ["gradient", "hessian"]:
#            rtd = True
#        else:
#            rtd = False
#
#        # todo put back
#        #if info.data.get("embedding_charges", False) and rtd is False:
#        #    raise ValueError("Cannot return interaction data when using embedding scheme.")
#
#        return rtd



class ManyBodyResult(ManyBodyInput):
#class ManyBodyResult(SuccessfulResultBase):

    schema_name: Literal["qcschema_manybodyresult"] = "qcschema_manybodyresult"
    schema_version: Literal[1] = Field(
        1,
        description="The version number of ``schema_name`` to which this model conforms.",
    )
    id: Optional[str] = Field(None, description="The optional ID for the object.")
    extras: Dict[str, Any] = Field(
        {},
        description="Additional information to bundle with the object. Use for schema development and scratch space.",
    )

    provenance: Provenance = Field(..., description=str(Provenance.__doc__))
    input_data: ManyBodyInput = Field(
        ...,
    )
    success: bool = Field(
        ...,
        description="A boolean indicator that the operation succeeded or failed. Allows programmatic assessment of "
        "all results regardless of if they failed or succeeded by checking `result.success`.",
    )

    stdout: Optional[str] = Field(
        None,
        description="The primary logging output of the program, whether natively standard output or a file. Presence vs. absence (or null-ness?) configurable by protocol.",
    )
    stderr: Optional[str] = Field(None, description="The standard error of the program execution.")
    success: Literal[True] = Field(True, description="Always `True` for a successful result")


class ManyBodyResultProperties(ProtoModel):
    r"""
    Named properties of quantum chemistry computations following the MolSSI QCSchema.

    All arrays are stored flat but must be reshapable into the dimensions in attribute ``shape``, with abbreviations as follows:

    * nao: number of atomic orbitals = :attr:`~qcelemental.models.AtomicResultProperties.calcinfo_nbasis`
    * nmo: number of molecular orbitals = :attr:`~qcelemental.models.AtomicResultProperties.calcinfo_nmo`
    """

    # Calcinfo
    calcinfo_nmc: Optional[int] = Field(None, description="The number of model chemistries applied to n-body levels of the computation.")
    calcinfo_nfr: Optional[int] = Field(None, description="The number of fragments in the molecule for the computation.")
    calcinfo_natom: Optional[int] = Field(None, description="The number of atoms in the computation.")  # alias nat

    # Canonical
    #    nuclear_repulsion_energy: Optional[float] = Field(None, description="The nuclear repulsion energy.")
    return_energy: Optional[float] = Field(
        None,
        description=f"The interaction energy of the requested method: IE or total (depending on return_total_data) with cp/nocp/vmfc treatment (dep. on first of bsse_type). Always available. Identical to :attr:`~qcelemental.models.ManyBodyResult.return_result` for :attr:`~qcelemental.models.AtomicInput.driver`\\ =\\ :attr:`~qcelemental.models.DriverEnum.energy` computations.",
        json_schema_extra={
            "units": "E_h",
        }
    # alias ret_energy
    )
    return_gradient: Optional[Array[float]] = Field(
        None,
        description=f"The interaction gradient of the requested method: IE or total (depending on return_total_data) with cp/nocp/vmfc treatment (dep. on first of bsse_type). Available when driver is g/h. Identical to :attr:`~qcelemental.models.ManyBodyResult.return_result` for :attr:`~qcelemental.models.AtomicInput.driver`\\ =\\ :attr:`~qcelemental.models.DriverEnum.gradient` computations.",
        json_schema_extra={
            "units": "E_h/a0",
            "shape": ["nat", 3],
        },
        # alias ret_gradient
    )
    return_hessian: Optional[Array[float]] = Field(
        None,
        description=f"The interaction Hessian of the requested method: IE or total (depending on return_total_data) with cp/nocp/vmfc treatment (dep. on first of bsse_type). Available when driver is h. Identical to :attr:`~qcelemental.models.ManyBodyResult.return_result` for :attr:`~qcelemental.models.AtomicInput.driver`\\ =\\ :attr:`~qcelemental.models.DriverEnum.hessian` computations.",
        json_schema_extra={
            "units": "E_h/a0^2",
            "shape": ["nat" * 3, "nat" * 3],
        },
        # alias ret_hessian
    )

    # Energies
    cp_corrected_total_energy_through_1body: Optional[float] = Field(
        None,
        description="MBE sum of subsystems of 1-body. Summed are total energies with cp treatment. Available when cp in bsse_type.",
        json_schema_extra={"units": "E_h"},
        # alias CP-CORRECTED TOTAL ENERGY THROUGH 1-BODY
    )


#######

#class TrajectoryProtocolEnum(str, Enum):
#class OptimizationProtocols(ProtoModel):
#class QCInputSpecification(ProtoModel):
#class OptimizationInput(ProtoModel):
#class OptimizationResult(OptimizationInput):
#class OptimizationSpecification(ProtoModel):
#
#class TDKeywords(ProtoModel):
#class TorsionDriveInput(ProtoModel):
#class TorsionDriveResult(TorsionDriveInput):
#
###### next  #####
#
#class TrajectoryProtocolEnum(str, Enum):
#class OptimizationProtocols(ProtoModel):
#class OptimizationSpecification(SpecificationBase):
#class OptimizationInput(InputBase):
#class OptimizationResult(SuccessfulResultBase):
#
#class TDKeywords(ProtoModel):
#class TorsionDriveSpecification(SpecificationBase):
#class TorsionDriveInput(InputBase):
#class TorsionDriveResult(SuccessfulResultBase):
#
#class FailedOperation(ResultBase):




#######opt master #####

# class OptimizationInput(ProtoModel):
#     id: Optional[str] = None
#     hash_index: Optional[str] = None
#     schema_name: constr(  # type: ignore
#         strip_whitespace=True, pattern=qcschema_optimization_input_default
#     ) = qcschema_optimization_input_default
#     schema_version: int = 1

#     keywords: Dict[str, Any] = Field({}, description="The optimization specific keywords to be used.")
#     extras: Dict[str, Any] = Field({}, description="Extra fields that are not part of the schema.")
#     protocols: OptimizationProtocols = Field(OptimizationProtocols(), description=str(OptimizationProtocols.__doc__))

#     input_specification: QCInputSpecification = Field(..., description=str(QCInputSpecification.__doc__))
#     initial_molecule: Molecule = Field(..., description="The starting molecule for the geometry optimization.")

#     provenance: Provenance = Field(Provenance(**provenance_stamp(__name__)), description=str(Provenance.__doc__))

#     def __repr_args__(self) -> "ReprArgs":
#         return [
#             ("model", self.input_specification.model.model_dump()),
#             ("molecule_hash", self.initial_molecule.get_hash()[:7]),
#         ]


# class OptimizationResult(OptimizationInput):
#     schema_name: constr(  # type: ignore
#         strip_whitespace=True, pattern=qcschema_optimization_output_default
#     ) = qcschema_optimization_output_default

#     final_molecule: Optional[Molecule] = Field(..., description="The final molecule of the geometry optimization.")
#     trajectory: List[AtomicResult] = Field(
#         ..., description="A list of ordered Result objects for each step in the optimization."
#     )
#     energies: List[float] = Field(..., description="A list of ordered energies for each step in the optimization.")

#     stdout: Optional[str] = Field(None, description="The standard output of the program.")
#     stderr: Optional[str] = Field(None, description="The standard error of the program.")

#     success: bool = Field(
#         ..., description="The success of a given programs execution. If False, other fields may be blank."
#     )
#     error: Optional[ComputeError] = Field(None, description=str(ComputeError.__doc__))
#     provenance: Provenance = Field(..., description=str(Provenance.__doc__))

#     @field_validator("trajectory")
#     @classmethod
#     def _trajectory_protocol(cls, v, info):
#         # Do not propogate validation errors
#         if "protocols" not in info.data:
#             raise ValueError("Protocols was not properly formed.")

#         keep_enum = info.data["protocols"].trajectory
#         if keep_enum == "all":
#             pass
#         elif keep_enum == "initial_and_final":
#             if len(v) != 2:
#                 v = [v[0], v[-1]]
#         elif keep_enum == "final":
#             if len(v) != 1:
#                 v = [v[-1]]
#         elif keep_enum == "none":
#             v = []
#         else:
#             raise ValueError(f"Protocol `trajectory:{keep_enum}` is not understood.")

#         return v

# ####### next######

# class OptimizationInput(InputBase):
#     """Input object for an optimization computation"""

#     schema_name: Literal["qcschema_optimizationinput"] = "qcschema_optimizationinput"
#     specification: OptimizationSpecification = Field(..., description=OptimizationSpecification.__doc__)

#     def __repr_args__(self) -> "ReprArgs":
#         return [
#             ("model", self.specification.gradient_specification.model.dict()),
#             ("molecule_hash", self.molecule.get_hash()[:7]),
#         ]


# class OptimizationResult(SuccessfulResultBase):
#     """The result of an optimization procedure"""

#     schema_name: Literal["qcschema_optimizationresult"] = "qcschema_optimizationresult"
#     input_data: OptimizationInput = Field(..., description=OptimizationInput.__doc__)
#     # NOTE: If Optional we want None instead of ...; is there a reason for ...? Should the attribute not be Optional?
#     final_molecule: Optional[Molecule] = Field(..., description="The final molecule of the geometry optimization.")
#     trajectory: List[AtomicResult] = Field(
#         ..., description="A list of ordered Result objects for each step in the optimization."
#     )
#     energies: List[float] = Field(..., description="A list of ordered energies for each step in the optimization.")

#     @validator("trajectory", each_item=False)
#     def _trajectory_protocol(cls, v, values):
#         # NOTE: Commenting out because with current setup field is guaranteed to always exist
#         # Do not propagate validation errors
#         # if "protocols" not in values["input_data"]:
#         #     raise ValueError("Protocols was not properly formed.")
#         if not values.get("input_data"):
#             raise ValueError("input_data not correctly formatted!")

#         keep_enum = values["input_data"].specification.protocols.trajectory
#         if keep_enum == "all":
#             pass
#         elif keep_enum == "initial_and_final":
#             if len(v) != 2:
#                 v = [v[0], v[-1]]
#         elif keep_enum == "final":
#             if len(v) != 1:
#                 v = [v[-1]]
#         elif keep_enum == "none":
#             v = []
#         else:
#             raise ValueError(f"Protocol `trajectory:{keep_enum}` is not understood.")
#
#        return v

###################

# class AutoSetProvenance(QCSchemaModelBase):
#     """Base class for QCSchema objects that auto-set their provenance value"""

#     provenance: Provenance = Field(Provenance(**provenance_stamp(__name__)), description=Provenance.__doc__)

# QCSchemaModelBase
#     schema_name: str = Field(..., description="The QCSchema name of the class")
#     schema_version: Literal[2] = Field(
#         2, description="The version number of ``schema_name`` to which this model conforms."
#     )
#     id: Optional[str] = Field(None, description="The optional ID for the object.")
#     extras: Dict[str, Any] = Field(
#         {},
#         description="Additional information to bundle with the object. Use for schema development and scratch space.",
#     )

#     provenance: Provenance = Field(..., description=str(Provenance.__doc__))

# class SpecificationBase(AutoSetProvenance):
#     """Specification objects contain the keywords and other configurable parameters directed at a particular QC program"""

#     keywords: Dict[str, Any] = Field({}, description="The program specific keywords to be used.")
#     program: str = Field(..., description="The program for which the Specification is intended.")


# class InputBase(AutoSetProvenance):
#     """An Input is composed of a .specification and a .molecule which together fully specify a computation"""

#     specification: SpecificationBase = Field(..., description=SpecificationBase.__doc__)
#     molecule: Molecule = Field(..., description=Molecule.__doc__)


# class ResultBase(QCSchemaModelBase):
#     """Base class for all result classes"""

#     input_data: InputBase = Field(..., description=InputBase.__doc__)
#     success: bool = Field(
#         ...,
#         description="A boolean indicator that the operation succeeded or failed. Allows programmatic assessment of "
#         "all results regardless of if they failed or succeeded by checking `result.success`.",
#     )

#     stdout: Optional[str] = Field(
#         None,
#         description="The primary logging output of the program, whether natively standard output or a file. Presence vs. absence (or null-ness?) configurable by protocol.",
#     )
#     stderr: Optional[str] = Field(None, description="The standard error of the program execution.")


# class SuccessfulResultBase(ResultBase):
#     """Base object for any successful result"""

#     success: Literal[True] = Field(True, description="Always `True` for a successful result")

