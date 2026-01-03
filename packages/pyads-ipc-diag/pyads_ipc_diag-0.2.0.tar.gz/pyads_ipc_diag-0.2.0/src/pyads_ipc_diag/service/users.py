"""
users.py

Project: pyads-ipc-diag
:author: Teemu Vartiainen
:license: MIT
:created on: 30.12.2025 15.42

"""
from dataclasses import dataclass

from .mdp_service import ConfigArea
from ..areas import CONFIG_AREA

class UserManagement(ConfigArea):
    MODULE = CONFIG_AREA.USER_MANAGEMENT

    def __init__(self, ipc):
        super().__init__(ipc)
        self._modules = self.ipc.mdp.get(self.MODULE)
        self._user_names = None
        self._domains = None
        self._group_memberships = None
        self._local_groups = None

    @property
    def user_names(self) -> str:
        if self._user_names is None:
            self._user_names = self._read_table(0x8001, self._string)

        return self._user_names

    @property
    def domains(self) -> str:
        if self._domains is None:
            self._domains = self._read_table(0x8002, self._string)

        return self._domains

    @property
    def group_memberships(self) -> str:
        if self._group_memberships is None:
            self._group_memberships = self._read_table(0x8003, self._string)

        return self._group_memberships

    @property
    def local_groups(self) -> str:
        if self._local_groups is None:
            self._local_groups = self._read_table(0x8004, self._string)

        return self._local_groups

    def properties(self):
        return {
            'users': self.user_names,
            'domains': self.domains,
            'group_memberships': self.group_memberships,
            'local_groups': self.local_groups
        }