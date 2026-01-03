"""
fan.py

Project: pyads-ipc-diag
:author: Teemu Vartiainen
:license: MIT
:created on: 23.12.2025 10.59

"""
from dataclasses import dataclass

from .mdp_service import ConfigArea
from ..areas import CONFIG_AREA

@dataclass
class FanInfo:
    speed: int

class Fan(ConfigArea):
    MODULE = CONFIG_AREA.FAN

    def __init__(self, ipc):
        super().__init__(ipc)
        self._speed = None

    @property
    def speed(self):
        """ Fan speed """
        if self._speed is None:
            self._speed = self._s16(1)
        return self._speed

    def info(self) -> FanInfo:
        """ Return Fan info """
        return FanInfo(speed=self.speed)

    def refresh(self):
        """Force re-reading all fan values from IPC"""
        self._speed = None