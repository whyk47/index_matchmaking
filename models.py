from dataclasses import dataclass, field


@dataclass
class Offer:
    module: str
    have_index: str
    want_indexes: set[str] = field(default_factory=set)


@dataclass
class Message:
    sender: str
    timestamp: str
    content: str
