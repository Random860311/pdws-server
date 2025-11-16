from dataclasses import dataclass
from typing import Sequence, Tuple

from common import utils
from device.base.device_status import EDeviceStatus
from device.system.system_priority import ESystemPriority
from device.system.system_protocol import SystemProtocol
from station.alternatator.alternator_protocol import AlternatorProtocol

@dataclass
class SystemStatus:
    crit_fault_count: int
    can_run_auto_count: int
    all_stopped: bool
    fail_to_start: int = 0


class TimeAlternator(AlternatorProtocol):
    def __init__(self, systems: Sequence[SystemProtocol]):
        self.__systems = systems
        self.__system_status = self.get_system_status(systems)
        self.__systems_order: Sequence[Tuple[int, int]] = []

    @property
    def systems(self) -> Sequence[SystemProtocol]:
        return self.__systems

    @staticmethod
    def get_system_status(systems: Sequence[SystemProtocol]) -> SystemStatus:
        result = SystemStatus(crit_fault_count=0, can_run_auto_count=0, all_stopped=True)
        for i, sys in enumerate(systems):
            result.all_stopped &= sys.status == EDeviceStatus.STOPPED
            result.crit_fault_count += 1 if sys.has_critical_alarm else 0
            result.can_run_auto_count += 1 if sys.can_run_auto else 0
            if sys.alarm_fail_to_start:
                result.fail_to_start |= (1 << i)
            else:
                result.fail_to_start &= ~(1 << i)
        return result

    def alternate(self) -> None:
        current_status = self.get_system_status(self.systems)
        if self.__systems_order and current_status == self.__system_status:
            return

        self.__system_status = current_status

        # keep only systems that can run in auto
        candidates = [sys for sys in self.systems if (sys.can_run_auto and not sys.alarm_fail_to_start)]
        if not candidates:
            self.__systems_order = []
        else:
            # sort by run_time (ascending). stable sort preserves input order on ties
            ordered = sorted(candidates, key=lambda s: s.run_time_total)

            # assign priorities: 0,1,2,... (lower runtime → lower priority number)
            self.__systems_order = [(sys.device_id, prio) for prio, sys in enumerate(ordered)]

        for sys in self.__systems:
            sys.priority_auto = ESystemPriority.OUT
            for order in self.__systems_order:
                if sys.device_id == order[0]:
                    sys.priority_auto = utils.enum_from_any(ESystemPriority, order[1], ESystemPriority.OUT)
                    break