from agilix_api_fr8train.models.courses import (
    CopyCourseDefinition,
    UpdateCourseDefinition,
)


def build_update_course_payload(update_courses: list[UpdateCourseDefinition]) -> dict:
    return {"requests": {"course": list(map(lambda x: dict(x), update_courses))}}


def build_copy_course_payload(copy_courses: list[CopyCourseDefinition]) -> dict:
    return {"requests": {"course": list(map(lambda x: dict(x), copy_courses))}}
