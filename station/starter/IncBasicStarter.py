import time
from typing import Sequence

from device.sensor.sensor_protocol import SensorProtocol
from device.system.system_protocol import SystemProtocol
from services.application.application_service_protocol import ApplicationServiceProtocol
from station.starter.BaseStarter import BaseStarter


class IncBasicStarter(BaseStarter):
    def __init__(self, app_service: ApplicationServiceProtocol, sensor: SensorProtocol, systems: Sequence[SystemProtocol]):
        super().__init__(app_service, sensor, systems)

    def should_start(self) -> bool:
        call_time = time.perf_counter()
        if self.sensor.value_scaled < (self.set_point - self.offset):
            if self.start_call_time == 0.0:
                self.start_call_time = call_time
        else:
            self.start_call_time = 0.0
        # print(f"start_call_time: {self.start_call_time}, call_time: {call_time}, diff: {call_time - self.start_call_time}, start_delay: {self.start_delay}")
        return (self.start_call_time > 0) and ((call_time - self.start_call_time) >= self.start_delay)

    def should_stop(self) -> bool:
        call_time = time.perf_counter()
        if self.sensor.value_scaled > (self.set_point + self.offset):
            if self.stop_call_time == 0.0:
                self.stop_call_time = call_time
        else:
            self.stop_call_time = 0.0

        return (self.stop_call_time > 0) and ((call_time - self.stop_call_time) >= self.stop_delay)