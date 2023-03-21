from dataclasses import dataclass
from typing import Any

from construct import (
    Array,
    BitsInteger,
    Bytes,
    Checksum,
    Computed,
    Const,
    Default,
    ExprValidator,
    Flag,
    Hex,
    HexDump,
    Int8ub,
    Int16ub,
    PaddedString,
    RawCopy,
    Rebuild,
    Select,
    Switch,
    Transformed,
    obj_,
    this,
)
from construct_typed import (
    DataclassBitStruct,
    DataclassMixin,
    DataclassStruct,
    EnumBase,
    FlagsEnumBase,
    TEnum,
    TFlagsEnum,
    csfield,
)


# TODO:
# Some AM43 responses expect a confirmation from the client (0xA1, 0xA3, 0xA6 and 0xA2).
# Those responses must be formatted in the same way OperationResult is formatted
# i.e. using values from ContentOperationResult instead of the checksum in the footer.
class RequestMessageType(EnumBase):
    LIMIT_OR_RESET = 0x22
    SEND_TIME = 0x14
    UPDATE_TIMER = 0x15
    UPDATE_SEASON = 0x16
    PASSWORD = 0x17
    PASSWORD_CHANGE = 0x18
    CONTROL_DIRECT = 0x0A
    CONTROL_PERCENT = 0x0D
    UPDATE_SETTINGS = 0x11
    REQUEST_BATTERY_STATUS = 0xA2
    REQUEST_SETTINGS = 0xA7
    REQUEST_ILLUMINANCE = 0xAA
    CHANGE_NAME = 0x35


class ResponseMessageType(EnumBase):
    # Everything from RequestMessageType
    LIMIT_OR_RESET = 0x22
    SEND_TIME = 0x14
    UPDATE_TIMER = 0x15
    UPDATE_SEASON = 0x16
    PASSWORD = 0x17
    PASSWORD_CHANGE = 0x18
    CONTROL_DIRECT = 0x0A
    CONTROL_PERCENT = 0x0D
    UPDATE_SETTINGS = 0x11
    REQUEST_BATTERY_STATUS = 0xA2
    REQUEST_SETTINGS = 0xA7
    REQUEST_ILLUMINANCE = 0xAA
    CHANGE_NAME = 0x35

    # Some extra message types
    FINISHED_MOVING = 0xA1
    SPEED = 0xA3  # TODO: not implemented
    FAULT = 0xA6  # TODO: not implemented
    LIST_TIMERS = 0xA8
    LIST_SEASONS = 0xA9


class ContentControlDirect(EnumBase):
    STOP = 0xCC
    OPEN = 0xDD
    CLOSE = 0xEE


class ContentLimit(EnumBase):
    SAVE = 0x20
    EXIT = 0x40


class SeasonLightSwitchState(EnumBase):
    ALL_CLOSE = 0x00
    OPEN2OPEN_CLOSE2CLOSE = 0x10
    OPEN2STOP_CLOSE2OPEN = 0x01
    OPEN2OPEN_CLOSE2OPEN = 0x11


class ContentLimitSet(EnumBase):
    INIT_SUCCESS = 0x5A
    SUCCESS = 0x5B
    EXIT = 0x5C
    TIMEOUT = 0xA5
    FAILURE = 0xB5


class ContentReset(EnumBase):
    SUCCESS = 0xC5


class ContentOperationResult(EnumBase):
    SUCCESS = 0x5A
    FAILURE = 0xA5


class DeviceType(EnumBase):
    VENETIAN_BLIND = 1
    VERTICAL_BLIND = 2
    ROLLER_SHADE = 3
    HONEYCOMB_SHADE = 4
    ZEBRA_SHADE = 5
    TRIPPLE_SHADE = 8


class UpdateTimerAction(EnumBase):
    UPDATE = 0
    DELETE = 1


def xor_checksum(data: bytearray) -> int:
    checksum = 0
    for byte in data:
        checksum = checksum ^ byte

    return checksum


class LimitCommand(EnumBase):
    INIT = 0x00
    SAVE = 0x20
    EXIT = 0x40


class SetLimitMode(EnumBase):
    UNDEFINED = 0
    TOP = 1
    BOTTOM = 2


