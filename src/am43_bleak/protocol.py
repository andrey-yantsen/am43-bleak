from dataclasses import dataclass
from datetime import datetime, tzinfo
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
    Optional,
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


class MessageType(EnumBase):
    PASSWORD = 0x17
    REQUEST_BATTERY_STATUS = 0xA2
    REQUEST_SETTINGS = 0xA7
    UPDATE_DEVICE_TIME = 0x14

    CONTROL_DIRECT = 0x0A
    CONTROL_POSITION = 0x0D

    REQUEST_ILLUMINANCE = 0xAA
    UPDATE_SETTINGS = 0x11
    UPDATE_TIMER = 0x15
    UPDATE_SEASON = 0x16
    UPDATE_NAME = 0x35
    PASSWORD_CHANGE = 0x18

    UPDATE_LIMIT_OR_RESET = 0x22

    # Device notifications
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


class ContentLimitSetOrReset(EnumBase):
    LIMIT_INIT_SUCCESS = 0x5A
    LIMIT_UPDATE_SUCCESS = 0x5B
    RESET_SUCCESS = 0xC5
    TIMEOUT = 0xA5
    EXIT = 0x5C
    FAILURE = 0xB5


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


class DayOfWeek(EnumBase):
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 0


@dataclass
class UpdateDeviceTime(DataclassMixin):
    day_of_week: DayOfWeek = csfield(TEnum(Int8ub, DayOfWeek))
    hour: int = csfield(ExprValidator(Int8ub, obj_ >= 0 and obj_ <= 23))
    minute: int = csfield(ExprValidator(Int8ub, obj_ >= 0 and obj_ <= 59))
    second: int = csfield(ExprValidator(Int8ub, obj_ >= 0 and obj_ <= 59))

    def now(tz: tzinfo = None) -> "UpdateDeviceTime":
        now = datetime.now(tz)
        return UpdateDeviceTime(
            (now.weekday + 1) % 7, hour=now.hour, minute=now.minute, second=now.second
        )


@dataclass
class AlwaysOne(DataclassMixin):
    _body: int = csfield(Const(b"\x01"))


@dataclass
class DirectControl(DataclassMixin):
    action: int = csfield(TEnum(Int8ub, ContentControlDirect))


@dataclass
class PositionControl(DataclassMixin):
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
    _reserved1: int = csfield(Hex(BitsInteger(3)))
    has_light_device: bool = csfield(Flag)
    bottom_limit_is_ok: bool = csfield(Flag)
    top_limit_is_ok: bool = csfield(Flag)
    buttons_mode: int = csfield(TEnum(BitsInteger(1), ButtonsMode))
    direction: Direction = csfield(TEnum(BitsInteger(1), Direction))
    speed: int = csfield(ExprValidator(BitsInteger(8), obj_ >= 20 and obj_ <= 50))
    current_position: int = csfield(BitsInteger(8))
    length: int = csfield(BitsInteger(16))
    wheel_gear_diameter: DeviceDiameter = csfield(TEnum(BitsInteger(8), DeviceDiameter))
    device_type: DeviceType = csfield(TEnum(BitsInteger(4), DeviceType))
    _reserved2: int = csfield(Hex(BitsInteger(4)))


@dataclass
class UpdateSettings(DataclassMixin):
    device_type: DeviceType = csfield(TEnum(BitsInteger(4), DeviceType))
    _reserved1: int = csfield(Hex(BitsInteger(1)))
    buttons_mode: int = csfield(TEnum(BitsInteger(1), ButtonsMode))
    direction: Direction = csfield(TEnum(BitsInteger(1), Direction))
    _reserved2: int = csfield(Hex(BitsInteger(1)))
    speed: int = csfield(ExprValidator(BitsInteger(8), obj_ >= 20 and obj_ <= 50))
    _reserved3: int = csfield(Hex(BitsInteger(8)))
    length: int = csfield(BitsInteger(16))
    wheel_gear_diameter: DeviceDiameter = csfield(TEnum(BitsInteger(8), DeviceDiameter))


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
    # Max 4 timers per device
    timer_id: int = csfield(ExprValidator(Int8ub, 0 <= obj_ <= 3))
    action: UpdateTimerAction = csfield(TEnum(Int8ub, UpdateTimerAction))
    timer: Timer = csfield(DataclassStruct(Timer))


