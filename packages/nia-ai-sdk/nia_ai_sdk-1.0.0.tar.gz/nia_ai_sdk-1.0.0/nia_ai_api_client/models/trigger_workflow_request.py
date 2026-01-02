from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.trigger_workflow_request_input import TriggerWorkflowRequestInput


T = TypeVar("T", bound="TriggerWorkflowRequest")


@_attrs_define
class TriggerWorkflowRequest:
    """Request model for triggering a workflow.

    Attributes:
        workflow_name (str):
        input_ (TriggerWorkflowRequestInput):
    """

    workflow_name: str
    input_: TriggerWorkflowRequestInput
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        workflow_name = self.workflow_name

        input_ = self.input_.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "workflow_name": workflow_name,
                "input": input_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.trigger_workflow_request_input import TriggerWorkflowRequestInput

        d = dict(src_dict)
        workflow_name = d.pop("workflow_name")

        input_ = TriggerWorkflowRequestInput.from_dict(d.pop("input"))

        trigger_workflow_request = cls(
            workflow_name=workflow_name,
            input_=input_,
        )

        trigger_workflow_request.additional_properties = d
        return trigger_workflow_request

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