@dataclass
class LimitOrReset(DataclassMixin):
    command: LimitCommand = csfield(TEnum(Int8ub, LimitCommand))
    limit_mode: SetLimitMode = csfield(TEnum(Int8ub, SetLimitMode))
    is_reset: bool = csfield(
        ExprValidator(
            Default(Flag, False),
            lambda obj, ctx: (
                obj
                and ctx.command == LimitCommand.INIT
                and ctx.limit_mode == SetLimitMode.UNDEFINED
            )
            or (not obj and ctx.limit_mode != SetLimitMode.UNDEFINED),
        )
    )


@dataclass
class SendTime(DataclassMixin):
    # Day of the week, where 0 is Sunday and 6 is Saturday
    day_of_week: int = csfield(ExprValidator(Int8ub, obj_ >= 0 and obj_ <= 6))
    hour: int = csfield(ExprValidator(Int8ub, obj_ >= 0 and obj_ <= 23))
    minute: int = csfield(ExprValidator(Int8ub, obj_ >= 0 and obj_ <= 59))
    second: int = csfield(ExprValidator(Int8ub, obj_ >= 0 and obj_ <= 59))


@dataclass
class AlwaysOne(DataclassMixin):
    body: int = csfield(Const(b"\x01"))


@dataclass
class DirectControl(DataclassMixin):
    action: int = csfield(TEnum(Int8ub, ContentControlDirect))


@dataclass
class PercentControl(DataclassMixin):
    position: int = csfield(ExprValidator(Int8ub, obj_ >= 0 and obj_ <= 100))


class Direction(EnumBase):
    REVERSE = 0
    FORWARD = 1


class ButtonsMode(EnumBase):
    CONTINUOUS = 0
    INCHING = 1


class DeviceDiameter(EnumBase):
    DIAMETER_13MM = 13
    DIAMETER_18MM = 18
    DIAMETER_29MM = 29


@dataclass
class SettingsResponse(DataclassMixin):
    reserved: int = csfield(Hex(BitsInteger(3)))
    has_light_device: bool = csfield(Flag)
    bottom_limit_is_ok: bool = csfield(Flag)
    top_limit_is_ok: bool = csfield(Flag)
    buttons_mode: int = csfield(TEnum(BitsInteger(1), ButtonsMode))
    direction: Direction = csfield(TEnum(BitsInteger(1), Direction))
    device_speed: int = csfield(
        ExprValidator(BitsInteger(8), obj_ >= 20 and obj_ <= 50)
    )
    device_percent_position: int = csfield(BitsInteger(8))
    device_length: int = csfield(BitsInteger(16))
    device_diameter: DeviceDiameter = csfield(TEnum(BitsInteger(8), DeviceDiameter))
    device_type: DeviceType = csfield(TEnum(BitsInteger(4), DeviceType))
    reserved2: int = csfield(Hex(BitsInteger(4)))


@dataclass
class UpdateSettings(DataclassMixin):
    device_type: DeviceType = csfield(TEnum(BitsInteger(4), DeviceType))
    reserved1: int = csfield(Hex(BitsInteger(1)))
    buttons_mode: int = csfield(TEnum(BitsInteger(1), ButtonsMode))
    direction: Direction = csfield(TEnum(BitsInteger(1), Direction))
    reserved2: int = csfield(Hex(BitsInteger(1)))
    device_speed: int = csfield(
        ExprValidator(BitsInteger(8), obj_ >= 20 and obj_ <= 50)
    )
    reserved3: int = csfield(Hex(BitsInteger(8)))
    device_length: int = csfield(BitsInteger(16))
    device_diameter: DeviceDiameter = csfield(TEnum(BitsInteger(8), DeviceDiameter))


class TimerRepeat(FlagsEnumBase):
    SUNDAY = 0x01
    MONDAY = 0x02
    TUESDAY = 0x04
    WEDNESDAY = 0x08
    THURSDAY = 0x10
    FRIDAY = 0x20
    SATURDAY = 0x40


@dataclass
class Timer(DataclassMixin):
    enabled: bool = csfield(Flag)
    target_position: int = csfield(ExprValidator(Int8ub, obj_ >= 0 and obj_ <= 100))
    repeat: TimerRepeat = csfield(TFlagsEnum(Int8ub, TimerRepeat))
    # Hours are stored on the devices incremented by 1
    hours: int = csfield(
        ExprValidator(
            Transformed(
                Int8ub,
                lambda h: bytearray([ord(h) - 1]),
                1,
                lambda h: bytearray([ord(h) + 1]),
                1,
            ),
            obj_ >= 0 and obj_ <= 23,
        )
    )
    minutes: int = csfield(ExprValidator(Int8ub, obj_ >= 0 and obj_ <= 59))


