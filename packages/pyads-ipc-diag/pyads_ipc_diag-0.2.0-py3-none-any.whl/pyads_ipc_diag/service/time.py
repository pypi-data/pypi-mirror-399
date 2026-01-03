"""
time.py

Project: pyads-ipc-diag
:author: Teemu Vartiainen
:license: MIT
:created on: 30.12.2025 8.56

"""
from typing import List
from dataclasses import dataclass
import datetime

from .mdp_service import ConfigArea
from ..areas import CONFIG_AREA

@dataclass
class TimeInfo:
    length: int
    sntp_server: str
    sntp_refresh: int
    unix_time: int
    datetime: datetime.datetime
    timezone: str
    time_offset: int

class Time(ConfigArea):
    MODULE = CONFIG_AREA.TIME

    def __init__(self, ipc):
        """ Initialize Time
        For property documentation, see:
        https://infosys.beckhoff.com/content/1033/devicemanager/263027979.html?id=8041884874648754543
        :param ipc
        """
        super().__init__(ipc)
        self._length = None
        self._sntp_server = None
        self._sntp_refresh = None
        self._unix_time = None
        self._datetime = None
        self._timezone = None
        self._time_offset = None

    @property
    def length(self) -> int:
        """Len"""
        if self._length is None:
            self._length = self._u16(0)
        return self._length

    @property
    def sntp_server(self) -> str:
        """SNTP Server:

        Name or IP Address of the timeserver
        "NoSync" = No synchronization
        "NT5DS" = Use domain hierarchy settings (Win32 only – no WinCE)
        May contain the following flags: See "NtpServer" msdn (Win32 only – no WinCE)

        *The system must be rebooted in order for the changes to take effect."""
        if self._sntp_server is None:
            self._sntp_server = self._string(1)
        return self._sntp_server

    @property
    def sntp_refresh(self) -> int:
        """SNTP Refresh in Seconds
        On WindowsCE lowest allowed value is 5 Seconds

        The system must be rebooted in order for the changes to take effect."""
        if self._sntp_refresh is None:
            self._sntp_refresh = self._u32(2)
        return self._sntp_refresh

    @property
    def unix_time(self) -> int:
        """Seconds since midnight January 1, 1970 (local time)"""
        if self._unix_time is None:
            self._unix_time = self._u32(3)
        return self._unix_time

    @property
    def datetime(self) -> datetime.datetime:
        """Local date and time.

        Returned as ``datetime.datetime`` converted from the device's
        ISO 8601 textual representation."""
        if self._datetime is None:
            datetime_str = self._string(4)
            self._datetime = datetime.datetime.fromisoformat(datetime_str)
        return self._datetime

    @property
    def timezone(self) -> str:
        """Timezone
        Returns timezone of the device as a string
        Not supported on TC/RTOS """
        if self._timezone is None:
            idx = self._u16(5)
            if idx is None:
                self._timezone = None
            else:
                self._timezone = self.timezones()[idx]

        return self._timezone

    @property
    def time_offset(self) -> int:
        """Time Offset
        Offset in seconds of the current local time relative to the coordinated universal time (UTC)
        (supports only steps of 15 minutes = 900 seconds)

        Only for TC/RTOS """
        if self._time_offset is None:
            self._time_offset = self._s32(6)
        return self._time_offset

    def properties(self):
        """ Return all Time table properties as TimeInfo object"""
        return TimeInfo(
            length=self.length,
            sntp_server=self.sntp_server,
            sntp_refresh=self.sntp_refresh,
            unix_time=self.unix_time,
            datetime=self.datetime,
            timezone=self.timezone,
            time_offset=self.time_offset
        )

    def refresh(self):
        self._length = None
        self._sntp_server = None
        self._sntp_refresh = None
        self._unix_time = None
        self._datetime = None
        self._timezone = None
        self._time_offset = None

    def timezones(self) -> List[str]:
        """ Returns a list of timezones
        Based on Information model documentation, the timezones might be in two tables """
        tz1 = self._read_table(0x8002, self._string)
        tz2 = self._read_table(0x8003, self._string)
        if tz1 is None:
            return None

        if tz2 is None:
            return tz1

        return tz1 + tz2
