# -*- coding: utf-8 -*-

from configcraft.inherit import (
    inherit_value,
    apply_inheritance,
)

import copy

import pytest


class TestInheritValue:
    def test_multi_parts_path(self):
        # one part
        data = {"key1": "value1"}
        inherit_value(path="key1", value="invalid", data=data)
        assert data["key1"] == "value1"  # no change
        inherit_value(path="key2", value="value2", data=data)
        assert data["key2"] == "value2"  # new key

        # two parts
        data = {"key1": {"key11": "value11"}}
        inherit_value(path="key1.key11", value="invalid", data=data)
        assert data["key1"]["key11"] == "value11"  # no change
        inherit_value(path="key1.key12", value="value12", data=data)
        assert data["key1"]["key12"] == "value12"  # new key

        # three parts
        data = {"key1": {"key11": {"key111": "value111"}}}
        inherit_value(path="key1.key11.key111", value="invalid", data=data)
        assert data["key1"]["key11"]["key111"] == "value111"  # no change
        inherit_value(path="key1.key11.key112", value="value112", data=data)
        assert data["key1"]["key11"]["key112"] == "value112"  # new key

    def test_list_of_dict(self):
        # one part
        data = [
            {"key1": "value1"},
            {"key1": "value1"},
        ]
        inherit_value(path="key1", value="invalid", data=data)
        assert data == [{"key1": "value1"}, {"key1": "value1"}]
        inherit_value(path="key2", value="value2", data=data)
        assert data == [
            {"key1": "value1", "key2": "value2"},
            {"key1": "value1", "key2": "value2"},
        ]

        # two parts
        data = {
            "tags": [
                {"key1": "value1"},
                {"key1": "value1"},
            ],
        }
        inherit_value(path="tags.key1", value="invalid", data=data)
        assert data["tags"] == [{"key1": "value1"}, {"key1": "value1"}]
        inherit_value(path="tags.key2", value="value2", data=data)
        assert data["tags"] == [
            {"key1": "value1", "key2": "value2"},
            {"key1": "value1", "key2": "value2"},
        ]

        # three parts
        data = {
            "persons": [
                {
                    "name": "alice",
                    "tags": [
                        {"key1": "value1"},
                        {"key1": "value1"},
                    ],
                },
                {
                    "name": "bob",
                    "tags": [
                        {"key1": "value1"},
                        {"key1": "value1"},
                    ],
                },
            ],
        }
        inherit_value(path="persons.tags.key2", value="value2", data=data)
        assert data["persons"][0]["tags"] == [
            {"key1": "value1", "key2": "value2"},
            {"key1": "value1", "key2": "value2"},
        ]
        assert data["persons"][1]["tags"] == [
            {"key1": "value1", "key2": "value2"},
            {"key1": "value1", "key2": "value2"},
        ]

    def test_with_star_notation(self):
        data = {
            "dev": {"key1": "dev_value1"},
            "prod": {"key1": "prod_value1"},
        }
        inherit_value(path="*.key1", value="invalid", data=data)
        assert data["dev"]["key1"] == "dev_value1"
        assert data["prod"]["key1"] == "prod_value1"
        inherit_value(path="*.key2", value="value2", data=data)
        assert data["dev"]["key2"] == "value2"
        assert data["prod"]["key2"] == "value2"

        data = {
            "envs": {
                "dev": {"key1": "dev_value1"},
                "prod": {"key1": "prod_value1"},
            }
        }
        inherit_value(path="envs.*.key1", value="invalid", data=data)
        assert data["envs"]["dev"]["key1"] == "dev_value1"
        assert data["envs"]["prod"]["key1"] == "prod_value1"
        inherit_value(path="envs.*.key2", value="value2", data=data)
        assert data["envs"]["dev"]["key2"] == "value2"
        assert data["envs"]["prod"]["key2"] == "value2"

        raw_data = {
            "envs": {
                "dev": {
                    "server": {
                        "blue": {"key1": "dev_blue_value1"},
                        "green": {"key1": "dev_green_value1"},
                    }
                },
                "prod": {
                    "server": {
                        "black": {"key1": "prod_black_value1"},
                        "white": {"key1": "prod_white_value1"},
                    }
                },
            }
        }

        data = copy.deepcopy(raw_data)
        inherit_value(path="envs.*.server.*.key1", value="value2", data=data)
        assert data["envs"]["dev"]["server"]["blue"]["key1"] == "dev_blue_value1"
        assert data["envs"]["dev"]["server"]["green"]["key1"] == "dev_green_value1"
        assert data["envs"]["prod"]["server"]["black"]["key1"] == "prod_black_value1"
        assert data["envs"]["prod"]["server"]["white"]["key1"] == "prod_white_value1"
        inherit_value(path="envs.*.server.*.key2", value="value2", data=data)
        assert data["envs"]["dev"]["server"]["blue"]["key2"] == "value2"
        assert data["envs"]["dev"]["server"]["green"]["key2"] == "value2"
        assert data["envs"]["prod"]["server"]["black"]["key2"] == "value2"
        assert data["envs"]["prod"]["server"]["white"]["key2"] == "value2"

        data = copy.deepcopy(raw_data)
        inherit_value(path="envs.dev.server.*.key1", value="value2", data=data)
        assert data["envs"]["dev"]["server"]["blue"]["key1"] == "dev_blue_value1"
        assert data["envs"]["dev"]["server"]["green"]["key1"] == "dev_green_value1"
        assert data["envs"]["prod"]["server"]["black"]["key1"] == "prod_black_value1"
        assert data["envs"]["prod"]["server"]["white"]["key1"] == "prod_white_value1"
        inherit_value(path="envs.dev.server.*.key2", value="value2", data=data)
        assert data["envs"]["dev"]["server"]["blue"]["key2"] == "value2"
        assert data["envs"]["dev"]["server"]["green"]["key2"] == "value2"
        assert "key2" not in data["envs"]["prod"]["server"]["black"]
        assert "key2" not in data["envs"]["prod"]["server"]["white"]

        raw_data = {
            "envs": {
                "dev": {
                    "server": {
                        "blue": {
                            "tags": [
                                {"key1": "dev_blue_value1"},
                            ],
                        },
                        "green": {
                            "tags": [
                                {"key1": "dev_green_value1"},
                            ],
                        },
                    }
                },
                "prod": {
                    "server": {
                        "black": {
                            "tags": [
                                {"key1": "prod_black_value1"},
                            ],
                        },
                        "white": {
                            "tags": [
                                {"key1": "prod_white_value1"},
                            ],
                        },
                    }
                },
            }
        }
        data = copy.deepcopy(raw_data)

        inherit_value(path="envs.*.server.*.tags.key1", value="invalid", data=data)
        dev, prod = data["envs"]["dev"], data["envs"]["prod"]
        assert dev["server"]["blue"]["tags"][0]["key1"] == "dev_blue_value1"
        assert dev["server"]["green"]["tags"][0]["key1"] == "dev_green_value1"
        assert prod["server"]["black"]["tags"][0]["key1"] == "prod_black_value1"
        assert prod["server"]["white"]["tags"][0]["key1"] == "prod_white_value1"

        inherit_value(path="envs.*.server.*.tags.key2", value="value2", data=data)
        dev, prod = data["envs"]["dev"], data["envs"]["prod"]
        assert dev["server"]["blue"]["tags"][0]["key2"] == "value2"
        assert dev["server"]["green"]["tags"][0]["key2"] == "value2"
        assert prod["server"]["black"]["tags"][0]["key2"] == "value2"
        assert prod["server"]["white"]["tags"][0]["key2"] == "value2"

    def test_edge_cases_type_and_value_error(self):
        data = {"key1": "value1"}

        with pytest.raises(ValueError):
            inherit_value(path="*", value="value", data={"k1": "v1"})

        with pytest.raises(TypeError):
            inherit_value(path="k1", value="v1", data="hello")

        with pytest.raises(TypeError):
            inherit_value(path="k1", value="v1", data=(1, 2, 3))

        with pytest.raises(TypeError):
            inherit_value(path="k1.k11", value="v11", data={"k1": "v1"})

        with pytest.raises(TypeError):
            inherit_value(path="k1.k11", value="v11", data={"k1": [1, 2, 3]})

        with pytest.raises(TypeError):
            inherit_value(path="k1.k11", value="v11", data="hello")

        with pytest.raises(TypeError):
            inherit_value(path="k1.k11.k111", value="v111", data={"k1": {"k11": "v11"}})

    def test_edge_cases_missing_keys(self):
        """Test behavior when intermediate keys in path don't exist."""
        data = {"env": {}}

        # Should raise KeyError when trying to access non-existent intermediate key
        with pytest.raises(KeyError):
            inherit_value(path="env.missing.key", value="value", data=data)

        # Test with list - should raise KeyError when item doesn't have required key
        data = {
            "envs": [
                {"name": "dev"},
                {"name": "prod"},
            ],
        }
        with pytest.raises(KeyError):
            inherit_value(path="envs.missing_key.field", value="value", data=data)

    def test_empty_data_structures(self):
        """Test behavior with empty data structures."""
        # Empty dict with star notation should do nothing (no items to iterate over)
        data = {}
        inherit_value(path="*.key", value="value", data=data)
        assert data == {}

        # Empty list should do nothing
        data = []
        inherit_value(path="key", value="value", data=data)
        assert data == []

        # Dict with empty subdicts
        data = {
            "env1": {},
            "env2": {},
        }
        inherit_value(path="*.key", value="value", data=data)
        assert data == {"env1": {"key": "value"}, "env2": {"key": "value"}}

    def test_star_with_defaults_key(self):
        """Test that star notation properly skips _defaults keys."""
        data = {
            "_defaults": {"some": "config"},
            "dev": {},
            "prod": {},
        }
        inherit_value(path="*.memory", value=2, data=data)

        # _defaults should not get the inherited value
        assert "_defaults" not in data or "memory" not in data["_defaults"]
        assert data["dev"]["memory"] == 2
        assert data["prod"]["memory"] == 2