@dataclass
class UpdateTimer(DataclassMixin):
    timer_id: int = csfield(Int8ub)
    action: UpdateTimerAction = csfield(TEnum(Int8ub, UpdateTimerAction))
    timer: Timer = csfield(DataclassStruct(Timer))


@dataclass
class FindTiming(DataclassMixin):
    timers: list[Timer] = csfield(
        Array(lambda this: int(this._.message_size / 5), DataclassStruct(Timer))
    )


@dataclass
class IlluminanceLevel(DataclassMixin):
    has_light_device: bool = csfield(Flag)
    level: int = csfield(Int8ub)


@dataclass
class ChangeName(DataclassMixin):
    new_name: str = csfield(PaddedString(this._.message_size, "utf8"))


@dataclass
class OperationResult(DataclassMixin):
    result: int = csfield(TEnum(Int8ub, ContentOperationResult))
    is_success: bool = csfield(
        Computed(lambda ctx: ctx.result == ContentOperationResult.SUCCESS)
    )


@dataclass
class Battery(DataclassMixin):
    unknown: int = csfield(Hex(Bytes(4)))  # looks like unused and always 0x00000000
    level: int = csfield(Int8ub)


@dataclass
class Password(DataclassMixin):
    pin: int = csfield(ExprValidator(Int16ub, obj_ >= 0 and obj_ <= 9999))


@dataclass
class FinishedMoving(DataclassMixin):
    reserved1: int = csfield(Hex(Bytes(1)))
    position: int = csfield(Int8ub)
    reserved2: int = csfield(Hex(Bytes(2)))


@dataclass
class LimitOrResetResult(DataclassMixin):
    result: int = csfield(TEnum(Int8ub, ContentLimitSet))


class SeasonLightLevel(EnumBase):
    LUX_20 = 1
    LUX_100 = 2
    LUX_200 = 3
    LUX_300 = 4
    LUX_500 = 5
    LUX_800 = 6
    LUX_1000 = 7
    LUX_2000 = 8
    LUX_5000 = 9


@dataclass
class Season(DataclassMixin):
    season_id: int = csfield(BitsInteger(8))
    reserved: int = csfield(Default(BitsInteger(7), 0))
    is_enabled: bool = csfield(Flag)
    light_switch_state: SeasonLightSwitchState = csfield(
        TEnum(BitsInteger(8), SeasonLightSwitchState)
    )
    light_value_to_open: SeasonLightLevel = csfield(
        TEnum(BitsInteger(4), SeasonLightLevel)
    )
    light_value_to_close: SeasonLightLevel = csfield(
        TEnum(BitsInteger(4), SeasonLightLevel)
    )
    start_hour: int = csfield(ExprValidator(BitsInteger(8), obj_ >= 0 and obj_ <= 23))
    start_minute: int = csfield(ExprValidator(BitsInteger(8), obj_ >= 0 and obj_ <= 59))
    end_hour: int = csfield(ExprValidator(BitsInteger(8), obj_ >= 0 and obj_ <= 23))
    end_minute: int = csfield(ExprValidator(BitsInteger(8), obj_ >= 0 and obj_ <= 59))


@dataclass
class Seasons(DataclassMixin):
    summer: Season = csfield(DataclassBitStruct(Season))
    winter: Season = csfield(DataclassBitStruct(Season))


@dataclass
class UpdateSeason(DataclassMixin):
    season: Season = csfield(DataclassBitStruct(Season))


