import collections

COLLECTION_ORIGINS = (
    list,
    collections.deque,
    set,
    frozenset,
    collections.abc.Iterable,
    collections.abc.Iterator,
    collections.abc.Sequence,
)

MAPPING_ORIGINS = (
    dict,
    collections.defaultdict,
    collections.abc.Mapping,
    collections.abc.MutableMapping,
    collections.OrderedDict,
)
