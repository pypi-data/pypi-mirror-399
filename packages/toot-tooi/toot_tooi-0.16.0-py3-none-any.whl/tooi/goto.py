from dataclasses import dataclass


@dataclass
class Goto: ...


@dataclass
class GotoHomeTimeline(Goto): ...


@dataclass
class GotoPersonalTimeline(Goto): ...


@dataclass
class GotoLocalTimeline(Goto): ...


@dataclass
class GotoFederatedTimeline(Goto): ...


@dataclass
class GotoNotifications(Goto): ...


@dataclass
class GotoConversations(Goto): ...


@dataclass
class GotoHashtagTimeline(Goto):
    tag: str


@dataclass
class GotoContextTimeline(Goto):
    status_id: str
