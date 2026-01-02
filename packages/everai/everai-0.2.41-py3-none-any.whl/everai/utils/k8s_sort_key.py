
def sort_key(key: str) -> int:
    weight = dict(
        version=10,
        kind=20,
        metadata=30,
        spec=40,
        status=1000,
    )
    if key in weight:
        return weight[key]
    return 500
