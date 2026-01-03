"""
software.py

Project: pyads-ipc-diag
:author: Teemu Vartiainen
:license: MIT
:created on: 31.12.2025 9.06

"""
from dataclasses import dataclass
from typing import List

from .mdp_service import ConfigArea
from ..areas import CONFIG_AREA

@dataclass
class SoftwareInfo:
    names: List[str]
    companies: List[str]
    dates: List[str]
    versions: List[str]

class Software(ConfigArea):
    MODULE = CONFIG_AREA.SOFTWARE
    TABLE_BASE = 0x8001

    def __init__(self, ipc):
        super().__init__(ipc)
        self._names = None
        self._companies = None
        self._dates = None
        self._versions = None

    @property
    def names(self) -> List[str]:
        if self._names is None:
            self._names = self._read_table(0x8001, self._string)
        return self._names

    @property
    def companies(self) -> List[str]:
        if self._companies is None:
            self._companies = self._read_table(0x8002, self._string)
        return self._companies

    @property
    def dates(self) -> List[str]:
        if self._dates is None:
            self._dates = self._read_table(0x8003, self._string)
        return self._dates

    @property
    def versions(self) -> List[str]:
        if self._versions is None:
            self._versions = self._read_table(0x8004, self._string)
        return self._versions

    def refresh(self):
        self._names = None
        self._companies = None
        self._dates = None
        self._versions = None

    def properties(self) -> SoftwareInfo:
        return SoftwareInfo(
            names=self.names,
            companies=self.companies,
            dates=self.dates,
            versions=self.versions
        )