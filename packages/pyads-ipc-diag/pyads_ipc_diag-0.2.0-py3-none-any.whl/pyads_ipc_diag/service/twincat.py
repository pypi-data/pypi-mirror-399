"""
twincat.py

Project: pyads-ipc-diag
:author: Teemu Vartiainen
:license: MIT
:created on: 23.12.2025 9.30

"""
from dataclasses import dataclass

from .mdp_service import ConfigArea
from ..areas import CONFIG_AREA

@dataclass
class TwinCATRouterInfo: # Only supported on TC/RTOS
    memory_max: int
    memory_available: int
    registered_ports: int
    registered_drivers: int
    registered_transports: int
    debug_windows: bool
    mailbox_size: int
    mailbox_used: int

@dataclass
class ExtendedInformation: # Only supported on TC/RTOS
    heap_memory_max: int
    heap_memory_available: int

@dataclass
class TwinCATInfo:
    major: int
    minor: int
    build: int
    ams_net_id: str
    reg_level: int
    status: int
    run_as_device: int
    show_target_visu: int
    log_file_size: int
    log_file_path: str
    system_id: str
    revision: int
    seconds_since_status_change: int
    twincat_route_names: str # List of strings
    twincat_route_addresses: str # List of strings
    twincat_ams_addresses: str # List of strings
    twincat_route_flags: str # List of ints
    twincat_route_timeouts: int # List of ints
    twincat_route_transports: int # List of ints
    twincat_log_file: str
    twincat_router_information: TwinCATRouterInfo
    extended_information: ExtendedInformation


