from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InvoiceItem")


@_attrs_define
class InvoiceItem:
    """
    Attributes:
        id (str):
        amount_paid (float):
        amount_due (float):
        currency (str):
        created (int):
        number (None | str | Unset):
        status (None | str | Unset):
        hosted_invoice_url (None | str | Unset):
        invoice_pdf (None | str | Unset):
    """

    id: str
    amount_paid: float
    amount_due: float
    currency: str
    created: int
    number: None | str | Unset = UNSET
    status: None | str | Unset = UNSET
    hosted_invoice_url: None | str | Unset = UNSET
    invoice_pdf: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        amount_paid = self.amount_paid

        amount_due = self.amount_due

        currency = self.currency

        created = self.created

        number: None | str | Unset
        if isinstance(self.number, Unset):
            number = UNSET
        else:
            number = self.number

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        else:
            status = self.status

        hosted_invoice_url: None | str | Unset
        if isinstance(self.hosted_invoice_url, Unset):
            hosted_invoice_url = UNSET
        else:
            hosted_invoice_url = self.hosted_invoice_url

        invoice_pdf: None | str | Unset
        if isinstance(self.invoice_pdf, Unset):
            invoice_pdf = UNSET
        else:
            invoice_pdf = self.invoice_pdf

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "amount_paid": amount_paid,
                "amount_due": amount_due,
                "currency": currency,
                "created": created,
            }
        )
        if number is not UNSET:
            field_dict["number"] = number
        if status is not UNSET:
            field_dict["status"] = status
        if hosted_invoice_url is not UNSET:
            field_dict["hosted_invoice_url"] = hosted_invoice_url
        if invoice_pdf is not UNSET:
            field_dict["invoice_pdf"] = invoice_pdf

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        amount_paid = d.pop("amount_paid")

        amount_due = d.pop("amount_due")

        currency = d.pop("currency")

        created = d.pop("created")

        def _parse_number(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        number = _parse_number(d.pop("number", UNSET))

        def _parse_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_hosted_invoice_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        hosted_invoice_url = _parse_hosted_invoice_url(d.pop("hosted_invoice_url", UNSET))

        def _parse_invoice_pdf(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        invoice_pdf = _parse_invoice_pdf(d.pop("invoice_pdf", UNSET))

        invoice_item = cls(
            id=id,
            amount_paid=amount_paid,
            amount_due=amount_due,
            currency=currency,
            created=created,
            number=number,
            status=status,
            hosted_invoice_url=hosted_invoice_url,
            invoice_pdf=invoice_pdf,
        )

        invoice_item.additional_properties = d
        return invoice_item

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
