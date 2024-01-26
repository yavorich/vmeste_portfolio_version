from enum import Enum


class EventStatus(str, Enum):
    PUBLISHED = "published"
    POPULAR = "popular"
    UPCOMING = "upcoming"
    PAST = "past"
    DRAFT = "draft"
