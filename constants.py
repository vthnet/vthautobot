from enum import StrEnum


class Status(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


class Service(StrEnum):
    VIEWS = "views"
    REACTIONS = "reactions"
    BOTH = "both"


class Event(StrEnum):
    START = "start"
    ORDER = "order"
    CHANNEL_ADD = "channel_add"
    CHANNEL_REMOVE = "channel_remove"
    CREDIT = "credit"
    REFERRAL = "referral"
    ERROR = "error"