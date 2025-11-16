GPIO_DI_MAP: dict[int, int] = {
    17: 0,  # Feed back pump 1 Run
    27: 1,  # Feed back pump 2 Run
    22: 2,  # Feed back pump 3 Run
    5: 3,   # Pump 1 Hand
    6: 4,   # Pump 1 Auto
    26: 5,  # Pump 2 Hand
    16: 6,  # Pump 2 Auto
    20: 7,  # Pump 3 Hand
    21: 8,  # Pump 3 Auto
    4: 9,   # Emergency stop
}

GPIO_DO_MAP: dict[int, int] = {
    23: 0,  # Cmd pump 1 Run
    24: 1,  # Cmd pump 2 Run
    25: 2,  # Cmd pump 3 Run
}
