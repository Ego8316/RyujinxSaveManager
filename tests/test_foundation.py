# standard imports
from pathlib import Path

# 1st-party imports
from ryujinx_save_manager.core.models import DiscoveredSave
from ryujinx_save_manager.diff.binary_diff import ByteChange, compare_bytes
from ryujinx_save_manager.plugins.plugin_registry import PluginRegistry

# 3rd-party imports
import pytest


def test_binary_diff_reports_offsets_and_length_changes() -> None:
    assert compare_bytes(b"\x00\x01", b"\x00\xc3\xff") == (
        ByteChange(1, 1, 0xC3),
        ByteChange(2, None, 0xFF),
    )
    assert compare_bytes(b"\x01", b"") == (ByteChange(0, 1, None),)
    assert compare_bytes(b"same", b"same") == ()


class ExamplePlugin:
    plugin_id = "example"
    display_name = "Example"
    title_ids = frozenset({"TEST"})

    def detects(self, save: DiscoveredSave) -> bool:
        return save.title_id in self.title_ids

    def relevant_files(self, _save: DiscoveredSave) -> tuple[Path, ...]:
        return (Path("save.bin"),)


def test_registry_matches_and_rejects_duplicates(tmp_path: Path) -> None:
    registry = PluginRegistry()
    plugin = ExamplePlugin()
    registry.register(plugin)
    save = DiscoveredSave("test", tmp_path, title_id="TEST")
    assert registry.matching(save) == (plugin,)
    with pytest.raises(ValueError, match="duplicate"):
        registry.register(plugin)
