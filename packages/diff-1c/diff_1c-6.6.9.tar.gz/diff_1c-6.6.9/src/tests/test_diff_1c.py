import pytest

from diff_1c.cli import get_argparser
from diff_1c.main import run


@pytest.fixture()
def test():
    parser = get_argparser()

    return parser


def test_run(test):
    parser = test

    args = parser.parse_args("data/test.epf data/test.epf".split())
    run(args)
