import ast
from enum import Enum
from dataclasses import dataclass


class MotorSide(Enum):
    LEFT = 1
    RIGHT = 2


class MotorDirection(Enum):
    FORWARD = 1
    BACKWARD = -1


class ValueWithDirection:
    def __init__(self, raw_value: float):
        self.value = abs(raw_value)
        self.sign = 1.0 if raw_value >= 0.0 else -1.0

    def abs_value(self) -> float:
        return self.value

    def update_abs_value(self, v: float) -> None:
        if v < 0.0:
            raise RuntimeError(f"update_abs_value was given a negative value {v}")
        self.value = v

    def signed_value(self) -> float:
        return self.value * self.sign

    def __repr__(self):
        return f"[sign:{self.sign}, value:{self.value}]"


class EncoderData:
    def __init__(self, side: MotorSide, pwm_percent: float, motor_rpm: float, wheel_rpm: float, speed_mm_sec: float,
                 timestamp: int, pin_state: str):
        self.side: MotorSide = side
        self.pwm_percent: float = pwm_percent
        self.wheel_rpm: float = wheel_rpm
        self.speed_mm_sec: float = speed_mm_sec
        self.timestamp: int = timestamp
        if pin_state not in ['F', 'B']:
            raise RuntimeError(f"EncoderData.init - invalid pin_state {pin_state}")
        if self.side == MotorSide.LEFT:
            self.pin_state = 'F' if pin_state == 'B' else 'F'
        else:
            self.pin_state = pin_state

        # self.motor_rpm = ValueWithDirection(abs(motor_rpm) if self.pin_state == 'F' else -1.0*abs(motor_rpm))
        self.motor_rpm = (abs(motor_rpm) if self.pin_state == 'F' else -1.0 * abs(motor_rpm))

    def get_abs_motor_rpm(self) -> float:
        return abs(self.motor_rpm)

    def get_signed_motor_rpm(self) -> float:
        return self.motor_rpm


@dataclass
class BothEncoders:
    left: EncoderData
    right: EncoderData


def both_encoders_from_json_string(data: str) -> BothEncoders:
    jsondata = ast.literal_eval(data)

    if type(jsondata) is list and len(jsondata) == 2:
        encoders = BothEncoders(
            left=EncoderData(
                MotorSide.LEFT,
                jsondata[0]['pwm'],
                jsondata[0]['mr'],
                jsondata[0]['wr'],
                jsondata[0]['sd'],
                jsondata[0]['ts'],
                jsondata[0]['ps'],
            ),
            right=EncoderData(
                MotorSide.RIGHT,
                jsondata[1]['pwm'],
                jsondata[1]['mr'],
                jsondata[1]['wr'],
                jsondata[1]['sd'],
                jsondata[1]['ts'],
                jsondata[1]['ps'],
            )
        )
    else:
        raise RuntimeError("invalid json data")
    return encoders


def make_encoders(pwm_percent: float, data: str) -> BothEncoders:
    jsondata = ast.literal_eval(data)

    if type(jsondata) is list and len(jsondata) == 2:
        encoders = BothEncoders(
            left=EncoderData(
                MotorSide.LEFT,
                pwm_percent,
                jsondata[0]['mr'],
                jsondata[0]['wr'],
                jsondata[0]['sd'],
                jsondata[0]['ts'],
                jsondata[0]['ps']
            ),
            right=EncoderData(
                MotorSide.RIGHT,
                pwm_percent,
                jsondata[1]['mr'],
                jsondata[1]['wr'],
                jsondata[1]['sd'],
                jsondata[1]['ts'],
                jsondata[0]['ps']
            )
        )
    else:
        raise RuntimeError("invalid json data")
    return encoders
