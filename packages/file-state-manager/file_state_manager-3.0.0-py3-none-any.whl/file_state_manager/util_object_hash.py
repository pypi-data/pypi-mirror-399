from typing import Any, Dict, List, Set


class UtilObjectHash:
    """
    (en) This is a utility for object hash calculations.
    This makes it easy to calculate hashes, for example
    if you want to enable enableDiffCheck flag in FileStateManager.

    (ja) これはオブジェクトハッシュ計算用のユーティリティです。
    利用することで、FileStateManagerのenableDiffCheckフラグを有効化したい場合などに、
    ハッシュ計算を簡単に行えます。
    """

    @staticmethod
    def calc_map(m: Dict[Any, Any]) -> int:
        """
        (en) Calculate hash code for Dict. Supports nesting of Dicts, Lists, and Sets.

        (ja) Dictのハッシュコードを計算します。Dict, List, Setのネストに対応しています。
        """
        # キーと値のペアをタプルにしてハッシュ化し、それをfrozensetに集約（順序不問）
        return hash(frozenset((hash(k), UtilObjectHash._deep_hash_code(v)) for k, v in m.items()))

    @staticmethod
    def calc_list(lst: List[Any]) -> int:
        """
        (en) Calculate hash code for list. Supports nesting of Dicts, Lists, and Sets.

        (ja) Listのハッシュコードを計算します。Dict, List, Setのネストに対応しています。
        """
        # リストは順序が重要なので、そのままタプル化してハッシュ計算
        return hash(tuple(UtilObjectHash._deep_hash_code(v) for v in lst))

    @staticmethod
    def calc_set(s: Set[Any]) -> int:
        """
        (en) Calculate hash code for set. Supports nesting of Dicts, Lists, and Sets.

        (ja) Setのハッシュコードを計算します。Dict, List, Setのネストに対応しています。
        """
        # セットは順序不問なので、各要素のハッシュをfrozensetに集約
        return hash(frozenset(UtilObjectHash._deep_hash_code(v) for v in s))

    @staticmethod
    def _deep_hash_code(v: Any) -> int:
        """
        (en) Recursively parses a data structure to generate a hash seed.

        (ja) 再帰的にデータ構造を解析してハッシュの種を生成します。
        """
        if isinstance(v, dict):
            return UtilObjectHash.calc_map(v)
        elif isinstance(v, list):
            return UtilObjectHash.calc_list(v)
        elif isinstance(v, set):
            return UtilObjectHash.calc_set(v)
        elif v is None:
            return 0
        return hash(v)
