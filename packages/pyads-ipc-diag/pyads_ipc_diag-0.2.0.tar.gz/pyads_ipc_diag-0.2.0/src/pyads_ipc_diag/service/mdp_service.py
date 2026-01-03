"""
mdp_service.py

Project: pyads-ipc-diag
:author: Teemu Vartiainen
:license: MIT
:created on: 22.12.2025 13.51

"""
from dataclasses import dataclass

from typing import Union, Optional
from pyads_ipc_diag import data_types as dtypes

@dataclass
class ModuleHeader:
    length: int
    address: int
    module_type: str
    name: str
    dev_type: int

class MDPService:
    """High level class for reading MDP data """
    def __init__(self, ipc):
        self.ipc = ipc

    def _read(self, subindex, var_type) -> Union[int, str, bool, None] :
        return self.ipc.read(self.MODULE, self.TABLE_BASE, subindex, var_type)

    def _u16(self, subindex: int) -> int:
        return self._read(subindex, dtypes.UNSIGNED16)

    def _s16(self, subindex: int) -> int:
        return self._read(subindex, dtypes.SIGNED16)

    def _u32(self, subindex: int) -> int:
        return self._read(subindex, dtypes.UNSIGNED32)

    def _s32(self, subindex: int) -> int:
        return self._read(subindex, dtypes.SIGNED32)

    def _u64(self, subindex: int) -> int:
        return self._read(subindex, dtypes.UNSIGNED64)

    def _string(self, subindex: int) -> str:
        return self._read(subindex, dtypes.VISIBLE_STRING)

    def _bool(self, subindex: int) -> bool:
        return self._read(subindex, dtypes.BOOL)

class ConfigArea(MDPService):
    """ Class for reading configuration area data """
    TABLE_BASE = 0x8001

    def __init__(self, ipc):
        super().__init__(ipc)
        self._header_cache: Optional[ModuleHeader] = None

    def header(self) -> ModuleHeader:
        """Header data (cached)."""
        if self._header_cache is None:
            self._header_cache = ModuleHeader(
                length=self._u16(0),
                address=self._u32(1),
                module_type=self._string(2),
                name=self._string(3),
                dev_type=self._u32(4),
            )
        return self._header_cache

    def _read_table(self, table_base, data_type=None, data_types=None):
        if data_type is None and data_types is None:
            raise Exception('Either data_type or data_types should be provided')

        orig_table_base= self.TABLE_BASE
        self.TABLE_BASE = table_base
        values = []

        if data_types is None:
            length = self._u16(0)
            if length is not None:
                for i in range(1, length+1):
                    values.append(data_type(i))

        else:
            length = len(data_types)
            for i in range(0, length):
                values.append(data_types[i](i))

        self.TABLE_BASE = orig_table_base
        return values

    def properties(self):
        """ This is overwritten by modules """
        return None

    def info(self) -> dict:
        """Return all information as dictionary"""
        return {
            'Header': self.header(),
            'Properties': self.properties(),
        }