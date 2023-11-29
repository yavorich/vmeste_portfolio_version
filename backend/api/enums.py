from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)


class EventStatus(str, Enum):
    PUBLISHED = "published"
    POPULAR = "popular"
    UPCOMING = "upcoming"
    PAST = "past"
    DRAFT = "draft"
