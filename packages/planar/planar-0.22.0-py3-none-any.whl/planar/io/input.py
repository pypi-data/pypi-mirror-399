"""Input helpers for the Planar IO facade."""

from datetime import date

from ._base import _ensure_context
from ._field_specs import (
    _boolean_field_spec,
    _date_field_spec,
    _execute_single_field,
    _text_field_spec,
)


class IOInput:
    async def text(
        self,
        label: str,
        *,
        default: str | None = None,
        help_text: str | None = None,
        placeholder: str | None = None,
        multiline: bool = False,
    ) -> str:
        _ensure_context()
        spec = _text_field_spec(
            label=label,
            default=default,
            help_text=help_text,
            placeholder=placeholder,
            multiline=multiline,
        )
        return await _execute_single_field(
            spec,
            kind="input.text",
            model_suffix="Text",
            label=label,
            help_text=help_text,
        )

    async def boolean(
        self,
        label: str,
        *,
        default: bool = False,
        help_text: str | None = None,
    ) -> bool:
        _ensure_context()
        spec = _boolean_field_spec(
            label=label,
            default=default,
            help_text=help_text,
        )
        return await _execute_single_field(
            spec,
            kind="input.boolean",
            model_suffix="Boolean",
            label=label,
            help_text=help_text,
        )

    async def date(
        self,
        label: str,
        *,
        default: date | None = None,
        help_text: str | None = None,
        min_date: date | None = None,
        max_date: date | None = None,
    ) -> date:
        _ensure_context()
        spec = _date_field_spec(
            label=label,
            default=default,
            help_text=help_text,
            min_date=min_date,
            max_date=max_date,
        )
        return await _execute_single_field(
            spec,
            kind="input.date",
            model_suffix="Date",
            label=label,
            help_text=help_text,
        )


__all__ = ["IOInput"]