class TwinCAT(ConfigArea):
    MODULE = CONFIG_AREA.TWINCAT
    TABLE_BASE = 0x8001

    def __init__(self, ipc):
        super().__init__(ipc)
        self._major = None
        self._minor = None
        self._build = None
        self._ams_net_id = None
        self._reg_level = None
        self._status = None
        self._run_as_device = None
        self._show_target_visu = None
        self._log_file_size = None
        self._log_file_path = None
        self._system_id = None
        self._revision = None
        self._seconds_since_status_change = None
        self._twincat_route_names = None
        self._twincat_route_addresses = None
        self._twincat_ams_addresses = None
        self._twincat_route_flags = None
        self._twincat_route_timeouts = None
        self._twincat_route_transports = None
        self._twincat_log_file = None
        self._twincat_router_information = None
        self._extended_information = None

    @property
    def major(self) -> int:
        """Major Version (UNSIGNED16)"""
        if self._major is None:
            self._major = self._u16(1)
        return self._major

    @property
    def minor(self) -> int:
        """Minor Version (UNSIGNED16)"""
        if self._minor is None:
            self._minor = self._u16(2)
        return self._minor

    @property
    def build(self) -> int:
        """Build (UNSIGNED16)"""
        if self._build is None:
            self._build = self._u16(3)
        return self._build

    @property
    def ams_net_id(self) -> str:
        """Ams Net ID (VISIBLE STRING)"""
        if self._ams_net_id is None:
            self._ams_net_id = self._string(4)
        return self._ams_net_id

    @property
    def reg_level(self) -> int:
        """Reg Level (UNSIGNED32) - only for TwinCAT 2"""
        if self._reg_level is None:
            self._reg_level = self._u32(5)
        return self._reg_level

    @property
    def status(self) -> int:
        """TwinCAT Status (UNSIGNED16)"""
        if self._status is None:
            self._status = self._u16(6)
        return self._status

    @property
    def run_as_device(self) -> int:
        """RunAsDevice (UNSIGNED16) - only for Windows CE"""
        if self._run_as_device is None:
            self._run_as_device = self._u16(7)
        return self._run_as_device

    @property
    def show_target_visu(self) -> int:
        """ShowTargetVisu (UNSIGNED16) - only for Windows CE"""
        if self._show_target_visu is None:
            self._show_target_visu = self._u16(8)
        return self._show_target_visu

    @property
    def log_file_size(self) -> int:
        """Log File size (UNSIGNED32) - only for Windows CE"""
        if self._log_file_size is None:
            self._log_file_size = self._u32(9)
        return self._log_file_size

    @property
    def log_file_path(self) -> str:
        """Log File Path (VISIBLE STRING) - only for Windows CE"""
        if self._log_file_path is None:
            self._log_file_path = self._string(10)
        return self._log_file_path

    @property
    def system_id(self) -> str:
        """TwinCAT System ID (VISIBLE STRING) - MDP v1.6+"""
        if self._system_id is None:
            self._system_id = self._string(11)
        return self._system_id

    @property
    def revision(self) -> int:
        """TwinCAT Revision (UNSIGNED16)"""
        if self._revision is None:
            self._revision = self._u16(12)
        return self._revision

    @property
    def seconds_since_status_change(self) -> int:
        """Seconds since last TwinCAT status change (UNSIGNED64)"""
        if self._seconds_since_status_change is None:
            self._seconds_since_status_change = self._u64(13)
        return self._seconds_since_status_change

    @property
    def twincat_route_names(self) -> str:
        if self._twincat_route_names is None:
            self._twincat_route_names = self._read_table(0x8002, self._string)
        return self._twincat_route_names

    @property
    def twincat_route_addresses(self) -> str:
        if self._twincat_route_addresses is None:
            self._twincat_route_addresses = self._read_table(0x8003, self._string)
        return self._twincat_route_addresses

    @property
    def twincat_ams_addresses(self) -> str:
        if self._twincat_ams_addresses is None:
            self._twincat_ams_addresses = self._read_table(0x8004, self._string)
        return self._twincat_ams_addresses

    @property
    def twincat_route_flags(self) -> str:
        if self._twincat_route_flags is None:
            self._twincat_route_flags = self._read_table(0x8005, self._u32)
        return self._twincat_route_flags

    @property
    def twincat_route_timeouts(self) -> str:
        if self._twincat_route_timeouts is None:
            self._twincat_route_timeouts = self._read_table(0x8006, self._u32)
        return self._twincat_route_timeouts

    @property
    def twincat_route_transports(self) -> str:
        if self._twincat_route_transports is None:
            self._twincat_route_transports = self._read_table(0x8007, self._u16)
        return self._twincat_route_transports

    @property
    def twincat_log_file(self) -> str:
        if self._twincat_log_file is None:
            self._twincat_log_file = self._read_table(0x8008, data_types=[self._string])
        return self._twincat_log_file

    @property
    def twincat_router_information(self) -> str:
        if self._twincat_router_information is None:
            data = self._read_table(
                0x8009,
                data_types=[
                    self._u16, # Len
                    self._u64, # Router Memory Maximum
                    self._u64, # Router Memory Available
                    self._u32, # Registered Ports
                    self._u32, # Registered Drivers
                    self._u32, # Registered Transports
                    self._bool, # Debug Window – True if Ads Logger is active
                    self._u32, # Mailbox Size
                    self._u32 # Mailbox Used Entries
                ])
            self._twincat_router_information = TwinCATRouterInfo(
                memory_max = data[1],
                memory_available = data[2],
                registered_ports = data[3],
                registered_drivers = data[4],
                registered_transports = data[5],
                debug_windows = data[6],
                mailbox_size = data[7],
                mailbox_used = data[8],
            )
        return self._twincat_router_information

    @property
    def extended_information(self) -> str:
        if self._extended_information is None:
            data = self._read_table(
                0x800A,
                data_types=[
                    self._u16, # Len
                    self._u64, # TwinCAT Heap Memory Maximum – Maximum available Memory for TcOs Instance
                    self._u64, # TwinCAT Heap Memory Available – free Memory in TcOs Instance
                ])
            self._extended_information = ExtendedInformation(
                heap_memory_max = data[1],
                heap_memory_available = data[2],
            )
        return self._extended_information

    def properties(self) -> TwinCATInfo:
        """Return all TwinCAT information as a dataclass"""
        return TwinCATInfo(
            major=self.major,
            minor=self.minor,
            build=self.build,
            ams_net_id=self.ams_net_id,
            reg_level=self.reg_level,
            status=self.status,
            run_as_device=self.run_as_device,
            show_target_visu=self.show_target_visu,
            log_file_size=self.log_file_size,
            log_file_path=self.log_file_path,
            system_id=self.system_id,
            revision=self.revision,
            seconds_since_status_change=self.seconds_since_status_change,
            twincat_route_names=self.twincat_route_names,
            twincat_route_addresses=self.twincat_route_addresses,
            twincat_ams_addresses=self.twincat_ams_addresses,
            twincat_route_flags=self.twincat_route_flags,
            twincat_route_timeouts=self.twincat_route_timeouts,
            twincat_route_transports=self.twincat_route_transports,
            twincat_log_file=self.twincat_log_file,
            twincat_router_information=self.twincat_router_information,
            extended_information=self.extended_information
        )

    def refresh(self):
        """Force re-reading all TwinCAT values from IPC"""
        self._major = None
        self._minor = None
        self._build = None
        self._ams_net_id = None
        self._reg_level = None
        self._status = None
        self._run_as_device = None
        self._show_target_visu = None
        self._log_file_size = None
        self._log_file_path = None
        self._system_id = None
        self._revision = None
        self._seconds_since_status_change = None
        self._twincat_route_names = None
        self._twincat_route_addresses = None
        self._twincat_ams_addresses = None
        self._twincat_route_flags = None
        self._twincat_route_timeouts = None
        self._twincat_route_transports = None
        self._twincat_log_file = None
        self._twincat_router_information = None
        self._extended_information = None

    def version(self):
        """Convenience: return (major, minor, build)"""
        return self.major, self.minor, self.build