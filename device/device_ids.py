from enum import Enum


class EDeviceIds(int, Enum):
    SENSOR_PRESSURE = 1
    SENSOR_ADDITIONAL = 2

    PUMP_1 = 1
    PUMP_2 = 2
    PUMP_3 = 3
    PUMP_4 = 4

    CONTACTOR_1 = 1
    CONTACTOR_2 = 2
    CONTACTOR_3 = 3
    CONTACTOR_4 = 4

    SYSTEM_1 = 1
    SYSTEM_2 = 2
    SYSTEM_3 = 3
    SYSTEM_4 = 4
