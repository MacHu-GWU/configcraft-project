# -*- coding: utf-8 -*-

from configcraft.merge import deep_merge

import pytest


def test_deep_merge_no_overlapping_keys():
    """Test merging when data2 has only new keys (difference set pattern)"""
    data1 = {"dev": {"username": "dev.user"}}
    data2 = {"prod": {"username": "prod.user"}}
    
    result = deep_merge(data1, data2)
    expected = {
        "dev": {"username": "dev.user"},
        "prod": {"username": "prod.user"}
    }
    assert result == expected


def test_deep_merge_only_data1_populated():
    """Test merging when data2 is empty (data1 preserved)"""
    data1 = {"dev": {"username": "dev.user"}}
    data2 = {}
    
    result = deep_merge(data1, data2)
    expected = {"dev": {"username": "dev.user"}}
    assert result == expected


def test_deep_merge_nested_dict_merge():
    """Test recursive merging of nested dictionaries"""
    data1 = {
        "database": {
            "host": "localhost",
            "port": 5432
        }
    }
    data2 = {
        "database": {
            "username": "admin",
            "password": "secret"
        }
    }
    
    result = deep_merge(data1, data2)
    expected = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "username": "admin", 
            "password": "secret"
        }
    }
    assert result == expected


def test_deep_merge_simple_list_merge():
    """Test positional merging of simple lists with dictionaries"""
    data1 = {
        "users": [
            {"username": "alice"},
            {"username": "bob"}
        ]
    }
    data2 = {
        "users": [
            {"password": "alice-pwd"},
            {"password": "bob-pwd"}
        ]
    }
    
    result = deep_merge(data1, data2)
    expected = {
        "users": [
            {"username": "alice", "password": "alice-pwd"},
            {"username": "bob", "password": "bob-pwd"}
        ]
    }
    assert result == expected


def test_deep_merge_mixed_keys_and_nesting():
    """Test combining new keys with nested merging"""
    data1 = {
        "dev": {"username": "dev.user"},
        "shared": {"timeout": 30}
    }
    data2 = {
        "shared": {"retry_count": 3},  # Merge with existing
        "prod": {"username": "prod.user"}  # New key
    }
    
    result = deep_merge(data1, data2)
    expected = {
        "dev": {"username": "dev.user"},
        "shared": {"timeout": 30, "retry_count": 3},
        "prod": {"username": "prod.user"}
    }
    assert result == expected


def test_deep_merge_comprehensive_scenario():
    """Test comprehensive scenario with all merge patterns combined"""
    # This test covers the original complex example but broken down logically
    data1 = {
        "dev": {
            "username": "dev.user",
        },
        "test": {
            "username": "test.user",
            "server": {
                "username": "ubuntu",
            },
            "databases": [
                {"host": "www.db1.com", "username": "admin"},
                {"host": "www.db2.com", "username": "admin"},
            ],
        },
    }
    data2 = {
        "test": {
            "password": "test.password",  # New key at test level
            "server": {
                "password": "ubuntu.password",  # Merge into existing server dict
            },
            "databases": [
                {"password": "db1pwd"},  # Merge into list items
                {"password": "db2pwd"},
            ],
        },
        "prod": {  # Completely new environment
            "password": "prod.password",
        },
    }
    
    result = deep_merge(data1, data2)
    expected = {
        "dev": {"username": "dev.user"},  # Unchanged (no overlap)
        "test": {
            "username": "test.user",  # Preserved from data1
            "password": "test.password",  # Added from data2
            "server": {"username": "ubuntu", "password": "ubuntu.password"},  # Merged
            "databases": [
                {"host": "www.db1.com", "username": "admin", "password": "db1pwd"},
                {"host": "www.db2.com", "username": "admin", "password": "db2pwd"},
            ],  # List items merged positionally
        },
        "prod": {"password": "prod.password"},  # New from data2
    }
    assert result == expected


def test_deep_merge_empty_dictionaries():
    """Test merging with empty dictionaries"""
    # Empty data1 with non-empty data2
    result = deep_merge({}, {"key": "value"})
    assert result == {"key": "value"}

    # Non-empty data1 with empty data2
    result = deep_merge({"key": "value"}, {})
    assert result == {"key": "value"}

    # Both empty
    result = deep_merge({}, {})
    assert result == {}


def test_deep_merge_empty_lists():
    """Test merging dictionaries with empty lists"""
    # Both have empty lists
    data1 = {"items": []}
    data2 = {"items": []}
    result = deep_merge(data1, data2)
    assert result == {"items": []}

    # One empty, one non-empty (should raise ValueError)
    data1 = {"items": []}
    data2 = {"items": [{"key": "value"}]}
    with pytest.raises(ValueError):
        deep_merge(data1, data2)


def test_deep_merge_deeply_nested():
    """Test merging with deeply nested structures"""
    data1 = {"level1": {"level2": {"level3": {"level4": {"username": "user"}}}}}
    data2 = {"level1": {"level2": {"level3": {"level4": {"password": "pass"}}}}}
    result = deep_merge(data1, data2)
    expected = {
        "level1": {
            "level2": {"level3": {"level4": {"username": "user", "password": "pass"}}}
        }
    }
    assert result == expected


def test_deep_merge_mixed_list_dict_errors():
    """Test error cases with mixed list and dict types"""
    # Dict in data1, list in data2
    with pytest.raises(TypeError):
        deep_merge({"key": {"nested": "value"}}, {"key": [{"item": "value"}]})

    # List in data1, dict in data2
    with pytest.raises(TypeError):
        deep_merge({"key": [{"item": "value"}]}, {"key": {"nested": "value"}})


