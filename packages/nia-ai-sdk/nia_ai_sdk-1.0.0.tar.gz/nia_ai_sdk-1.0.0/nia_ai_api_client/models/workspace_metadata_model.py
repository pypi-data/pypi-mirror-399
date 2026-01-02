from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkspaceMetadataModel")


@_attrs_define
class WorkspaceMetadataModel:
    """Workspace detection metadata for context organization.

    Attributes:
        cwd (str): Current working directory when context was created
        git_root (None | str | Unset): Git repository root path
        git_remote (None | str | Unset): Git remote URL
        branch (None | str | Unset): Git branch name
        commit_hash (None | str | Unset): Git commit hash (short)
        project_name (None | str | Unset): Detected or custom project name
        project_type (None | str | Unset): Detected tech stack (e.g., 'python+fastapi')
        relative_path (None | str | Unset): Path relative to git root
        package_manager (None | str | Unset): Detected package manager
    """

    cwd: str
    git_root: None | str | Unset = UNSET
    git_remote: None | str | Unset = UNSET
    branch: None | str | Unset = UNSET
    commit_hash: None | str | Unset = UNSET
    project_name: None | str | Unset = UNSET
    project_type: None | str | Unset = UNSET
    relative_path: None | str | Unset = UNSET
    package_manager: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cwd = self.cwd

        git_root: None | str | Unset
        if isinstance(self.git_root, Unset):
            git_root = UNSET
        else:
            git_root = self.git_root

        git_remote: None | str | Unset
        if isinstance(self.git_remote, Unset):
            git_remote = UNSET
        else:
            git_remote = self.git_remote

        branch: None | str | Unset
        if isinstance(self.branch, Unset):
            branch = UNSET
        else:
            branch = self.branch

        commit_hash: None | str | Unset
        if isinstance(self.commit_hash, Unset):
            commit_hash = UNSET
        else:
            commit_hash = self.commit_hash

        project_name: None | str | Unset
        if isinstance(self.project_name, Unset):
            project_name = UNSET
        else:
            project_name = self.project_name

        project_type: None | str | Unset
        if isinstance(self.project_type, Unset):
            project_type = UNSET
        else:
            project_type = self.project_type

        relative_path: None | str | Unset
        if isinstance(self.relative_path, Unset):
            relative_path = UNSET
        else:
            relative_path = self.relative_path

        package_manager: None | str | Unset
        if isinstance(self.package_manager, Unset):
            package_manager = UNSET
        else:
            package_manager = self.package_manager

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "cwd": cwd,
            }
        )
        if git_root is not UNSET:
            field_dict["git_root"] = git_root
        if git_remote is not UNSET:
            field_dict["git_remote"] = git_remote
        if branch is not UNSET:
            field_dict["branch"] = branch
        if commit_hash is not UNSET:
            field_dict["commit_hash"] = commit_hash
        if project_name is not UNSET:
            field_dict["project_name"] = project_name
        if project_type is not UNSET:
            field_dict["project_type"] = project_type
        if relative_path is not UNSET:
            field_dict["relative_path"] = relative_path
        if package_manager is not UNSET:
            field_dict["package_manager"] = package_manager

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cwd = d.pop("cwd")

        def _parse_git_root(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        git_root = _parse_git_root(d.pop("git_root", UNSET))

        def _parse_git_remote(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        git_remote = _parse_git_remote(d.pop("git_remote", UNSET))

        def _parse_branch(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        branch = _parse_branch(d.pop("branch", UNSET))

        def _parse_commit_hash(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        commit_hash = _parse_commit_hash(d.pop("commit_hash", UNSET))

        def _parse_project_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        project_name = _parse_project_name(d.pop("project_name", UNSET))

        def _parse_project_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        project_type = _parse_project_type(d.pop("project_type", UNSET))

        def _parse_relative_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        relative_path = _parse_relative_path(d.pop("relative_path", UNSET))

        def _parse_package_manager(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        package_manager = _parse_package_manager(d.pop("package_manager", UNSET))

        workspace_metadata_model = cls(
            cwd=cwd,
            git_root=git_root,
            git_remote=git_remote,
            branch=branch,
            commit_hash=commit_hash,
            project_name=project_name,
            project_type=project_type,
            relative_path=relative_path,
            package_manager=package_manager,
        )

        workspace_metadata_model.additional_properties = d
        return workspace_metadata_model

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
