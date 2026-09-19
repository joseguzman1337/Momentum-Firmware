"""Regression checks for the Flipper Lab MFKey32 SD-card exchange contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FLIPPER = ROOT / "furi/flipper.c"
MFKEY_PLUGIN = ROOT / "applications/external/mfkey/init_plugin.c"


def test_nfc_lab_exchange_file_is_created_without_overwriting_captures():
    source = FLIPPER.read_text(encoding="utf-8")

    assert 'EXT_PATH("nfc/.mfkey32.log")' in source
    assert "storage_common_stat(storage, NFC_LAB_MFKEY32_LOG_PATH, &info)" in source
    assert "FSOM_CREATE_NEW" in source
    assert "file_info_is_dir(&info)" in source

    helper = source.split("static void flipper_prepare_nfc_lab_storage", 1)[1].split(
        "void flipper_migrate_files", 1
    )[0]
    assert "FSOM_CREATE_ALWAYS" not in helper
    assert "storage_common_remove" not in helper


def test_empty_exchange_file_is_not_reported_as_captured_nonces():
    source = MFKEY_PLUGIN.read_text(encoding="utf-8")
    presence = source.split(
        "bool napi_mf_classic_mfkey32_nonces_check_presence()", 1
    )[1].split("bool napi_mf_classic_nested_nonces_check_presence()", 1)[0]

    assert "stream_read_line" in presence
    assert "mfkey32_parse_line" in presence

    parser = source.split("static bool mfkey32_parse_line", 1)[1].split(
        "bool napi_mf_classic_mfkey32_nonces_check_presence", 1
    )[0]
    assert 'parsed != 9' in parser
    assert "sector > 39" in parser
    assert "key_type != 'A'" in parser


def test_nonce_array_counters_start_at_zero_for_empty_logs():
    source = MFKEY_PLUGIN.read_text(encoding="utf-8")

    assert "calloc(1, sizeof(MfClassicNonceArray))" in source
    assert "calloc(1, sizeof(MfClassicNonce))" in source
    assert "free(nonce_array->remaining_nonce_array)" in source


def test_nonce_array_payload_is_released_after_successful_attack():
    source = (ROOT / "applications/external/mfkey/mfkey.c").read_text(encoding="utf-8")

    cleanup = source.split("dolphin_deed(DolphinDeedNfcKeyAdd);", 1)[1].split(
        "keys_dict_free(user_dict);", 1
    )[0]
    assert "free(nonce_arr->remaining_nonce_array);" in cleanup
    assert cleanup.index("free(nonce_arr->remaining_nonce_array);") < cleanup.index(
        "free(nonce_arr);"
    )


def test_nonce_array_growth_preserves_original_allocation_on_failure():
    source = MFKEY_PLUGIN.read_text(encoding="utf-8")
    helper = source.split("static bool mfkey_nonce_array_append", 1)[1].split(
        "bool napi_mf_classic_mfkey32_nonces_check_presence", 1
    )[0]

    assert "MfClassicNonce* resized" in helper
    assert "if(!resized) return false;" in helper
    assert "nonce_array->remaining_nonce_array = resized;" in helper
    assert helper.index("if(!resized) return false;") < helper.index(
        "nonce_array->remaining_nonce_array = resized;"
    )
