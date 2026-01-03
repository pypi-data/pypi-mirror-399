from enum import Enum


class Attribute(str, Enum):
    Power = "A02"
    Mode = "A03"
    Airflow = "A04"
    Plasmawave = "A07"
    FilterHours = "A21"
    AirQuality = "S07"
    AmbientLight = "S14"


class Power(str, Enum):
    Off = "0"
    On = "1"


class Mode(str, Enum):
    Auto = "01"
    Manual = "02"


class Airflow(str, Enum):
    Low = "01"
    Medium = "02"
    High = "03"
    Turbo = "05"
    Sleep = "06"


class AirQuality(str, Enum):

    Good = "01"
    Fair = "02"
    Poor = "03"

    @classmethod
    def _missing_(cls, value):
        mapping = {
            "1.0": cls.Good,
            "2.0": cls.Fair,
            "3.0": cls.Poor,
            1.0: cls.Good,
            2.0: cls.Fair,
            3.0: cls.Poor,
            1: cls.Good,
            2: cls.Fair,
            3: cls.Poor,
        }
        if value in mapping:
            return mapping[value]
        try:
            int_value = int(float(value))
            return mapping.get(int_value)
        except Exception:
            pass
        raise ValueError(f"{value!r} is not a valid {cls.__qualname__}")


class Plasmawave(str, Enum):
    Off = "0"
    On = "1"


class DeviceStatus:
    def __init__(
        self, power, mode, airflow, air_quality, plasmawave, ambient_light, filter_hours
    ):
        self.power = power
        self.mode = mode
        self.airflow = airflow
        self.air_quality = air_quality
        self.plasmawave = plasmawave
        self.ambient_light = ambient_light
        self.filter_hours = filter_hours
