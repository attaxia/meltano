import os
import json
import yaml
import logging
from typing import List

from .project import Project
from .plugin import PluginType, PluginInstall, PluginRef
from .plugin_discovery_service import PluginDiscoveryService
from .plugin.factory import plugin_factory
from .config_service import ConfigService, PluginAlreadyAddedException


class PluginNotSupportedException(Exception):
    pass


class MissingPluginException(Exception):
    pass


class ProjectAddService:
    def __init__(
        self,
        project: Project,
        plugin_discovery_service: PluginDiscoveryService = None,
        config_service: ConfigService = None,
    ):
        self.project = project
        self.discovery_service = plugin_discovery_service or PluginDiscoveryService(
            project
        )
        self.config_service = config_service or ConfigService(project)

    def add(self, plugin_type: PluginType, plugin_name: str, **kwargs) -> PluginInstall:
        plugin = self.discovery_service.find_plugin(plugin_type, plugin_name)
        installed = plugin.as_installed()
        return self.config_service.add_to_file(installed)

    def add_related(
        self,
        target_plugin: PluginInstall,
        plugin_types: List[PluginType] = list(PluginType),
    ):
        try:
            plugin_types.remove(target_plugin.type)
        except ValueError:
            pass

        related_plugins = [
            plugin
            for plugin in self.discovery_service.plugins()
            if plugin.namespace == target_plugin.namespace
            and plugin.type in plugin_types
        ]

        added_plugins = []
        for plugin in related_plugins:
            try:
                plugin_install = self.add(plugin.type, plugin.name)

                added_plugins.append(plugin_install)
            except PluginAlreadyAddedException:
                pass

        return added_plugins