class TestApplyInheritance:
    def test_edge_cases(self):
        """Test apply_inheritance with edge cases."""
        # Empty dict
        data = {}
        apply_inheritance(data)
        assert data == {}

        # Dict with no _defaults key
        data = {
            "dev": {"key": "value"},
            "prod": {"key": "value"},
        }
        original = data.copy()
        apply_inheritance(data)
        assert data == original  # Should be unchanged

        # Dict with empty _defaults
        data = {"_defaults": {}, "dev": {"key": "value"}}
        apply_inheritance(data)
        assert data == {"dev": {"key": "value"}}  # _defaults removed, no changes applied

        # Nested empty structures
        data = {"_defaults": {"*.key": "value"}, "env": {"nested": {}}}
        apply_inheritance(data)
        assert data == {"env": {"nested": {}, "key": "value"}}

    def test_with_nested_lists(self):
        """Test apply_inheritance processes lists properly."""
        data = {
            "_defaults": {"*.items.name": "default"},
            "env": {
                "items": [
                    {"id": 1},
                    {"id": 2, "name": "existing"},
                ],
            },
        }
        apply_inheritance(data)
        assert data == {
            "env": {
                "items": [{"id": 1, "name": "default"}, {"id": 2, "name": "existing"}]
            }
        }

    def test_complex_error_scenarios(self):
        """Test complex error scenarios for better error coverage."""
        # Try to traverse through a non-dict in the middle of a path
        data = {
            "env": {"config": "string_value"},
        }
        with pytest.raises(TypeError):
            inherit_value(path="env.config.nested", value="value", data=data)

        # List containing non-dict items when trying to traverse further
        data = {
            "envs": [{"valid": "dict"}, "invalid_string"],
        }
        with pytest.raises(TypeError):
            inherit_value(path="envs.key", value="value", data=data)

        # Mixed types in list during star traversal
        data = {
            "envs": [
                {"name": "env1"},
                None,
            ],
        }
        with pytest.raises(TypeError):
            inherit_value(path="envs.missing_key", value="value", data=data)

    def test_complicated_example(self):
        data = {
            "_defaults": {
                "*.key2": "value2",
                "*.a_dict.key2": "value2",
                # this conflict with dev.servers._defaults.*.cpu = 2
                # child value should override it
                "*.servers.*.cpu": 1,
                "*.databases.port": 1,
            },
            "dev": {
                "key1": "dev_value1",
                "a_dict": {
                    "key1": "dev_value1",
                },
                "servers": {
                    "_defaults": {
                        # this conflict with _defaults.*.servers.*.cpu = 1
                        # child value (THIS ONE) should override it
                        "*.cpu": 2,
                    },
                    "blue": {},
                    "green": {"cpu": 4},
                },
                "databases": [
                    {"host": "db1.com"},
                    {"host": "db2.com", "port": 2},
                ],
            },
            "prod": {
                "_defaults": {
                    "databases.port": 3,
                },
                "key1": "prod_value1",
                "a_dict": {
                    "key1": "prod_value1",
                },
                "servers": {
                    "black": {},
                    "white": {"cpu": 8},
                },
                "databases": [
                    {"host": "db3.com"},
                    {"host": "db4.com", "port": 4},
                ],
            },
        }
        apply_inheritance(data)

        assert data == {
            "dev": {
                "key1": "dev_value1",
                "key2": "value2",
                "a_dict": {
                    "key1": "dev_value1",
                    "key2": "value2",
                },
                "servers": {
                    # child _defaults should override parent _defaults
                    "blue": {"cpu": 2},
                    "green": {"cpu": 4},
                },
                "databases": [
                    {"host": "db1.com", "port": 1},
                    {"host": "db2.com", "port": 2},
                ],
            },
            "prod": {
                "key1": "prod_value1",
                "key2": "value2",
                "a_dict": {
                    "key1": "prod_value1",
                    "key2": "value2",
                },
                "servers": {
                    "black": {"cpu": 1},
                    "white": {"cpu": 8},
                },
                "databases": [
                    {"host": "db3.com", "port": 3},
                    {"host": "db4.com", "port": 4},
                ],
            },
        }


if __name__ == "__main__":
    from configcraft.tests import run_cov_test

    run_cov_test(
        __file__,
        "configcraft.inherit",
        preview=False,
    )