def test_deep_merge_scalar_values():
    """Test error cases with scalar values that can't be merged"""
    test_cases = [
        # String values
        ({"key": "value1"}, {"key": "value2"}),
        # Integer values
        ({"key": 1}, {"key": 2}),
        # Boolean values
        ({"key": True}, {"key": False}),
        # None values
        ({"key": None}, {"key": None}),
        # Mixed scalar types
        ({"key": "string"}, {"key": 123}),
        ({"key": True}, {"key": "false"}),
        # List with non-dict items
        ({"key": ["item1"]}, {"key": ["item2"]}),
        ({"key": [1, 2]}, {"key": [3, 4]}),
    ]

    for data1, data2 in test_cases:
        with pytest.raises(TypeError):
            deep_merge(data1, data2)


def test_deep_merge_complex_list_scenarios():
    """Test complex list merging scenarios"""
    # Lists with nested dictionaries at multiple levels
    data1 = {
        "environments": [
            {
                "name": "dev",
                "services": [
                    {"name": "api", "port": 3000},
                    {"name": "worker", "port": 3001},
                ],
            },
            {"name": "prod", "services": [{"name": "api", "port": 8000}]},
        ]
    }
    data2 = {
        "environments": [
            {
                "password": "dev-secret",
                "services": [{"password": "api-secret"}, {"password": "worker-secret"}],
            },
            {"password": "prod-secret", "services": [{"password": "api-prod-secret"}]},
        ]
    }

    result = deep_merge(data1, data2)
    expected = {
        "environments": [
            {
                "name": "dev",
                "password": "dev-secret",
                "services": [
                    {"name": "api", "port": 3000, "password": "api-secret"},
                    {"name": "worker", "port": 3001, "password": "worker-secret"},
                ],
            },
            {
                "name": "prod",
                "password": "prod-secret",
                "services": [
                    {"name": "api", "port": 8000, "password": "api-prod-secret"}
                ],
            },
        ]
    }
    assert result == expected


def test_deep_merge_list_length_mismatches():
    """Test various list length mismatch scenarios"""
    # Different lengths at root level
    with pytest.raises(ValueError, match="list length mismatch: path = '.items'"):
        deep_merge({"items": [{"a": 1}, {"b": 2}]}, {"items": [{"c": 3}]})

    # Different lengths in nested structure
    with pytest.raises(
        ValueError, match="list length mismatch: path = '.env.databases'"
    ):
        deep_merge(
            {"env": {"databases": [{"host": "db1"}, {"host": "db2"}]}},
            {"env": {"databases": [{"password": "pwd1"}]}},
        )


def test_deep_merge_non_dict_items_in_lists():
    """Test error cases with non-dict items in lists"""
    # Mixed dict and non-dict in same list
    with pytest.raises(TypeError, match="items in '.mixed' are not dict"):
        deep_merge(
            {"mixed": [{"key": "value"}, "string_item"]},
            {"mixed": [{"other": "value"}, {"dict": "item"}]},
        )

    # Non-dict items in nested lists
    with pytest.raises(TypeError, match="items in '.env.items' are not dict"):
        deep_merge({"env": {"items": [1, 2, 3]}}, {"env": {"items": [4, 5, 6]}})


def test_deep_merge_immutability():
    """Test that original dictionaries are not modified"""
    original_data1 = {"shared": {"username": "user"}, "unique1": "value1"}
    original_data2 = {"shared": {"password": "pass"}, "unique2": "value2"}

    # Keep references to original data
    data1_copy = original_data1.copy()
    data2_copy = original_data2.copy()

    # Perform merge
    result = deep_merge(original_data1, original_data2)

    # Verify originals are unchanged
    assert original_data1 == data1_copy
    assert original_data2 == data2_copy

    # Verify result is correct
    expected = {
        "shared": {"username": "user", "password": "pass"},
        "unique1": "value1",
        "unique2": "value2",
    }
    assert result == expected


def test_deep_merge_edge_case_values():
    """Test merging with edge case values"""
    # Special values that should still work
    data1 = {
        "config": {
            "empty_string": "",
            "zero": 0,
            "false_bool": False,
            "empty_list": [],
            "empty_dict": {},
        }
    }
    data2 = {
        "config": {"none_value": None, "empty_dict": {"added": "value"}},
        "new_section": {"value": "added"},
    }

    result = deep_merge(data1, data2)
    expected = {
        "config": {
            "empty_string": "",
            "zero": 0,
            "false_bool": False,
            "empty_list": [],
            "empty_dict": {"added": "value"},
            "none_value": None,
        },
        "new_section": {"value": "added"},
    }
    assert result == expected


def test_deep_merge_error_path_reporting():
    """Test that error messages include correct path information"""
    # Test path reporting in nested TypeError
    with pytest.raises(
        TypeError, match="type of value at '.level1.level2' in data1 and data2"
    ):
        deep_merge(
            {"level1": {"level2": "string"}}, {"level1": {"level2": {"dict": "value"}}}
        )

    # Test path reporting in deeply nested ValueError
    with pytest.raises(ValueError, match="list length mismatch: path = '.a.b.c'"):
        deep_merge(
            {"a": {"b": {"c": [{"x": 1}]}}}, {"a": {"b": {"c": [{"y": 2}, {"z": 3}]}}}
        )


if __name__ == "__main__":
    from configcraft.tests import run_cov_test

    run_cov_test(
        __file__,
        "configcraft.merge",
        preview=False,
    )
