from typing import Any, Optional, Dict, List, Literal
from collections import defaultdict
from copy import deepcopy
import warnings
import openseespy.opensees as ops

from ._BaseHandler import BaseHandler, SubBaseHandler


class SectionHandler(SubBaseHandler):
    def __init__(self, registry: dict[str, dict], sections_store: dict[int, dict]):
        """
        registry: secType → handler global mapping (for manager generation)
        sections_store: Shared reference to SectionManager.sections
        """
        self.sections = sections_store
        self._current_section:int = None
        self._register(registry)

    @property
    def _COMMAND_RULES(self) -> dict[str, dict[str, Any]]:
        ndm = ops.getNDM()[0]
        return {
            "section": {
                "alternative": True,
                "Elastic": {
                    "positional": ["secType", "secTag", "E_mod", "A", "Iz", "G_mod?", "alphaY?"] if ndm == 2 else ["secType", "secTag", "E_mod", "A", "Iz", "Iy", "G_mod", "Jxx", "alphaY?", "alphaZ?"]
                },
                "Fiber": {
                    "positional": ["secType", "secTag"],
                    "options": {
                        "-GJ?": "GJ",
                        "-torsion?": "torsion_mat_tag"
                    }
                },
                "FiberThermal": {
                    "positional": ["secType", "secTag"],
                    "options": {
                        "-GJ?": "GJ"
                    }
                },
                "NDFiber": {
                    "positional": ["secType", "secTag"]
                },
                "WFSection2d": {
                    "positional": ["secType", "secTag", "matTag", "d", "tw", "bf", "tf", "Nfw", "Nff"]
                },
                "RCSection2d": {
                    "positional": ["secType", "secTag", "coreMatTag", "coverMatTag", "steelMatTag", "d", "b", "cover_depth", "Atop", "Abot", "Aside", "Nfcore", "Nfcover", "Nfs"]
                },
                "RCCircularSection": {
                    "positional": ["secType", "secTag", "coreMatTag", "coverMatTag", "steelMatTag", "d", "cover_depth", "Ab", "NringsCore", "NringsCover", "Nwedges", "Nsteel"],
                    "options": {
                        "-GJ?": "GJ",
                        "-torsion?": "torsion_mat_tag"
                    }
                },
                "Parallel":{
                    "positional": ["secType", "secTag", "SecTags*"]
                },
                "Aggregator": {
                    "positional": ["secType", "secTag", "mats*"],
                    "options": {
                        "-section?": "sectionTag"
                    }
                },
                "Uniaxial": {
                    "positional": ["secType", "secTag", "matTag", "quantity"]
                },
                "ElasticMembranePlateSection": {
                    "positional": ["secType", "secTag", "E_mod", "nu", "h", "rho", "Ep_modifier?"]
                },
                "PlateFiber": {
                    "positional": ["secType", "secTag", "matTag", "h"]
                },
                "Bidirectional": {
                    "positional": ["secType", "secTag", "E_mod", "Fy", "Hiso", "Hkin", "code1?", "code2?"]
                },
                "Isolator2spring": {
                    "positional": ["secType", "secTag", "tol", "k1", "Fyo", "k2o", "kvo", "hb", "PE", "Po?"]
                },
                "LayeredShell": {
                    "positional": ["secType", "secTag", "nLayers", "mats*"]
                },
                "Pipe": {
                    "positional": ["secType", "secTag", "do", "t"],
                    "options": {
                        "-alphaV?": "alphaV",
                        "-defaultAlphaV?": "defaultAlphaV", 
                        "-rho?": "rho"
                    }
                }
            }
        }

    # ---------- secType to handle ----------
    @staticmethod
    def handles() -> list[str]:
        return ["section"]

    @staticmethod
    def types() -> list[str]:
        return ["Elastic", "Fiber", "FiberThermal", "NDFiber", "WFSection2d", "RCSection2d",
                "RCCircularSection", "Parallel", "Aggregator", "Uniaxial", "ElasticMembranePlateSection",
                "PlateFiber", "Bidirectional", "Isolator2spring", "LayeredShell", "Pipe"]

    def handle(self, func_name: str, arg_map: dict[str, Any]):
        args, kwargs = arg_map["args"], arg_map["kwargs"]
        secType = args[0]
        dispatch = {
            "Elastic": self._handle_Elastic,
            "Fiber": self._handle_Fiber,
            "FiberThermal": self._handle_FiberThermal,
            "NDFiber": self._handle_NDFiber,
            "WFSection2d": self._handle_WFSection2d,
            "RCSection2d": self._handle_RCSection2d,
            "RCCircularSection": self._handle_RCCircularSection,
            "Parallel": self._handle_Parallel,
            "Aggregator": self._handle_Aggregator,
            "Uniaxial": self._handle_Uniaxial,
            "ElasticMembranePlateSection": self._handle_ElasticMembranePlateSection,
            "PlateFiber": self._handle_PlateFiber,
            "Bidirectional": self._handle_Bidirectional,
            "Isolator2spring": self._handle_Isolator2spring,
            "LayeredShell": self._handle_LayeredShell,
            "Pipe": self._handle_Pipe
        }.get(secType, self._unknown)
        dispatch(*args, **kwargs)

    def _handle_Elastic(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle Elastic Section

        section('Elastic', secTag, E_mod, A, Iz, G_mod=None, alphaY=None)   # 2D

        section('Elastic', secTag, E_mod, A, Iz, Iy, G_mod, Jxx, alphaY=None, alphaZ=None)   # 3D
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)
        ndm = ops.getNDM()
        secTag = arg_map.get("secTag")
        if ndm == 2:
            section_info = {
                "secType": arg_map.get("secType"),
                "secTag": secTag,
                "E_mod": arg_map.get("E_mod"),
                "A": arg_map.get("A"),
                "Iz": arg_map.get("Iz"),
                "G_mod": arg_map.get("G_mod",None),
                "alphaY": arg_map.get("alphaY",None),
            }
        else:
            section_info = {
                "secType": arg_map.get("secType"),
                "secTag": secTag,
                "E_mod": arg_map.get("E_mod"),
                "A": arg_map.get("A"),
                "Iz": arg_map.get("Iz"),
                "Iy": arg_map.get("Iy"),
                "G_mod": arg_map.get("G_mod"),
                "Jxx": arg_map.get("Jxx"),
                "alphaY": arg_map.get("alphaY",None),
                "alphaZ": arg_map.get("alphaZ",None),
            }

        self.sections[secTag] = section_info
        self._current_section = None
        return section_info

    def _handle_Fiber(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle Fiber Section

        section('Fiber', secTag, '-GJ', GJ)
        section('Fiber', secTag, '-torsion', torsionMatTag)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "fibers": [],
            "patches": [],
            "layers": []
        }
        
        if arg_map.get("GJ") is not None:
            section_info["GJ"] = arg_map.get("GJ")
        if arg_map.get("torsion_mat_tag") is not None:
            section_info["torsion_mat_tag"] = arg_map.get("torsion_mat_tag")

        self.sections[secTag] = section_info
        self._current_section = secTag
        return section_info

    def _handle_FiberThermal(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle FiberThermal Section

        section('FiberThermal', secTag, '-GJ', GJ=0.0)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "GJ": arg_map.get("GJ", 0.0),
            "fibers": [],
            "patches": [],
            "layers": []
        }

        self.sections[secTag] = section_info
        self._current_section = secTag
        return section_info

    def _handle_NDFiber(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle NDFiber Section

        section('NDFiber', secTag)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "fibers": [],
            "patches": [],
            "layers": []
        }

        self.sections[secTag] = section_info
        self._current_section = secTag
        return section_info

    def _handle_WFSection2d(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle Wide Flange Section

        section('WFSection2d', secTag, matTag, d, tw, bf, tf, Nfw, Nff)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "matTag": arg_map.get("matTag"),
            "d": arg_map.get("d"),
            "tw": arg_map.get("tw"),
            "bf": arg_map.get("bf"),
            "tf": arg_map.get("tf"),
            "Nfw": arg_map.get("Nfw"),
            "Nff": arg_map.get("Nff"),
        }

        self.sections[secTag] = section_info
        self._current_section = None
        return section_info

    def _handle_RCSection2d(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle RC Section

        section('RCSection2d', secTag, coreMatTag, coverMatTag, steelMatTag, d, b, cover_depth, Atop, Abot, Aside, Nfcore, Nfcover, Nfs)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "coreMatTag": arg_map.get("coreMatTag"),
            "coverMatTag": arg_map.get("coverMatTag"),
            "steelMatTag": arg_map.get("steelMatTag"),
            "d": arg_map.get("d"),
            "b": arg_map.get("b"),
            "cover_depth": arg_map.get("cover_depth"),
            "Atop": arg_map.get("Atop"),
            "Abot": arg_map.get("Abot"),
            "Aside": arg_map.get("Aside"),
            "Nfcore": arg_map.get("Nfcore"),
            "Nfcover": arg_map.get("Nfcover"),
            "Nfs": arg_map.get("Nfs"),
        }

        self.sections[secTag] = section_info
        self._current_section = None
        return section_info

    def _handle_RCCircularSection(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle RCCircular Section

        section('RCCircularSection', secTag, coreMatTag, coverMatTag, steelMatTag, d, cover_depth, Ab, NringsCore, NringsCover, Nwedges, Nsteel, '-GJ', GJ <or '-torsion', matTag>)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "coreMatTag": arg_map.get("coreMatTag"),
            "coverMatTag": arg_map.get("coverMatTag"),
            "steelMatTag": arg_map.get("steelMatTag"),
            "d": arg_map.get("d"),
            "cover_depth": arg_map.get("cover_depth"),
            "Ab": arg_map.get("Ab"),
            "NringsCore": arg_map.get("NringsCore"),
            "NringsCover": arg_map.get("NringsCover"),
            "Nwedges": arg_map.get("Nwedges"),
            "Nsteel": arg_map.get("Nsteel"),
        }
        
        if arg_map.get("GJ") is not None:
            section_info["GJ"] = arg_map.get("GJ")
        if arg_map.get("torsion_mat_tag") is not None:
            section_info["torsion_mat_tag"] = arg_map.get("torsion_mat_tag")

        self.sections[secTag] = section_info
        self._current_section = None
        return section_info

    def _handle_Parallel(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle Parallel Section

        section('Parallel', secTag, SecTags*)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "SecTags": arg_map.get("SecTags", []),
        }

        self.sections[secTag] = section_info
        self._current_section = None
        return section_info

    def _handle_Aggregator(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle Section Aggregator

        section('Aggregator', secTag, *mats, '-section', sectionTag)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "mats": arg_map.get("mats", []),
        }
        
        if arg_map.get("sectionTag") is not None:
            section_info["sectionTag"] = arg_map.get("sectionTag")

        self.sections[secTag] = section_info
        self._current_section = None
        return section_info

    def _handle_Uniaxial(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle Uniaxial Section

        section('Uniaxial', secTag, matTag, quantity)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "matTag": arg_map.get("matTag"),
            "quantity": arg_map.get("quantity"),
        }

        self.sections[secTag] = section_info
        self._current_section = None
        return section_info

    def _handle_ElasticMembranePlateSection(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle Elastic Membrane Plate Section

        section('ElasticMembranePlateSection', secTag, E_mod, nu, h, rho, <Ep_modifier>)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "E_mod": arg_map.get("E_mod"),
            "nu": arg_map.get("nu"),
            "h": arg_map.get("h"),
            "rho": arg_map.get("rho"),
        }
        
        if arg_map.get("Ep_modifier") is not None:
            section_info["Ep_modifier"] = arg_map.get("Ep_modifier")

        self.sections[secTag] = section_info
        self._current_section = None
        return section_info

    def _handle_PlateFiber(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle Plate Fiber Section

        section('PlateFiber', secTag, matTag, h)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "matTag": arg_map.get("matTag"),
            "h": arg_map.get("h"),
            "fibers": [],
            "patches": [],
            "layers": []
        }

        self.sections[secTag] = section_info
        self._current_section = secTag
        return section_info

    def _handle_Bidirectional(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle Bidirectional Section

        section('Bidirectional', secTag, E_mod, Fy, Hiso, Hkin, code1='Vy', code2='P')
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "E_mod": arg_map.get("E_mod"),
            "Fy": arg_map.get("Fy"),
            "Hiso": arg_map.get("Hiso"),
            "Hkin": arg_map.get("Hkin"),
            "code1": arg_map.get("code1", "Vy"),
            "code2": arg_map.get("code2", "P"),
        }

        self.sections[secTag] = section_info
        self._current_section = None
        return section_info

    def _handle_Isolator2spring(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle Isolator2spring Section

        section('Isolator2spring', matTag, tol, k1, Fyo, k2o, kvo, hb, PE, Po=0.0)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "tol": arg_map.get("tol"),
            "k1": arg_map.get("k1"),
            "Fyo": arg_map.get("Fyo"),
            "k2o": arg_map.get("k2o"),
            "kvo": arg_map.get("kvo"),
            "hb": arg_map.get("hb"),
            "PE": arg_map.get("PE"),
            "Po": arg_map.get("Po", 0.0),
        }

        self.sections[secTag] = section_info
        self._current_section = None
        return section_info

    def _handle_LayeredShell(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle LayeredShell Section

        section('LayeredShell', sectionTag, nLayers, *mats)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "nLayers": arg_map.get("nLayers"),
            "mats": arg_map.get("mats", []),
        }

        self.sections[secTag] = section_info
        self._current_section = None
        return section_info

    def _handle_Pipe(self, *args, **kwargs) -> dict[str, Any]:
        """
        Handle Pipe Section

        section('Pipe', secTag, do, t, <'-alphaV', alphaV>, <'-defaultAlphaV'>, <'-rho', rho>)
        """
        arg_map = self._parse(self.handles()[0], *args, **kwargs)

        secTag = arg_map.get("secTag")
        section_info = {
            "secType": arg_map.get("secType"),
            "secTag": secTag,
            "do": arg_map.get("do"),
            "t": arg_map.get("t"),
        }
        
        if arg_map.get("alphaV") is not None:
            section_info["alphaV"] = arg_map.get("alphaV")
        if arg_map.get("defaultAlphaV") is not None:
            section_info["defaultAlphaV"] = arg_map.get("defaultAlphaV")
        if arg_map.get("rho") is not None:
            section_info["rho"] = arg_map.get("rho")

        self.sections[secTag] = section_info
        self._current_section = None
        return section_info

    def _unknown(self, *args, **kwargs):
        # should never use this function but use SectionManager.handle_unknown_section()
        raise NotImplementedError(f"Unknown section type: {args[0]}")

    def clear(self):
        self.sections.clear()

