from file_state_manager.util_object_hash import UtilObjectHash

class TestUtilObjectHash:

    def test_old_compatibility(self):
        # Map tests
        m1 = {"a": "a"}
        m2 = {"a": "a"}
        m3 = {"a": "b"}
        m4 = {"b": "a"}
        m5 = {"a": "a", "b": "b"}
        assert UtilObjectHash.calc_map(m1) == UtilObjectHash.calc_map(m2)
        assert UtilObjectHash.calc_map(m1) != UtilObjectHash.calc_map(m3)
        assert UtilObjectHash.calc_map(m1) != UtilObjectHash.calc_map(m4)
        assert UtilObjectHash.calc_map(m1) != UtilObjectHash.calc_map(m5)

        m6 = {"a": {"a": 1}}
        m7 = {"a": {"a": 1}}
        m8 = {"a": {"a": 2}}
        m9 = {"b": {"a": 1}}
        m10 = {"a": {"a": 1}, "b": {"a": 1}}
        assert UtilObjectHash.calc_map(m6) == UtilObjectHash.calc_map(m7)
        assert UtilObjectHash.calc_map(m6) != UtilObjectHash.calc_map(m8)
        assert UtilObjectHash.calc_map(m6) != UtilObjectHash.calc_map(m9)
        assert UtilObjectHash.calc_map(m6) != UtilObjectHash.calc_map(m10)

        # List tests
        l1 = ["a"]
        l2 = ["a"]
        l3 = ["b"]
        l4 = ["a", "b"]
        assert UtilObjectHash.calc_list(l1) == UtilObjectHash.calc_list(l2)
        assert UtilObjectHash.calc_list(l1) != UtilObjectHash.calc_list(l3)
        assert UtilObjectHash.calc_list(l1) != UtilObjectHash.calc_list(l4)

        l6 = [[1]]
        l7 = [[1]]
        l8 = [[2]]
        l9 = [[1], [1]]
        assert UtilObjectHash.calc_list(l6) == UtilObjectHash.calc_list(l7)
        assert UtilObjectHash.calc_list(l6) != UtilObjectHash.calc_list(l8)
        assert UtilObjectHash.calc_list(l6) != UtilObjectHash.calc_list(l9)

        # Set tests
        s1 = {"a"}
        s2 = {"a"}
        s3 = {"b"}
        s4 = {"a", "b"}
        assert UtilObjectHash.calc_set(s1) == UtilObjectHash.calc_set(s2)
        assert UtilObjectHash.calc_set(s1) != UtilObjectHash.calc_set(s3)
        assert UtilObjectHash.calc_set(s1) != UtilObjectHash.calc_set(s4)

        # Pythonでは集合の集合(Set of Sets)は直接作れないため
        # frozensetを使用してネスト構造を再現
        s6 = {frozenset({1})}
        s7 = {frozenset({1})}
        s8 = {frozenset({2})}
        s9 = {frozenset({1}), frozenset({1})} # セットなので重複は1つになる
        assert UtilObjectHash.calc_set(s6) == UtilObjectHash.calc_set(s7)
        assert UtilObjectHash.calc_set(s6) != UtilObjectHash.calc_set(s8)
        # s9は要素が1つなのでs6と一致するはず
        assert UtilObjectHash.calc_set(s6) == UtilObjectHash.calc_set(s9)

    def test_map_hash_is_order_independent(self):
        map1 = {'a': 1, 'b': 2}
        map2 = {'b': 2, 'a': 1}
        assert UtilObjectHash.calc_map(map1) == UtilObjectHash.calc_map(map2)

    def test_list_hash_is_order_dependent(self):
        list1 = [1, 2, 3]
        list2 = [3, 2, 1]
        assert UtilObjectHash.calc_list(list1) != UtilObjectHash.calc_list(list2)

    def test_set_hash_is_order_independent(self):
        set1 = {1, 2, 3}
        set2 = {3, 2, 1}
        assert UtilObjectHash.calc_set(set1) == UtilObjectHash.calc_set(set2)

    def test_nested_structures_produce_consistent_hash(self):
        obj1 = {
            'list': [1, 2, {'x': 10, 'y': 20}],
            'set': {3, 4},
        }
        obj2 = {
            'set': {4, 3},
            'list': [1, 2, {'y': 20, 'x': 10}],
        }
        assert UtilObjectHash.calc_map(obj1) == UtilObjectHash.calc_map(obj2)

    def test_different_nested_values_produce_different_hash(self):
        obj1 = {'a': [1, 2, 3]}
        obj2 = {'a': [1, 2, 4]}
        assert UtilObjectHash.calc_map(obj1) != UtilObjectHash.calc_map(obj2)

    def test_null_values_are_handled_safely(self):
        map1 = {'a': None}
        map2 = {'a': None}
        assert UtilObjectHash.calc_map(map1) == UtilObjectHash.calc_map(map2)

    def test_primitive_values_produce_consistent_results(self):
        assert UtilObjectHash.calc_list([1, 'a', True]) == UtilObjectHash.calc_list([1, 'a', True])