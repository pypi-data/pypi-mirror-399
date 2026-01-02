from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BodyChatWithProjectProjectsProjectIdChatPost")


@_attrs_define
class BodyChatWithProjectProjectsProjectIdChatPost:
    """
    Attributes:
        user_id (str):
        prompt (str):
        chat_id (str):
        messages (str):
        max_tokens (int | Unset):  Default: 64000.
        temperature (float | Unset):  Default: 0.2.
        stream (bool | Unset):  Default: True.
        additional_project_ids (str | Unset):  Default: '[]'.
        include_external_sources (bool | Unset):  Default: True.
        include_sources (bool | Unset):  Default: True.
        fast_mode (bool | Unset):  Default: True.
    """

    user_id: str
    prompt: str
    chat_id: str
    messages: str
    max_tokens: int | Unset = 64000
    temperature: float | Unset = 0.2
    stream: bool | Unset = True
    additional_project_ids: str | Unset = "[]"
    include_external_sources: bool | Unset = True
    include_sources: bool | Unset = True
    fast_mode: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        prompt = self.prompt

        chat_id = self.chat_id

        messages = self.messages

        max_tokens = self.max_tokens

        temperature = self.temperature

        stream = self.stream

        additional_project_ids = self.additional_project_ids

        include_external_sources = self.include_external_sources

        include_sources = self.include_sources

        fast_mode = self.fast_mode

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "prompt": prompt,
                "chat_id": chat_id,
                "messages": messages,
            }
        )
        if max_tokens is not UNSET:
            field_dict["max_tokens"] = max_tokens
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if stream is not UNSET:
            field_dict["stream"] = stream
        if additional_project_ids is not UNSET:
            field_dict["additional_project_ids"] = additional_project_ids
        if include_external_sources is not UNSET:
            field_dict["include_external_sources"] = include_external_sources
        if include_sources is not UNSET:
            field_dict["include_sources"] = include_sources
        if fast_mode is not UNSET:
            field_dict["fast_mode"] = fast_mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        prompt = d.pop("prompt")

        chat_id = d.pop("chat_id")

        messages = d.pop("messages")

        max_tokens = d.pop("max_tokens", UNSET)

        temperature = d.pop("temperature", UNSET)

        stream = d.pop("stream", UNSET)

        additional_project_ids = d.pop("additional_project_ids", UNSET)

        include_external_sources = d.pop("include_external_sources", UNSET)

        include_sources = d.pop("include_sources", UNSET)

        fast_mode = d.pop("fast_mode", UNSET)

        body_chat_with_project_projects_project_id_chat_post = cls(
            user_id=user_id,
            prompt=prompt,
            chat_id=chat_id,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
            additional_project_ids=additional_project_ids,
            include_external_sources=include_external_sources,
            include_sources=include_sources,
            fast_mode=fast_mode,
        )

        body_chat_with_project_projects_project_id_chat_post.additional_properties = d
        return body_chat_with_project_projects_project_id_chat_post

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
