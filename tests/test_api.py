# -*- coding: utf-8 -*-

from configcraft import api


def test():
    _ = api


if __name__ == "__main__":
    from configcraft.tests import run_cov_test

    run_cov_test(
        __file__,
        "configcraft.api",
        preview=False,
    )