@dataclass
class ListTimersResponse(DataclassMixin):
    timers: list[Timer] = csfield(
        Array(lambda this: int(this._._message_size / 5), DataclassStruct(Timer))
    )


@dataclass
class IlluminanceLevel(DataclassMixin):
    has_light_device: bool = csfield(Flag)
    level: int = csfield(Int8ub)


@dataclass
class UpdateName(DataclassMixin):
    new_name: str = csfield(PaddedString(this._._message_size, "utf8"))


@dataclass
class OperationResult(DataclassMixin):
    _result: int = csfield(TEnum(Int8ub, ContentOperationResult))
    is_success: bool = csfield(
        Computed(lambda ctx: ctx._result == ContentOperationResult.SUCCESS)
    )


@dataclass
class BatteryStatusResponse(DataclassMixin):
    _reserved: int = csfield(Default(Hex(Bytes(4)), 0))
    level: int = csfield(Int8ub)


@dataclass
class Password(DataclassMixin):
    pin: int = csfield(ExprValidator(Int16ub, obj_ >= 0 and obj_ <= 9999))


@dataclass
class FinishedMoving(DataclassMixin):
    _reserved1: int = csfield(Default(Hex(Bytes(1)), 0))
    position: int = csfield(Int8ub)
    _reserved2: int = csfield(Default(Hex(Bytes(2)), 0))


@dataclass
class LimitOrResetResult(DataclassMixin):
    _result: int = csfield(TEnum(Int8ub, ContentLimitSetOrReset))
    is_success: bool = csfield(
        Computed(
            lambda ctx: ctx._result
            in (
                ContentLimitSetOrReset.LIMIT_INIT_SUCCESS,
                ContentLimitSetOrReset.LIMIT_UPDATE_SUCCESS,
                ContentLimitSetOrReset.RESET_SUCCESS,
                ContentLimitSetOrReset.EXIT,
            )
        )
    )


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
    _reserved1: int = csfield(Default(BitsInteger(7), 0))
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
class ListSeasonsResponse(DataclassMixin):
    summer: Season = csfield(DataclassBitStruct(Season))
    winter: Season = csfield(DataclassBitStruct(Season))


@dataclass
class UpdateSeason(DataclassMixin):
    season: Season = csfield(DataclassBitStruct(Season))


@dataclass
class Payload(DataclassMixin):
    REQUEST_MESSAGE_TYPE_MAP = {
        MessageType.PASSWORD: DataclassStruct(Password),
        MessageType.PASSWORD_CHANGE: DataclassStruct(Password),
        MessageType.UPDATE_NAME: DataclassStruct(UpdateName),
        MessageType.CONTROL_DIRECT: DataclassStruct(DirectControl),
        MessageType.UPDATE_DEVICE_TIME: DataclassStruct(UpdateDeviceTime),
        MessageType.REQUEST_SETTINGS: DataclassStruct(AlwaysOne),
        MessageType.REQUEST_BATTERY_STATUS: DataclassStruct(AlwaysOne),
        MessageType.REQUEST_ILLUMINANCE: DataclassStruct(AlwaysOne),
        MessageType.UPDATE_TIMER: DataclassStruct(UpdateTimer),
        MessageType.CONTROL_POSITION: DataclassStruct(PositionControl),
        MessageType.UPDATE_LIMIT_OR_RESET: DataclassStruct(LimitOrReset),
        MessageType.UPDATE_SEASON: DataclassStruct(UpdateSeason),
        MessageType.UPDATE_SETTINGS: DataclassBitStruct(UpdateSettings),
    }

    RESPONSE_MESSAGE_TYPE_MAP = {
        MessageType.REQUEST_BATTERY_STATUS: DataclassStruct(BatteryStatusResponse),
        MessageType.UPDATE_NAME: DataclassStruct(OperationResult),
        MessageType.PASSWORD_CHANGE: DataclassStruct(OperationResult),
        MessageType.PASSWORD: DataclassStruct(OperationResult),
        MessageType.CONTROL_DIRECT: DataclassStruct(OperationResult),
        MessageType.CONTROL_POSITION: DataclassStruct(OperationResult),
        MessageType.UPDATE_DEVICE_TIME: DataclassStruct(OperationResult),
        MessageType.REQUEST_SETTINGS: DataclassBitStruct(SettingsResponse),
        MessageType.LIST_TIMERS: DataclassStruct(ListTimersResponse),
        MessageType.UPDATE_TIMER: DataclassStruct(OperationResult),
        MessageType.REQUEST_ILLUMINANCE: DataclassStruct(IlluminanceLevel),
        MessageType.FINISHED_MOVING: DataclassStruct(FinishedMoving),
        MessageType.UPDATE_LIMIT_OR_RESET: DataclassStruct(LimitOrResetResult),
        MessageType.LIST_SEASONS: DataclassStruct(ListSeasonsResponse),
        MessageType.UPDATE_SEASON: DataclassStruct(OperationResult),
        MessageType.UPDATE_SETTINGS: DataclassStruct(OperationResult),
    }

    _header: bytes = csfield(Hex(Const(b"\x9A")))
    message_type: MessageType = csfield(TEnum(Int8ub, MessageType))
    _message_size: int = csfield(
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
        Switch(
            lambda ctx: ctx._.is_device_response,
            {
                True: Switch(
                    this.message_type,
                    RESPONSE_MESSAGE_TYPE_MAP,
                    HexDump(Bytes(this._message_size)),
                ),
                False: Switch(
                    this.message_type,
                    REQUEST_MESSAGE_TYPE_MAP,
                    HexDump(Bytes(this._message_size)),
                ),
            },
        )
    )


