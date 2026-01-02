import pytest
import spikesafe_python

@pytest.mark.parametrize(
    "version1, version2, expected",
    [
        ("1.2.3", "1.2.3", True), # equal versions
        ("2.0.0", "1.9.9", True), # major version higher
        ("1.3.0", "1.2.9", True), # minor version higher
        ("1.2.4", "1.2.3", True), # build version higher
        ("1.2.3", "2.0.0", False), # major version lower
        ("1.2.3", "1.3.0", False), # minor version lower
        ("1.2.3", "1.2.4", False), # build version lower
        ("1.2.3.4", "1.2.3", True), # extra revision number
        ("1.2.3", "1.2.3.4", False), # extra revision number
    ]
)
def test_compare_rev_version(version1, version2, expected):
    result = spikesafe_python.SpikeSafeInfoParser.compare_rev_version(version1, version2)
    assert result == expected