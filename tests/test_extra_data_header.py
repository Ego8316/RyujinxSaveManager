"""Synthetic tests for bounded, read-only ExtraData inspection."""

# standard imports
from pathlib import Path

# 1st-party imports
from ryujinx_save_manager.core.discovery_diagnostic_code import DiscoveryDiagnosticCode
from ryujinx_save_manager.core.models import SaveType
from ryujinx_save_manager.storage.extra_data_header import ExtraDataHeader
from ryujinx_save_manager.storage.ryujinx_storage_provider import RyujinxStorageProvider
from ryujinx_save_manager.storage.save_data_type import SaveDataType

# 3rd-party imports
import pytest

NSMBUD_ID = 0x0100EA80032EA000
ACNH_ID = 0x01006F8002326000


def _metadata(application_id: int = NSMBUD_ID, save_type: int = 1) -> bytes:
    data = bytearray(0x200)
    data[0:8] = application_id.to_bytes(8, "little")
    data[8:24] = bytes(range(16))
    data[0x20] = save_type
    return bytes(data)


def _container(root: Path, name: str, data: bytes, second: bytes | None = None) -> Path:
    container = root / name
    (container / "0").mkdir(parents=True)
    (container / "ExtraData0").write_bytes(data)
    (container / "ExtraData1").write_bytes(second if second is not None else data)
    return container


@pytest.mark.parametrize(
    ("application_id", "save_type"),
    [
        (NSMBUD_ID, SaveDataType.ACCOUNT),
        (ACNH_ID, SaveDataType.DEVICE),
        (ACNH_ID, SaveDataType.BCAT),
    ],
)
def test_header_decodes_observed_types_and_explicit_little_endian(
    application_id: int, save_type: SaveDataType
) -> None:
    header = ExtraDataHeader.from_bytes(_metadata(application_id, save_type))
    assert header.application_id == application_id
    assert header.application_id_hex == f"{application_id:016X}"
    assert header.save_data_type is save_type
    assert header.account_uid_bytes == bytes(range(16))
    assert header.system_save_data_id_bytes == bytes(8)


@pytest.mark.parametrize("size", [0, 0x1FF, 0x201])
def test_header_rejects_other_sizes(size: int) -> None:
    with pytest.raises(ValueError, match="Expected 512 metadata bytes"):
        ExtraDataHeader.from_bytes(bytes(size))


@pytest.mark.parametrize(
    "save_type", [SaveDataType.ACCOUNT, SaveDataType.DEVICE, SaveDataType.BCAT]
)
def test_scanner_exposes_application_id_independently_of_type(
    tmp_path: Path, save_type: SaveDataType
) -> None:
    app_id = NSMBUD_ID if save_type is SaveDataType.ACCOUNT else ACNH_ID
    container = _container(tmp_path, "0000000000000001", _metadata(app_id, save_type))

    report = RyujinxStorageProvider().discover(tmp_path)

    assert report.diagnostics == ()
    assert report.saves[0].container_path == container
    assert report.saves[0].save_data_id == "0000000000000001"
    assert report.saves[0].title_id == f"{app_id:016X}"
    assert report.saves[0].save_data_type == SaveType(int(save_type), save_type.label)
    assert report.saves[0].user_id is None


def test_scanner_reports_conflicting_copies_without_assigning_identity(tmp_path: Path) -> None:
    _container(tmp_path, "0000000000000001", _metadata(), _metadata(ACNH_ID))

    report = RyujinxStorageProvider().discover(tmp_path)

    assert report.saves[0].title_id is None
    assert report.saves[0].save_data_type is None
    assert [item.code for item in report.diagnostics] == [
        DiscoveryDiagnosticCode.CONFLICTING_METADATA
    ]


def test_scanner_compares_type_and_account_uid_too(tmp_path: Path) -> None:
    first = _metadata()
    second = bytearray(first)
    second[0x20] = SaveDataType.DEVICE
    _container(tmp_path, "0000000000000001", first, bytes(second))

    report = RyujinxStorageProvider().discover(tmp_path)
    assert report.diagnostics[0].code is DiscoveryDiagnosticCode.CONFLICTING_METADATA

    second[0x20] = SaveDataType.ACCOUNT
    second[0x08] ^= 1
    (tmp_path / "0000000000000001" / "ExtraData1").write_bytes(second)
    report = RyujinxStorageProvider().discover(tmp_path)
    assert report.diagnostics[0].code is DiscoveryDiagnosticCode.CONFLICTING_METADATA


def test_scanner_ignores_nonidentity_metadata_differences(tmp_path: Path) -> None:
    data = bytearray(_metadata())
    second = bytearray(data)
    second[0x68] = 0x55
    _container(tmp_path, "0000000000000001", bytes(data), bytes(second))

    report = RyujinxStorageProvider().discover(tmp_path)

    assert report.diagnostics == ()
    assert report.saves[0].title_id == "0100EA80032EA000"


def test_scanner_reports_malformed_copy_and_keeps_container(tmp_path: Path) -> None:
    _container(tmp_path, "0000000000000001", _metadata(), bytes(0x1FF))

    report = RyujinxStorageProvider().discover(tmp_path)

    assert len(report.saves) == 1
    assert report.saves[0].title_id is None
    assert [item.code for item in report.diagnostics] == [
        DiscoveryDiagnosticCode.INVALID_METADATA_SIZE
    ]


def test_single_copy_is_not_enough_to_assign_identity(tmp_path: Path) -> None:
    container = tmp_path / "0000000000000001"
    container.mkdir()
    (container / "ExtraData0").write_bytes(_metadata())

    report = RyujinxStorageProvider().discover(tmp_path)

    assert report.saves[0].title_id is None
    assert report.saves[0].save_data_type is None


def test_unknown_save_type_remains_raw_numeric_value(tmp_path: Path) -> None:
    data = _metadata(ACNH_ID, 255)
    header = ExtraDataHeader.from_bytes(data)
    assert header.save_data_type == 255
    assert not isinstance(header.save_data_type, SaveDataType)
    _container(tmp_path, "0000000000000001", data)

    report = RyujinxStorageProvider().discover(tmp_path)

    assert report.saves[0].title_id == "01006F8002326000"
    assert report.saves[0].save_data_type == SaveType(255, "Unknown (255)")


def test_zero_application_id_is_not_identification(tmp_path: Path) -> None:
    _container(tmp_path, "0000000000000001", _metadata(0, SaveDataType.DEVICE))

    report = RyujinxStorageProvider().discover(tmp_path)

    assert report.saves[0].title_id is None
    assert report.saves[0].save_data_type == SaveType(3, "Device")


def test_save_data_id_and_application_id_remain_distinct(tmp_path: Path) -> None:
    _container(tmp_path, "00000000000000AF", _metadata(ACNH_ID, SaveDataType.BCAT))

    save = RyujinxStorageProvider().discover(tmp_path).saves[0]

    assert save.save_data_id == "00000000000000AF"
    assert save.title_id == "01006F8002326000"
    assert save.save_data_id != save.title_id
