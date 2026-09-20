"""Explicit registry for bundled plugins; no dynamic downloads or imports."""

# standard imports
from dataclasses import dataclass, field

# 1st-party imports
from ryujinx_save_manager.core.models import DiscoveredSave
from ryujinx_save_manager.plugins.game_plugin import GamePlugin


@dataclass(slots=True)
class PluginRegistry:
    _plugins: dict[str, GamePlugin] = field(default_factory=dict)

    def register(self, plugin: GamePlugin) -> None:
        if plugin.plugin_id in self._plugins:
            raise ValueError(f"duplicate plugin ID: {plugin.plugin_id}")
        self._plugins[plugin.plugin_id] = plugin

    def matching(self, save: DiscoveredSave) -> tuple[GamePlugin, ...]:
        return tuple(plugin for plugin in self._plugins.values() if plugin.detects(save))
