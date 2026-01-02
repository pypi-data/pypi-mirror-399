from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar, cast
from types import ModuleType
import inspect

import click
import pydantic

from tgzr.cli.utils import TGZRCliGroup

from ..session import Session
from ..settings.settings import SettingsModelType

from .exceptions import MissingRunNativeModule
from .app_info import ShellAppContext, ShellAppInfo, DefaultShellAppInfo

if TYPE_CHECKING:
    from ..session import Session


class ShellAppSettings(pydantic.BaseModel):
    pass


class NoSettings(ShellAppSettings):
    pass


SettingsType = TypeVar("SettingsType", bound=ShellAppSettings)


class _BaseShellApp[SettingsType]:

    def __init__(
        self,
        app_name: str,
        run_module: ModuleType | None,
        app_id: str | None = None,
        app_groups: set[str] = set(),
        default_app_info: DefaultShellAppInfo | None = None,
        default_settings: SettingsType | None = None,
    ):
        """
        Create an App which will be accessible in the tgzr CLI.

        `app_name`:
            The name of the app, used to name the CLI command.

        `app_id`:
            The unic id associated with the app.
            The default value is the name of the module defining the
            app. This should be unic enough.

        `run_module`:
            The python module used to run the app.
            Must be a valid modules with appropriate safeguards.
            NOTE: using None will raise an exception showing you
            how to implement this module.

        `app_groups`:
            A set of groups where this app should be found.
            Groups with double-underscopre (like "_EXE_") are managed by tgzr.

        `app_info`:
            Provides the default info about this app.
            See _BaseShellApp.get_info()
        """
        frame: inspect.FrameInfo = inspect.stack()[1]
        if app_name is None:
            app_name = frame.function
            # print("---> AUTO APP NAME:", repr(app_name))

        if app_id is None:
            # FIXME: the module used here is wrong!
            module = inspect.getmodule(frame[0])
            app_id = (
                (module and module.__name__ or "???").replace(".", "_") + "." + app_name
            )
            # print("---> AUTO APP ID:", app_id)

        if run_module is None:
            raise MissingRunNativeModule(self)
        self.run_native_module = run_module

        self.app_name = app_name
        self.app_id = app_id
        self.app_groups = app_groups
        self._default_app_info = default_app_info or DefaultShellAppInfo()

        self._default_settings = default_settings or NoSettings()
        # FIXME: find a way to do this:
        # if not isinstance(self._default_settings, SettingsType):
        #     raise ValueError(
        #         f"The default settings must be an instance of {SettingsType}, not {type(default_settings)}"
        #     )

    def create_app_context(
        self,
        session: Session,
        host_suffix: str = "",
        context_name: str = "root",
    ):
        if host_suffix and not host_suffix.startswith("."):
            host_suffix = "." + host_suffix
        return ShellAppContext(
            session=session,
            host_name=f"tgzr.shell_apps.{self.app_id}{host_suffix}",
            context_name=context_name,
        )

    def installed_versions(self, session: Session) -> set[str]:
        """
        Return the list of installed versions.
        Default is to return an empty set, which means this app
        does not support multiple versions
        """
        return set()

    def cli_run_cmd_installed(
        self, created_cmd: click.Command, root_group: TGZRCliGroup
    ):
        """
        Called when tgzr.shell.cli_plugin.app_cli has created and
        registered a cli command to execute this app.

        Subclasses can override this to alter the cmd or set it as default
        on the root group.

        Default does nothing.
        """
        pass

    def get_info(self, context: ShellAppContext) -> ShellAppInfo:
        """
        Subclasses can reimplement this to provide
        information used by GUIs to display (or hide) this app
        in the given context.

        The default behavior is to return a copy of the `app_info`
        provided in the constructor, and hide the app if
        context.context_name is not part of the app.app_groups set.
        """
        # print("???", self.app_name, self.app_groups, context.context_name)
        app_info = ShellAppInfo(
            app=self,
            title=self._default_app_info.title or self.app_name.title(),
            icon=self._default_app_info.icon,
            color=self._default_app_info.color,
            hidden=context.context_name not in self.app_groups,
            installed_versions=self.installed_versions(context.session),
        )
        return app_info

    @property
    def settings_key(self) -> str:
        return f"shell_apps.{self.app_id}"

    def get_settings(
        self, context: ShellAppContext, settings_context: list[str] | None = None
    ) -> SettingsType:
        # TODO: get the default settings_context form context?
        settings_context = settings_context or []

        model_type = type(self._default_settings)
        settings = context.session.settings.get_context(
            settings_context, model_type, self.settings_key
        )
        return settings

    def store_settings(
        self,
        settings: SettingsType,
        context: ShellAppContext,
        context_name: str | None = None,
        exclude_defaults: bool = True,
    ) -> None:
        # TODO: get the default context_name form context?
        if not isinstance(settings, pydantic.BaseModel):
            raise Exception()
        context_name = context_name or "user"
        context.session.settings.update(
            context_name, settings, self.settings_key, exclude_defaults=exclude_defaults
        )

    def run_app(self, session: Session):
        raise NotImplementedError()