# Tag present only in client->device messages
CLIENT_MESSAGE_TAG = b"\x00\xFF\x00\x00"


def xor_checksum(data: bytearray) -> int:
    checksum = 0
    for byte in data:
        checksum = checksum ^ byte

    return checksum


@dataclass
class Message(DataclassMixin):
    _tag: bytes = csfield(
        Rebuild(
            Hex(Optional(Const(CLIENT_MESSAGE_TAG))),
            lambda ctx: b"" if ctx.is_device_response else CLIENT_MESSAGE_TAG,
        )
    )
    is_device_response: bool = csfield(
        Computed(lambda ctx: ctx._tag is None or ctx._tag == b"")
    )
    _payload: Payload = csfield(RawCopy(DataclassStruct(Payload)))
    payload: Payload = csfield(Computed(this._payload["value"]))
    _footer: int = csfield(
        Switch(
            lambda ctx: isinstance(ctx._payload["value"].message, OperationResult)
            or isinstance(ctx._payload["value"].message, LimitOrResetResult),
            {
                True: Switch(
                    lambda ctx: ctx._payload["value"].message.is_success,
                    {
                        True: Hex(Const(b"\x31")),
                        False: Hex(Const(b"\xCE")),
                    },
                ),
            },
            Checksum(
                Int8ub,
                xor_checksum,
                this._payload["data"],
            ),
        )
    )

    def prepare(
        message_type: MessageType = None,
        is_device_response: bool = False,
        payload: Payload = None,
        message: Any = None,
        **kwargs,
    ) -> "Message":
        if payload is None:
            if message_type is None:
                raise ValueError(
                    "You must provide either payload, or message_type and message/kwargs"
                )

            klass = (
                Payload.RESPONSE_MESSAGE_TYPE_MAP[message_type]
                if is_device_response
                else Payload.REQUEST_MESSAGE_TYPE_MAP[message_type]
            )

            if klass.dc_type is AlwaysOne and message is None:
                message = AlwaysOne()

            if message is not None:
                if not isinstance(message, klass.dc_type):
                    raise ValueError(
                        "Message must be an instance of " + klass.dc_type.__class__
                    )

                payload = Payload(message_type=message_type, message=message)
            else:
                payload = Payload(
                    message_type=message_type,
                    message=klass.dc_type(**kwargs),
                )
        elif message_type is not None or message is not None:
            raise ValueError(
                "When payload is provided, message_type and message must be omited"
            )

        msg = Message(_payload={"value": payload})
        msg.payload = payload
        msg.is_device_response = is_device_response
        return msg


message_format = DataclassStruct(Message)
