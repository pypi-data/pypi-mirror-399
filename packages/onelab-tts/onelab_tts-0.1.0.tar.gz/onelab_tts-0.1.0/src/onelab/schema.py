from typing import List, TypedDict


class Segment(TypedDict):
    voice: str
    text: str


class ConversationInput(TypedDict):
    segments: List[Segment]
