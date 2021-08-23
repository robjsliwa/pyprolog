import pytest
from prolog.prolog import start


def test_load_rules_bad_path():
    with pytest.raises(SystemExit):
        start('badpath')