class SectionManager(BaseHandler):
    """Manager for section commands in OpenSeesPy
    
    Handles section command which creates SectionForceDeformation objects
    representing force-deformation relationships at beam-column and plate sample points.
    """
    
    def __init__(self):
        # 统一数据仓库
        self.sections: dict[int, dict] = {}
        self.current_section: int = None
        # 构建 “命令 -> {matType -> handler}” 映射
        self._command2typehandler: dict[str, dict[str, BaseHandler]] = defaultdict(dict)
        handler_classes = [SectionHandler]
        for cls in handler_classes:
            cmd = cls.handles()[0]
            for typ in cls.types():
                self._command2typehandler[cmd][typ] = cls(self._command2typehandler[cmd], self.sections)
        
    @property
    def _COMMAND_RULES(self) -> dict[str, dict[str, Any]]:
        """Define parsing rules for section commands"""
        """聚合各子 Handler 的 rule"""
        merged: defaultdict[str, dict[str, Any]] = defaultdict(lambda: defaultdict(lambda: deepcopy({"positional": ["secType", "secTag", "args*"]})))
        for t2h in self._command2typehandler.values():
            for h in set(t2h.values()):
                for k, v in h._COMMAND_RULES.items():
                    merged[k].update(v)
        merged["fiber"] = {
            "positional": ["yloc", "zloc", "A", "matTag"]
        }
        merged["patch"] = {
            "alternative": True,
            "quad": {
                "positional": ["type", "matTag", "numSubdivIJ", "numSubdivJK", "crdsI*2", "crdsJ*2", "crdsK*2", "crdsL*2"]
            },
            "rect": {
                "positional": ["type", "matTag", "numSubdivY", "numSubdivZ", "crdsI*2", "crdsJ*2"]
            },
            "circ": {
                "positional": ["type", "matTag", "numSubdivCirc", "numSubdivRad", "center*2", "rad*2", "ang*2"]
            }
        }
        merged["layer"] = {
            "alternative": True,
            "straight": {
                "positional": ["type", "matTag", "numFiber", "areaFiber", "start*2", "end*2"]
            },
            "circ": {
                "positional": ["type", "matTag", "numFiber", "areaFiber", "center*2", "radius", "ang*2?"]
            },
            "rect": {
                "positional": ["type", "matTag", "numFiberY", "numFiberZ", "areaFiber", "center*2", "distY", "distZ"]
            }
        }
        return merged
    
    def handles(self) -> List[str]:
        """Return list of commands this manager handles"""
        return ["section", "fiber", "patch", "layer"]
    
    def handle(self, func_name: str, arg_map: dict[str, Any]):
        """Handle section commands"""
        if func_name == "fiber":
            args, kwargs = arg_map.get("args"), arg_map.get("kwargs")
            parsed_args = self._parse("fiber", *args, **kwargs)
            self._handle_fiber(parsed_args)
        elif func_name == "patch":
            args, kwargs = arg_map.get("args"), arg_map.get("kwargs")
            parsed_args = self._parse("patch", *args, **kwargs)
            self._handle_patch(parsed_args)
        elif func_name == "layer":
            args, kwargs = arg_map.get("args"), arg_map.get("kwargs")
            parsed_args = self._parse("layer", *args, **kwargs)
            self._handle_layer(parsed_args)
        elif func_name == "section":
            secType = arg_map["args"][0]
            registry = self._command2typehandler.get(func_name, {})
            handler = registry.get(secType)
            if handler:
                handler.handle(func_name, arg_map)
                self.current_section = handler._current_section
            else:
                self.handle_unknown_section(func_name, *arg_map["args"], **arg_map["kwargs"])
        else:
            raise ValueError(f"Unknown function: {func_name}")

    def handle_unknown_section(self, func_name: str, *args, **kwargs):
        """Handle unknown section types"""
        arg_map = self._parse(func_name, *args, **kwargs)

        secTag = int(arg_map.get("secTag"))
        secType = arg_map.get("secType")
        args = arg_map.get("args", [])
        secinfo = {
            "secType": secType,
            "secTag": secTag,
            "args": args,
            "sectionType": func_name  # section
        }
        self.sections[secTag] = secinfo


    def _handle_fiber(self, arg_map: dict[str, Any]):
        """Handle fiber command
        
        Args:
            arg_map: Parsed arguments from _parse method
        """
        if self.current_section is None:
            raise ValueError("No current section defined, Please define a fiber section first")
            
        fiber_info = {
            "yloc": arg_map.get("yloc"),
            "zloc": arg_map.get("zloc"), 
            "A": arg_map.get("A"),
            "matTag": arg_map.get("matTag")
        }
        
        # Add fiber to current section
        if self.current_section:
            self.sections[self.current_section]["fibers"].append(fiber_info)
        else:
            raise ValueError("No current section defined, Please define a fiber section first")

    def _handle_patch(self, arg_map: dict[str, Any]):
        """Handle patch command
        
        Args:
            arg_map: Parsed arguments from _parse method
        """
        if self.current_section is None:
            raise ValueError("No current section defined, Please define a fiber section first")
            
        patch_type = arg_map.get("type")
        patch_info = {"type": patch_type}
        
        if patch_type == "quad":
            patch_info.update({
                "matTag": arg_map.get("matTag"),
                "numSubdivIJ": arg_map.get("numSubdivIJ"),
                "numSubdivJK": arg_map.get("numSubdivJK"),
                "crdsI": arg_map.get("crdsI", []),
                "crdsJ": arg_map.get("crdsJ", []),
                "crdsK": arg_map.get("crdsK", []),
                "crdsL": arg_map.get("crdsL", [])
            })
        elif patch_type == "rect":
            patch_info.update({
                "matTag": arg_map.get("matTag"),
                "numSubdivY": arg_map.get("numSubdivY"),
                "numSubdivZ": arg_map.get("numSubdivZ"),
                "crdsI": arg_map.get("crdsI", []),
                "crdsJ": arg_map.get("crdsJ", [])
            })
        elif patch_type == "circ":
            patch_info.update({
                "matTag": arg_map.get("matTag"),
                "numSubdivCirc": arg_map.get("numSubdivCirc"),
                "numSubdivRad": arg_map.get("numSubdivRad"),
                "center": arg_map.get("center", []),
                "rad": arg_map.get("rad", []),
                "ang": arg_map.get("ang", [])
            })
        
        # Add patch to current section
        if self.current_section in self.sections:
            self.sections[self.current_section]["patches"].append(patch_info)
        else:
            raise ValueError("No current section defined, Please define a fiber section first")

    def _handle_layer(self, arg_map: dict[str, Any]):
        """Handle layer command
        
        Args:
            arg_map: Parsed arguments from _parse method
        """
        if self.current_section is None:
            raise ValueError("No current section defined, Please define a fiber section first")
            
        layer_type = arg_map.get("type")
        layer_info = {"type": layer_type}
        
        if layer_type == "straight":
            layer_info.update({
                "matTag": arg_map.get("matTag"),
                "numFiber": arg_map.get("numFiber"),
                "areaFiber": arg_map.get("areaFiber"),
                "start": arg_map.get("start", []),
                "end": arg_map.get("end", [])
            })
        elif layer_type == "circ":
            layer_info.update({
                "matTag": arg_map.get("matTag"),
                "numFiber": arg_map.get("numFiber"),
                "areaFiber": arg_map.get("areaFiber"),
                "center": arg_map.get("center", []),
                "radius": arg_map.get("radius"),
                "ang": arg_map.get("ang", [0.0, 360.0 - 360.0/arg_map.get("numFiber", 1)])
            })
        elif layer_type == "rect":
            layer_info.update({
                "matTag": arg_map.get("matTag"),
                "numFiberY": arg_map.get("numFiberY"),
                "numFiberZ": arg_map.get("numFiberZ"),
                "areaFiber": arg_map.get("areaFiber"),
                "center": arg_map.get("center", []),
                "distY": arg_map.get("distY"),
                "distZ": arg_map.get("distZ")
            })
        
        # Add layer to current section
        if self.current_section:
            self.sections[self.current_section]["layers"].append(layer_info)
        else:
            raise ValueError("No current section defined, Please define a fiber section first")

    def get_section(self, tag: int) -> Optional[Dict[str, Any]]:
        """Get section information by tag
        
        Args:
            tag: Section tag
            
        Returns:
            Section information dictionary or None if not found
        """
        return self.sections.get(tag)
    
    def get_current_section(self) -> Optional[Dict[str, Any]]:
        """Get current section information
        
        Returns:
            Current section information dictionary or None if not found
        """
        return self.sections.get(self.current_section)
    
    def get_sections_by_type(
            self,
            sec_type: Literal["Elastic", "Fiber", "FiberThermal", "NDFiber", "WFSection2d", "RCSection2d",
                "RCCircularSection", "Parallel", "Aggregator", "Uniaxial", "ElasticMembranePlateSection",
                "PlateFiber", "Bidirectional", "Isolator2spring", "LayeredShell", "Pipe"]
            ) -> List[Dict[str, Any]]:
        """Get all sections of a specific type
        
        Args:
            sec_type: Section type (e.g., 'Elastic', 'Fiber', etc.)
            
        Returns:
            List of section information dictionaries
        """
        result = []
        for section_info in self.sections.values():
            if section_info.get("secType") == sec_type:
                result.append(section_info)
        return result
    
    def get_section_tags(self) -> List[int]:
        """Get all section tags
        
        Returns:
            List of section tags
        """
        return list(self.sections.keys())
    
    def get_fibers(self, tag: int) -> List[Dict[str, Any]]:
        """Get all fibers for a specific section
        
        Args:
            tag: Section tag
            
        Returns:
            List of fiber information dictionaries
        """
        section = self.sections.get(tag)
        if section:
            return section.get("fibers", [])
        else:
            warnings.warn(f"Section with tag {tag} not found")
        return None
    
    def get_patches(self, tag: int) -> List[Dict[str, Any]]:
        """Get all patches for a specific section
        
        Args:
            tag: Section tag
            
        Returns:
            List of patch information dictionaries
        """
        section = self.sections.get(tag)
        if section:
            return section.get("patches", [])
        else:
            warnings.warn(f"Section with tag {tag} not found")
        return None
    
    def get_layers(self, tag: int) -> List[Dict[str, Any]]:
        """Get all layers for a specific section
        
        Args:
            tag: Section tag
            
        Returns:
            List of layer information dictionaries
        """
        section = self.sections.get(tag)
        if section:
            return section.get("layers", [])
        else:
            warnings.warn(f"Section with tag {tag} not found")
        return None
    
    def clear(self):
        """Clear all section data"""
        self.sections.clear()
        self.current_section = None

