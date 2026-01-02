"""
Thai DRG Grouper - Multi-Version Manager
"""

import json
import shutil
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .grouper import ThaiDRGGrouper
from .types import GrouperResult, VersionInfo


class ThaiDRGGrouperManager:
    """
    Manage multiple versions of Thai DRG Grouper

    Directory structure:
        versions/
        ├── config.json
        ├── 6.3/
        │   ├── version.json
        │   └── data/*.dbf
        └── 6.3.4/

    Example:
        manager = ThaiDRGGrouperManager('./versions')
        result = manager.group_latest(pdx='S82201D', los=5)
    """

    DOWNLOAD_URLS = {
        "6.3": "https://www.tcmc.or.th/_content_images/download/fileupload/S0021.zip",
        "5.1": "https://www.tcmc.or.th/_content_images/download/fileupload/S0033.zip",
    }

    def __init__(self, versions_path: str = "./versions"):
        self.versions_path = Path(versions_path)
        self.versions_path.mkdir(parents=True, exist_ok=True)

        self._groupers: Dict[str, ThaiDRGGrouper] = {}
        self._versions: Dict[str, VersionInfo] = {}
        self._default_version: Optional[str] = None

        self._load_config()
        self._scan_versions()

    def _load_config(self):
        config_path = self.versions_path / "config.json"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self._default_version = config.get("default_version")

    def _save_config(self):
        config_path = self.versions_path / "config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "default_version": self._default_version,
                    "last_updated": datetime.now().isoformat(),
                },
                f,
                indent=2,
            )

    def _scan_versions(self):
        self._versions.clear()

        for item in self.versions_path.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                version_json = item / "version.json"
                data_path = item / "data"

                if not data_path.exists():
                    dbf_files = list(item.glob("*.dbf"))
                    if dbf_files:
                        data_path = item

                if data_path.exists() and any(data_path.glob("*.dbf")):
                    info = {}
                    if version_json.exists():
                        with open(version_json, "r", encoding="utf-8") as f:
                            info = json.load(f)

                    version = info.get("version", item.name)
                    self._versions[version] = VersionInfo(
                        version=version,
                        name=info.get("name", f"Thai DRG {version}"),
                        release_date=info.get("release_date", "unknown"),
                        source=info.get("source", "tcmc.or.th"),
                        dbf_path=str(data_path),
                        is_default=(version == self._default_version),
                        rights=info.get("rights", ["UC", "CSMBS", "SSS"]),
                        notes=info.get("notes", ""),
                    )

        if not self._default_version and self._versions:
            self._default_version = sorted(self._versions.keys(), reverse=True)[0]
            self._save_config()

    def list_versions(self) -> List[VersionInfo]:
        return list(self._versions.values())

    def get_version_info(self, version: str) -> Optional[VersionInfo]:
        return self._versions.get(version)

    def get_default_version(self) -> Optional[str]:
        return self._default_version

    def set_default_version(self, version: str) -> bool:
        if version in self._versions:
            self._default_version = version
            for v in self._versions.values():
                v.is_default = v.version == version
            self._save_config()
            return True
        return False

    def _get_grouper(self, version: str) -> Optional[ThaiDRGGrouper]:
        if version not in self._versions:
            return None
        if version not in self._groupers:
            info = self._versions[version]
            self._groupers[version] = ThaiDRGGrouper(info.dbf_path, version)
        return self._groupers[version]

    def group(
        self,
        version: str,
        pdx: str,
        sdx: List[str] = None,
        procedures: List[str] = None,
        age: Optional[int] = None,
        sex: Optional[str] = None,
        los: int = 1,
        discharge_status: str = "normal",
    ) -> GrouperResult:
        """Group using specific version"""
        grouper = self._get_grouper(version)
        if not grouper:
            raise ValueError(
                f"Version {version} not found. Available: {list(self._versions.keys())}"
            )
        return grouper.group(pdx=pdx, sdx=sdx, procedures=procedures, age=age, sex=sex, los=los)

    def group_latest(
        self,
        pdx: str,
        sdx: List[str] = None,
        procedures: List[str] = None,
        age: Optional[int] = None,
        sex: Optional[str] = None,
        los: int = 1,
    ) -> GrouperResult:
        """Group using default version"""
        if not self._default_version:
            raise ValueError("No versions available")
        return self.group(
            self._default_version,
            pdx=pdx,
            sdx=sdx,
            procedures=procedures,
            age=age,
            sex=sex,
            los=los,
        )

    def group_all_versions(
        self,
        pdx: str,
        sdx: List[str] = None,
        procedures: List[str] = None,
        age: Optional[int] = None,
        sex: Optional[str] = None,
        los: int = 1,
    ) -> Dict[str, GrouperResult]:
        """Group using all versions for comparison"""
        results = {}
        for version in self._versions:
            try:
                results[version] = self.group(
                    version, pdx=pdx, sdx=sdx, procedures=procedures, age=age, sex=sex, los=los
                )
            except Exception:
                results[version] = None
        return results

    def add_version(
        self,
        version: str,
        source_path: str,
        name: str = None,
        release_date: str = None,
        rights: List[str] = None,
        notes: str = "",
        set_default: bool = False,
    ) -> bool:
        """Add a new version"""
        version_path = self.versions_path / version
        data_path = version_path / "data"
        version_path.mkdir(parents=True, exist_ok=True)
        data_path.mkdir(exist_ok=True)

        source = Path(source_path)

        if source.suffix.lower() == ".zip":
            with zipfile.ZipFile(source, "r") as zf:
                for member in zf.namelist():
                    if member.lower().endswith(".dbf"):
                        zf.extract(member, version_path)
                        extracted = version_path / member
                        if extracted.exists():
                            shutil.move(str(extracted), str(data_path / Path(member).name))
        else:
            for dbf_file in source.glob("**/*.dbf"):
                shutil.copy2(dbf_file, data_path / dbf_file.name)

        with open(version_path / "version.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "version": version,
                    "name": name or f"Thai DRG {version}",
                    "release_date": release_date or datetime.now().strftime("%Y-%m-%d"),
                    "source": str(source_path),
                    "rights": rights or ["UC", "CSMBS", "SSS"],
                    "notes": notes,
                    "added_at": datetime.now().isoformat(),
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

        self._scan_versions()
        if set_default:
            self.set_default_version(version)

        return version in self._versions

    def download_version(self, version: str, set_default: bool = False) -> bool:
        """Download version from tcmc.or.th"""
        if version not in self.DOWNLOAD_URLS:
            return False

        url = self.DOWNLOAD_URLS[version]
        temp_zip = self.versions_path / f"temp_{version}.zip"

        try:
            urllib.request.urlretrieve(url, temp_zip)
            success = self.add_version(
                version=version, source_path=str(temp_zip), set_default=set_default
            )
            temp_zip.unlink()
            return success
        except Exception:
            if temp_zip.exists():
                temp_zip.unlink()
            return False

    def remove_version(self, version: str) -> bool:
        """Remove a version"""
        if version not in self._versions:
            return False

        version_path = self.versions_path / version
        if version_path.exists():
            shutil.rmtree(version_path)

        if version in self._groupers:
            del self._groupers[version]

        if self._default_version == version:
            self._default_version = None
            self._save_config()

        self._scan_versions()
        return True

    def get_stats(self, version: str = None) -> dict:
        if version:
            grouper = self._get_grouper(version)
            return grouper.get_stats() if grouper else {}
        return {v: self._get_grouper(v).get_stats() for v in self._versions}