@dataclass
class ResponsePayload(DataclassMixin):
    MESSAGE_TYPE_MAP = {
        ResponseMessageType.REQUEST_BATTERY_STATUS: DataclassStruct(Battery),
        ResponseMessageType.CHANGE_NAME: DataclassStruct(OperationResult),
        ResponseMessageType.PASSWORD_CHANGE: DataclassStruct(OperationResult),
        ResponseMessageType.PASSWORD: DataclassStruct(OperationResult),
        ResponseMessageType.CONTROL_DIRECT: DataclassStruct(OperationResult),
        ResponseMessageType.CONTROL_PERCENT: DataclassStruct(OperationResult),
        ResponseMessageType.SEND_TIME: DataclassStruct(OperationResult),
        ResponseMessageType.REQUEST_SETTINGS: DataclassBitStruct(SettingsResponse),
        ResponseMessageType.LIST_TIMERS: DataclassStruct(FindTiming),
        ResponseMessageType.UPDATE_TIMER: DataclassStruct(OperationResult),
        ResponseMessageType.REQUEST_ILLUMINANCE: DataclassStruct(IlluminanceLevel),
        ResponseMessageType.FINISHED_MOVING: DataclassStruct(FinishedMoving),
        ResponseMessageType.LIMIT_OR_RESET: DataclassStruct(LimitOrResetResult),
        ResponseMessageType.LIST_SEASONS: DataclassStruct(Seasons),
        ResponseMessageType.UPDATE_SEASON: DataclassStruct(OperationResult),
        ResponseMessageType.UPDATE_SETTINGS: DataclassStruct(OperationResult),
    }

    header: bytes = csfield(Hex(Const(b"\x9A")))
    message_type: ResponseMessageType = csfield(TEnum(Int8ub, ResponseMessageType))
    message_size: int = csfield(
        Rebuild(
            Int8ub,
            lambda ctx: len(
                DataclassStruct(ctx.message.__class__).build(ctx.message)
                if isinstance(ctx.message, DataclassMixin)
                else ctx.message
            ),
        )
    )
    message: Any = csfield(
        RawCopy(
            Switch(
                this.message_type,
                MESSAGE_TYPE_MAP,
                default=HexDump(Bytes(this.message_size)),
            )
        )
    )


@dataclass
class Response(DataclassMixin):
    payload: ResponsePayload = csfield(RawCopy(DataclassStruct(ResponsePayload)))
    footer: Any = csfield(
        Select(
            success=Hex(Const(b"\x31")),
            failure=Hex(Const(b"\xCE")),
            checksum=Hex(
                Checksum(
                    Int8ub,
                    xor_checksum,
                    this.payload.data,
                )
            ),
        )
    )


@dataclass
class RequestPayload(DataclassMixin):
    MESSAGE_TYPE_MAP = {
        RequestMessageType.PASSWORD: DataclassStruct(Password),
        RequestMessageType.PASSWORD_CHANGE: DataclassStruct(Password),
        RequestMessageType.CHANGE_NAME: DataclassStruct(ChangeName),
        RequestMessageType.CONTROL_DIRECT: DataclassStruct(DirectControl),
        RequestMessageType.SEND_TIME: DataclassStruct(SendTime),
        RequestMessageType.REQUEST_SETTINGS: DataclassStruct(AlwaysOne),
        RequestMessageType.REQUEST_BATTERY_STATUS: DataclassStruct(AlwaysOne),
        RequestMessageType.REQUEST_ILLUMINANCE: DataclassStruct(AlwaysOne),
        RequestMessageType.UPDATE_TIMER: DataclassStruct(UpdateTimer),
        RequestMessageType.CONTROL_PERCENT: DataclassStruct(PercentControl),
        RequestMessageType.LIMIT_OR_RESET: DataclassStruct(LimitOrReset),
        RequestMessageType.UPDATE_SEASON: DataclassStruct(UpdateSeason),
        RequestMessageType.UPDATE_SETTINGS: DataclassBitStruct(UpdateSettings),
    }

    header: bytes = csfield(Hex(Const(b"\x9A")))
    message_type: RequestMessageType = csfield(TEnum(Int8ub, RequestMessageType))
    message_size: int = csfield(
        Rebuild(
            Int8ub,
            lambda ctx: len(
                DataclassStruct(ctx.message.__class__).build(ctx.message)
                if isinstance(ctx.message, DataclassMixin)
                else ctx.message
            ),
        )
    )
    message: Any = csfield(
        RawCopy(
            Switch(
                this.message_type,
                MESSAGE_TYPE_MAP,
                default=HexDump(Bytes(this.message_size)),
            )
        )
    )


@dataclass
class Request(DataclassMixin):
    # Tag should be excluded from the checksum calculation
    tag: bytes = csfield(Hex(Const(b"\x00\xFF\x00\x00")))
    payload: RequestPayload = csfield(RawCopy(DataclassStruct(RequestPayload)))
    footer: int = csfield(
        Hex(
            Checksum(
                Int8ub,
                xor_checksum,
                this.payload.data,
            )
        ),
    )
