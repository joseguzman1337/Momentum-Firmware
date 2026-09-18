from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path("scripts").resolve()))

from version import format_build_date


def test_format_build_date_uses_qflipper_day_month_year_format():
    assert format_build_date(date(2026, 9, 17)) == "17-09-2026"


def test_version_generator_does_not_pin_a_historical_build_date():
    source = open("scripts/version.py", encoding="utf-8").read()
    assert '"BUILD_DATE": "25-02-2026"' not in source
    assert '"BUILD_DATE": format_build_date()' in source
