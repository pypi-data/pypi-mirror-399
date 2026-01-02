"""
Thai DRG Grouper - Core Grouper Class
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

from .types import MDC_NAMES, GrouperResult

try:
    from dbfread import DBF
except ImportError:
    raise ImportError("Please install dbfread: pip install dbfread")


class ThaiDRGGrouper:
    """
    Thai DRG Grouper for a single version

    Args:
        dbf_path: Path to folder containing .dbf files
        version: Version string (e.g., '6.3')

    Example:
        grouper = ThaiDRGGrouper('./data/6.3', '6.3')
        result = grouper.group(pdx='S82201D', los=5)
    """

    def __init__(self, dbf_path: str, version: str = "unknown"):
        self.dbf_path = dbf_path
        self.version = version

        self._icd10_data: Dict[str, dict] = {}
        self._proc_data: Dict[str, dict] = {}
        self._drg_data: Dict[str, List[dict]] = {}
        self._cc_exclusions: Dict[str, Set[str]] = {}

        self._load_data()

    def _find_dbf_files(self) -> Dict[str, Optional[str]]:
        """Find .dbf files"""
        dbf_files = {"i10": None, "proc": None, "drg": None, "ccex": None}

        for f in os.listdir(self.dbf_path):
            fl = f.lower()
            if fl.endswith(".dbf"):
                if "i10" in fl:
                    dbf_files["i10"] = f
                elif "proc" in fl:
                    dbf_files["proc"] = f
                elif "drg" in fl and "ccex" not in fl:
                    dbf_files["drg"] = f
                elif "ccex" in fl or ("cc" in fl and "drg" not in fl):
                    dbf_files["ccex"] = f

        return dbf_files

    def _load_data(self):
        """Load .dbf files"""
        dbf_files = self._find_dbf_files()

        # Load ICD-10
        if dbf_files["i10"]:
            for rec in DBF(os.path.join(self.dbf_path, dbf_files["i10"]), encoding="cp874"):
                code = rec["CODE"].strip().upper()
                self._icd10_data[code] = {
                    "mdc": rec["MDC"].strip(),
                    "pdc": rec["PDC"].strip(),
                    "cc": bool(rec.get("CC")),
                    "maincc": (rec.get("MAINCC") or "").strip(),
                    "dclmain": (rec.get("DCLMAIN") or "").strip(),
                    "trauma": str(rec.get("TRAUMA", "")).strip() == "T",
                    "ccrow": rec.get("CCROW") or 0,
                }
                if len(code) > 4:
                    for length in [5, 4, 3]:
                        base = code[:length]
                        if base not in self._icd10_data:
                            self._icd10_data[base] = self._icd10_data[code]

        # Load Procedures
        if dbf_files["proc"]:
            for rec in DBF(os.path.join(self.dbf_path, dbf_files["proc"]), encoding="cp874"):
                code = str(rec["CODE"]).strip()
                self._proc_data[code] = {
                    "orp": str(rec.get("ORP", "")).strip().upper() == "Y",
                    "desc": str(rec.get("DESC", "")).strip(),
                }
                if len(code) == 4 and code.isdigit():
                    self._proc_data[f"{code[:2]}.{code[2:]}"] = self._proc_data[code]

        # Load DRG
        if dbf_files["drg"]:
            for rec in DBF(os.path.join(self.dbf_path, dbf_files["drg"]), encoding="cp874"):
                dc = rec["DC"].strip()
                if dc not in self._drg_data:
                    self._drg_data[dc] = []
                self._drg_data[dc].append(
                    {
                        "mdc": rec["MDC"].strip(),
                        "drg": rec["DRG"].strip(),
                        "rw": float(rec.get("RW") or 0),
                        "rw0d": float(rec.get("RW0D") or 0),
                        "wtlos": float(rec.get("WTLOS") or 0),
                        "ot": int(rec.get("OT") or 0),
                        "name": str(rec.get("DRGNAME") or "").strip(),
                    }
                )

        # Load CC Exclusions
        if dbf_files["ccex"]:
            for rec in DBF(os.path.join(self.dbf_path, dbf_files["ccex"]), encoding="cp874"):
                cc = rec["CC10"].strip().upper()
                notfor = rec["NOTFOR10"].strip().upper()
                if cc not in self._cc_exclusions:
                    self._cc_exclusions[cc] = set()
                self._cc_exclusions[cc].add(notfor)

    def _normalize_icd(self, code: str) -> str:
        return code.replace(".", "").replace(" ", "").upper().strip()

    def _normalize_proc(self, code: str) -> str:
        return code.replace(".", "").replace(" ", "").strip()

    def _get_icd10_info(self, code: str) -> Optional[dict]:
        normalized = self._normalize_icd(code)
        if normalized in self._icd10_data:
            return self._icd10_data[normalized]
        for length in [6, 5, 4, 3]:
            if len(normalized) >= length:
                short = normalized[:length]
                if short in self._icd10_data:
                    return self._icd10_data[short]
        return None

    def _get_proc_info(self, code: str) -> Optional[dict]:
        normalized = self._normalize_proc(code)
        if normalized in self._proc_data:
            return self._proc_data[normalized]
        if len(normalized) < 4:
            padded = normalized.zfill(4)
            if padded in self._proc_data:
                return self._proc_data[padded]
        return None

    def _is_valid_cc(self, cc_code: str, pdx_code: str) -> bool:
        cc_info = self._get_icd10_info(cc_code)
        if not cc_info or not cc_info["cc"]:
            return False
        maincc = cc_info["maincc"] or self._normalize_icd(cc_code)
        pdx_norm = self._normalize_icd(pdx_code)
        if maincc in self._cc_exclusions:
            for excl in self._cc_exclusions[maincc]:
                if pdx_norm.startswith(excl) or excl.startswith(pdx_norm[:3]):
                    return False
        return True

    def _calculate_pcl(self, pdx: str, sdx_list: List[str]) -> Tuple[int, List[str], List[str]]:
        valid_ccs, valid_mccs = [], []
        for sdx in sdx_list:
            if self._is_valid_cc(sdx, pdx):
                info = self._get_icd10_info(sdx)
                if info:
                    if (info.get("ccrow", 0) or 0) >= 3:
                        valid_mccs.append(sdx)
                    else:
                        valid_ccs.append(sdx)
        if valid_mccs:
            pcl = min(4, 2 + len(valid_mccs))
        elif valid_ccs:
            pcl = min(2, len(valid_ccs))
        else:
            pcl = 0
        return pcl, valid_ccs, valid_mccs

    def _find_dc(self, pdx: str, has_or: bool) -> str:
        pdx_info = self._get_icd10_info(pdx)
        if not pdx_info:
            return "2650"
        mdc = pdx_info["mdc"]
        pdc = pdx_info["pdc"]
        if pdc:
            pdc_letter = pdc[-1] if pdc[-1].isalpha() else "A"
            pdc_num = ord(pdc_letter.upper()) - ord("A")
            dc_num = min(49, 1 + pdc_num) if has_or else min(99, 50 + pdc_num)
            dc = f"{mdc.zfill(2)}{dc_num:02d}"
            if dc in self._drg_data:
                return dc
            for try_dc in range(dc_num - 5, dc_num + 5):
                if 0 <= try_dc <= 99:
                    alt_dc = f"{mdc.zfill(2)}{try_dc:02d}"
                    if alt_dc in self._drg_data:
                        return alt_dc
        for dc in self._drg_data:
            if dc.startswith(mdc.zfill(2)):
                dc_suffix = int(dc[2:]) if dc[2:].isdigit() else 50
                if has_or and dc_suffix < 50:
                    return dc
                elif not has_or and dc_suffix >= 50:
                    return dc
        return f"{mdc.zfill(2)}50"

    def _find_drg(self, dc: str, pcl: int) -> dict:
        if dc not in self._drg_data:
            return {
                "drg": "26509",
                "name": "Ungroupable",
                "rw": 0,
                "rw0d": 0,
                "wtlos": 0,
                "ot": 0,
                "mdc": "26",
            }
        drgs = sorted(self._drg_data[dc], key=lambda x: x["drg"])
        return drgs[min(pcl, len(drgs) - 1)]

    def _calculate_adjrw(
        self, rw: float, rw0d: float, wtlos: float, ot: int, los: int
    ) -> Tuple[float, str]:
        if los <= 0:
            return rw0d, "daycase"
        if los <= ot or ot == 0:
            return rw, "normal"
        if wtlos > 0:
            adjrw = rw + (los - ot) * (rw / wtlos) * 0.5
            return round(adjrw, 4), "long_stay"
        return rw, "normal"

    def group(
        self,
        pdx: str,
        sdx: List[str] = None,
        procedures: List[str] = None,
        age: Optional[int] = None,
        sex: Optional[str] = None,
        los: int = 1,
        discharge_status: str = "normal",
    ) -> GrouperResult:
        """Group a patient case into DRG"""
        sdx = sdx or []
        procedures = procedures or []
        errors, warnings = [], []

        # Validate Age (Error Code 6) - must be checked first
        if age is None or age < 0 or age > 124:
            error_msg = "No age" if age is None else f"Invalid age: {age}"
            errors.append(error_msg)
            return GrouperResult(
                version=self.version,
                pdx=pdx,
                sdx=sdx,
                procedures=procedures,
                age=age,
                sex=sex,
                los=los,
                mdc="26",
                mdc_name="Ungroupable",
                dc="2653",
                drg="26539",
                drg_name="Age error",
                rw=0,
                rw0d=0,
                adjrw=0,
                wtlos=0,
                ot=0,
                pcl=0,
                cc_list=[],
                mcc_list=[],
                has_or_procedure=False,
                is_surgical=False,
                los_status="normal",
                is_valid=False,
                errors=errors,
                warnings=warnings,
                grouped_at=datetime.now().isoformat(),
            )

        # Validate Sex (Warning Code 32)
        if sex is None or sex not in ["M", "F", "1", "2"]:
            warnings.append(f"Missing or invalid sex: {sex}")

        pdx_info = self._get_icd10_info(pdx)
        if not pdx_info:
            errors.append(f"Invalid PDx: {pdx}")
            return GrouperResult(
                version=self.version,
                pdx=pdx,
                sdx=sdx,
                procedures=procedures,
                age=age,
                sex=sex,
                los=los,
                mdc="26",
                mdc_name="Ungroupable",
                dc="2650",
                drg="26509",
                drg_name="Invalid principal diagnosis",
                rw=0,
                rw0d=0,
                adjrw=0,
                wtlos=0,
                ot=0,
                pcl=0,
                cc_list=[],
                mcc_list=[],
                has_or_procedure=False,
                is_surgical=False,
                los_status="normal",
                is_valid=False,
                errors=errors,
                warnings=warnings,
                grouped_at=datetime.now().isoformat(),
            )

        mdc = pdx_info["mdc"]
        has_or = any(self._get_proc_info(p) and self._get_proc_info(p)["orp"] for p in procedures)
        pcl, cc_list, mcc_list = self._calculate_pcl(pdx, sdx)
        dc = self._find_dc(pdx, has_or)
        drg_info = self._find_drg(dc, pcl)
        adjrw, los_status = self._calculate_adjrw(
            drg_info["rw"], drg_info["rw0d"], drg_info["wtlos"], drg_info["ot"], los
        )
        is_surgical = has_or or (int(dc[2:]) < 50 if len(dc) >= 4 and dc[2:].isdigit() else False)

        return GrouperResult(
            version=self.version,
            pdx=pdx,
            sdx=sdx,
            procedures=procedures,
            age=age,
            sex=sex,
            los=los,
            mdc=mdc,
            mdc_name=MDC_NAMES.get(mdc, "Unknown"),
            dc=dc,
            drg=drg_info["drg"],
            drg_name=drg_info["name"],
            rw=drg_info["rw"],
            rw0d=drg_info["rw0d"],
            adjrw=adjrw,
            wtlos=drg_info["wtlos"],
            ot=drg_info["ot"],
            pcl=pcl,
            cc_list=cc_list,
            mcc_list=mcc_list,
            has_or_procedure=has_or,
            is_surgical=is_surgical,
            los_status=los_status,
            is_valid=True,
            errors=errors,
            warnings=warnings,
            grouped_at=datetime.now().isoformat(),
        )

    def get_stats(self) -> dict:
        return {
            "version": self.version,
            "icd10_count": len(self._icd10_data),
            "procedure_count": len(self._proc_data),
            "dc_count": len(self._drg_data),
            "drg_count": sum(len(drgs) for drgs in self._drg_data.values()),
            "cc_exclusion_count": len(self._cc_exclusions),
        }

    def get_drg_info(self, drg_code: str) -> Optional[dict]:
        for drgs in self._drg_data.values():
            for d in drgs:
                if d["drg"] == drg_code:
                    return d
        return None
