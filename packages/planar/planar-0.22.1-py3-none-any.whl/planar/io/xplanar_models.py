"""Structured models for validating `x-planar` metadata."""

from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SelectOption(BaseModel):
    label: str
    value: str


class BaseProps(BaseModel):
    model_config = ConfigDict(extra="forbid")


class InputTextProps(BaseProps):
    label: str
    multiline: bool
    placeholder: str | None = None
    help_text: str | None = None
    default: str | None = None


class InputDateProps(BaseProps):
    label: str
    default: date | None = None
    help_text: str | None = None
    min_date: date | None = None
    max_date: date | None = None


class InputBooleanProps(BaseProps):
    label: str
    default: bool
    help_text: str | None = None


class SelectSingleProps(BaseProps):
    label: str
    options: list[SelectOption]
    search: bool
    help_text: str | None = None
    default: str | None = None

    @field_validator("options")
    @classmethod
    def _ensure_options_non_empty(cls, value: list[SelectOption]) -> list[SelectOption]:
        if not value:
            raise ValueError("options must contain at least one item")
        return value


class SelectMultipleProps(BaseProps):
    label: str
    options: list[SelectOption]
    search: bool
    help_text: str | None = None
    default: list[str] | None = None
    maxSelections: int | None = None

    model_config = ConfigDict(extra="forbid")

    @field_validator("options")
    @classmethod
    def _ensure_options_non_empty(cls, value: list[SelectOption]) -> list[SelectOption]:
        if not value:
            raise ValueError("options must contain at least one item")
        return value

    @field_validator("maxSelections")
    @classmethod
    def _validate_max_selections(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("maxSelections must be positive")
        return value


class EntitySelectProps(BaseProps):
    label: str
    entity: str
    multiple: bool
    displayField: str | None = None
    help_text: str | None = None
    default: str | list[str] | None = None

    @field_validator("default")
    @classmethod
    def _validate_default(cls, value: str | list[str] | None) -> str | list[str] | None:
        if isinstance(value, list):
            if len({*value}) != len(value):
                raise ValueError("default selections must be unique")
        return value


class UploadFileProps(BaseProps):
    label: str
    accept: list[str] | None = None
    maxSizeMb: int | None = Field(default=None)
    help_text: str | None = None

    @field_validator("maxSizeMb")
    @classmethod
    def _validate_size(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("maxSizeMb must be positive")
        return value


class FormProps(BaseProps):
    submitLabel: str


class XPlanarBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class InputTextXPlanar(XPlanarBase):
    component: Literal["io.input.text"]
    props: InputTextProps


class InputBooleanXPlanar(XPlanarBase):
    component: Literal["io.input.boolean"]
    props: InputBooleanProps


class InputDateXPlanar(XPlanarBase):
    component: Literal["io.input.date"]
    props: InputDateProps


class SelectSingleXPlanar(XPlanarBase):
    component: Literal["io.select.single"]
    props: SelectSingleProps


class SelectMultipleXPlanar(XPlanarBase):
    component: Literal["io.select.multiple"]
    props: SelectMultipleProps


class EntitySelectXPlanar(XPlanarBase):
    component: Literal["io.entity.select"]
    props: EntitySelectProps


class UploadFileXPlanar(XPlanarBase):
    component: Literal["io.upload.file"]
    props: UploadFileProps


class FormXPlanar(XPlanarBase):
    component: Literal["io.form"]
    props: FormProps


XPlanar = Annotated[
    InputTextXPlanar
    | InputBooleanXPlanar
    | InputDateXPlanar
    | SelectSingleXPlanar
    | SelectMultipleXPlanar
    | EntitySelectXPlanar
    | UploadFileXPlanar
    | FormXPlanar,
    Field(discriminator="component"),
]


__all__ = [
    "BaseProps",
    "XPlanar",
    "InputTextProps",
    "InputTextXPlanar",
    "InputBooleanProps",
    "InputBooleanXPlanar",
    "InputDateProps",
    "InputDateXPlanar",
    "SelectSingleProps",
    "SelectSingleXPlanar",
    "SelectMultipleProps",
    "SelectMultipleXPlanar",
    "EntitySelectProps",
    "EntitySelectXPlanar",
    "UploadFileProps",
    "UploadFileXPlanar",
    "FormProps",
    "FormXPlanar",
]
