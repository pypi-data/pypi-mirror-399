"""
Thai DRG Grouper - Type Definitions
"""

import json
from dataclasses import asdict, dataclass, field
from typing import List, Optional


@dataclass
class VersionInfo:
    """Version information"""

    version: str
    name: str
    release_date: str
    source: str
    dbf_path: str
    is_default: bool = False
    rights: List[str] = field(default_factory=lambda: ["UC", "CSMBS", "SSS"])
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GrouperResult:
    """Grouper result"""

    version: str
    pdx: str
    sdx: List[str]
    procedures: List[str]
    age: Optional[int]
    sex: Optional[str]
    los: int
    mdc: str
    mdc_name: str
    dc: str
    drg: str
    drg_name: str
    rw: float
    rw0d: float
    adjrw: float
    wtlos: float
    ot: int
    pcl: int
    cc_list: List[str]
    mcc_list: List[str]
    has_or_procedure: bool
    is_surgical: bool
    los_status: str
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    grouped_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


# MDC Names
MDC_NAMES = {
    "00": "Pre-MDC",
    "01": "Diseases & Disorders of the Nervous System",
    "02": "Diseases & Disorders of the Eye",
    "03": "Diseases & Disorders of the Ear, Nose, Mouth & Throat",
    "04": "Diseases & Disorders of the Respiratory System",
    "05": "Diseases & Disorders of the Circulatory System",
    "06": "Diseases & Disorders of the Digestive System",
    "07": "Diseases & Disorders of the Hepatobiliary System & Pancreas",
    "08": "Diseases & Disorders of the Musculoskeletal System & Connective Tissue",
    "09": "Diseases & Disorders of the Skin, Subcutaneous Tissue & Breast",
    "10": "Endocrine, Nutritional & Metabolic Diseases & Disorders",
    "11": "Diseases & Disorders of the Kidney & Urinary Tract",
    "12": "Diseases & Disorders of the Male Reproductive System",
    "13": "Diseases & Disorders of the Female Reproductive System",
    "14": "Pregnancy, Childbirth & the Puerperium",
    "15": "Newborns & Other Neonates",
    "16": "Diseases & Disorders of Blood & Blood Forming Organs",
    "17": "Myeloproliferative Diseases & Disorders",
    "18": "Infectious & Parasitic Diseases",
    "19": "Mental Diseases & Disorders",
    "20": "Alcohol/Drug Use & Alcohol/Drug Induced Organic Mental Disorders",
    "21": "Injuries, Poisonings & Toxic Effects of Drugs",
    "22": "Burns",
    "23": "Factors Influencing Health Status",
    "24": "Multiple Significant Trauma",
    "25": "Human Immunodeficiency Virus Infections",
    "26": "Ungroupable",
}

MDC_NAMES_TH = {
    "00": "Pre-MDC",
    "01": "โรคและความผิดปกติของระบบประสาท",
    "02": "โรคและความผิดปกติของตา",
    "03": "โรคและความผิดปกติของหู จมูก ปาก และคอ",
    "04": "โรคและความผิดปกติของระบบหายใจ",
    "05": "โรคและความผิดปกติของระบบไหลเวียนโลหิต",
    "06": "โรคและความผิดปกติของระบบย่อยอาหาร",
    "07": "โรคและความผิดปกติของตับ ทางเดินน้ำดี และตับอ่อน",
    "08": "โรคและความผิดปกติของระบบกล้ามเนื้อ กระดูก และเนื้อเยื่อเกี่ยวพัน",
    "09": "โรคและความผิดปกติของผิวหนัง เนื้อเยื่อใต้ผิวหนัง และเต้านม",
    "10": "โรคของต่อมไร้ท่อ โภชนาการ และเมตาบอลิซึม",
    "11": "โรคและความผิดปกติของไตและทางเดินปัสสาวะ",
    "12": "โรคและความผิดปกติของระบบสืบพันธุ์ชาย",
    "13": "โรคและความผิดปกติของระบบสืบพันธุ์หญิง",
    "14": "การตั้งครรภ์ การคลอด และระยะหลังคลอด",
    "15": "ทารกแรกเกิดและทารกในระยะปริกำเนิด",
    "16": "โรคและความผิดปกติของเลือดและอวัยวะสร้างเลือด",
    "17": "โรคเกี่ยวกับการเพิ่มจำนวนของเซลล์เม็ดเลือด",
    "18": "โรคติดเชื้อและปรสิต",
    "19": "โรคทางจิตเวช",
    "20": "การใช้แอลกอฮอล์/ยาเสพติด",
    "21": "การบาดเจ็บ พิษ และผลจากสารพิษ",
    "22": "แผลไหม้",
    "23": "ปัจจัยที่มีผลต่อภาวะสุขภาพ",
    "24": "การบาดเจ็บหลายระบบ",
    "25": "การติดเชื้อเอชไอวี",
    "26": "ไม่สามารถจัดกลุ่มได้",
}
