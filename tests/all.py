# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from configcraft.tests import run_cov_test

    run_cov_test(
        __file__,
        "configcraft",
        is_folder=True,
        preview=False,
    )
