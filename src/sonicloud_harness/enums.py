from enum import Enum


class SourceType(str, Enum):
    APP_STORE = "app_store"
    REVIEW = "review"
    TREND = "trend"
    COMMUNITY = "community"
    FREELANCE = "freelance"
    KEYWORD = "keyword"
    OPEN_SOURCE = "open_source"
    MANUAL = "manual"


class AccessMethod(str, Enum):
    API = "api"
    EXPORT = "export"
    CRAWLER = "crawler"
    MANUAL_UPLOAD = "manual_upload"
    PUBLIC_PAGE = "public_page"


class LegalStatus(str, Enum):
    ALLOWED = "allowed"
    RESTRICTED = "restricted"
    MANUAL_ONLY = "manual_only"
    EXCLUDED = "excluded"
    UNKNOWN = "unknown"


class Language(str, Enum):
    EN = "en"
    KO = "ko"
    OTHER = "other"


class MarketPriority(str, Enum):
    GLOBAL_FIRST = "global_first"
    KOREA_LOCALIZED = "korea_localized"
    KOREA_FIRST = "korea_first"


class MonetizationModel(str, Enum):
    ADS = "ads"
    SUBSCRIPTION = "subscription"
    PAID_APP = "paid_app"
    B2B = "b2b"
    TEMPLATE = "template"
    UNKNOWN = "unknown"


class Confidence(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Decision(str, Enum):
    PURSUE = "pursue"
    WATCH = "watch"
    REJECT = "reject"
    HOLD = "hold"
