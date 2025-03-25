import re
from collections import Counter as PyCounter
from collections import OrderedDict as PyOrderedDict
from collections import defaultdict, namedtuple
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum, Flag, IntEnum, auto
from ipaddress import IPv4Address, IPv6Address
from pathlib import Path
from typing import (
    Any,
    Callable,
    Counter,
    DefaultDict,
    Deque,
    Dict,
    FrozenSet,
    Generic,
    Iterable,
    Iterator,
    List,
    Literal,
    Mapping,
    MutableMapping,
    NamedTuple,
    NewType,
    Optional,
    OrderedDict,
    Protocol,
    Sequence,
    Set,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)
from uuid import UUID

import typtyp
from tests.helpers import check_with_tsc

T = TypeVar("T")
CustomID = NewType("CustomID", str)


# Enum classes
class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"


class UnixPermissions(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()


class NumEnum(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3


# Protocol definition
class Serializable(Protocol):
    def to_json(self) -> str: ...


# Dataclass for nested type
@dataclass
class Address:
    street: str
    city: str
    postal_code: str
    country: str


# NamedTuple example
class Point(NamedTuple):
    x: float
    y: float
    z: float = 0.0


# Complex TypedDict
class NestedConfig(TypedDict):
    timeout: int
    retry_count: int
    debug_mode: bool


Person2 = namedtuple("Person2", ["name", "age", "email"])


# The kitchen sink with ALL the types!
class KitchenSink(Generic[T], TypedDict, total=False):
    # Basic types
    string_field: str
    int_field: int
    float_field: float
    bool_field: bool
    none_field: None

    # Complex number
    complex_field: complex

    # Numeric specialized
    decimal_field: Decimal

    # Collections
    list_field: List[Any]
    int_list: List[int]
    nested_list: List[List[str]]

    # Tuples of various forms
    tuple_field: Tuple[int, str, bool]
    homogeneous_tuple: Tuple[int, ...]
    empty_tuple: Tuple[()]

    # Sets and variants
    set_field: Set[str]
    frozen_set: FrozenSet[int]

    # Dictionaries and variants
    dict_field: Dict[str, Any]
    int_to_str_dict: Dict[int, str]
    nested_dict: Dict[str, Dict[str, List[int]]]
    default_dict: DefaultDict[str, int]
    ordered_dict: OrderedDict[str, Any]
    counter_dict: Counter[str]

    # Optional and Union
    optional_field: Optional[str]
    union_field: Union[int, str, bool]
    optional_complex: Optional[Dict[str, List[Tuple[int, str]]]]

    # Time-related
    datetime_field: datetime
    date_field: date
    time_field: time
    timedelta_field: timedelta

    # Callable signatures
    some_callable: Callable
    simple_callback: Callable[[int], bool]
    complex_callback: Callable[[str, int, Dict[str, Any]], Optional[List[Tuple[int, str]]]]

    # Iterables
    iterator_field: Iterator[int]
    iterable_field: Iterable[str]
    sequence_field: Sequence[float]

    # Mappings
    mapping_field: Mapping[str, Any]
    mutable_mapping: MutableMapping[str, int]

    # Specialized collections
    deque_field: Deque[str]

    # Type references
    # TODO: type_reference: Type[Address]

    # Literals
    literal_field: Literal["red", "green", "blue"]
    literal_int: Literal[1, 2, 3, 5, 8]

    # Final (constant)
    # final_value: Final[str]

    # ClassVar
    # class_variable: ClassVar[Dict[str, Any]]

    # Regular expressions
    regex_pattern: re.Pattern

    # Custom type with NewType
    user_id: CustomID

    # Generic with TypeVar
    generic_container: List[T]

    # Path and file-related
    file_path: Path

    # Binary data
    binary_data: bytes
    bytearray_data: bytearray
    memoryview_data: memoryview

    # Network-related
    ipv4_address: IPv4Address
    ipv6_address: IPv6Address

    # UUID
    uuid_field: UUID

    # Protocol type
    # TODO: serializable_obj: Serializable

    # Enum types
    status: Status
    permissions: UnixPermissions
    favorite_number: NumEnum

    # Nested structures
    address: Address
    point: Point
    config: NestedConfig

    # Named tuple defined here
    named_tuple1: namedtuple("Person", ["name", "age", "email"])  # type: ignore
    named_tuple2: Person2

    # Special types
    any_field: Any
    ellipsis_field: ...  # type: ignore

    # Raw Python objects (non-typing)
    py_counter: PyCounter
    py_defaultdict: defaultdict
    py_ordered_dict: PyOrderedDict

    # Recursive type references
    recursive_field: "KitchenSink"


def test_kitchen_sink(snapshot):
    w = typtyp.World()
    w.add(KitchenSink)
    w.add(Address)
    w.add_many((Status, UnixPermissions))
    w.add(NumEnum, name="FavoriteNumberEnum")
    w.add(Point)
    w.add(NestedConfig)
    w.add(Person2)
    code = w.get_typescript()
    assert code == snapshot
    assert check_with_tsc(code)
