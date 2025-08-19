# -*- coding: utf-8 -*-

from configcraft import api


def test():
    _ = api
    _ = api.DEFAULTS
    _ = api.inherit_value
    _ = api.apply_inheritance
    _ = api.deep_merge


if __name__ == "__main__":
    from configcraft.tests import run_cov_test

    run_cov_test(
        __file__,
        "configcraft.api",
        preview=False,
    )
