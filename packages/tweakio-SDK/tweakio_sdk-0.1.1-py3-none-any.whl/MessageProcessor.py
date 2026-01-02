"""
Message Class for WhatsApp chats
"""
import time
from dataclasses import dataclass, field
from queue import Queue
from typing import Union, List, Dict, Literal, Optional

from playwright.async_api import Page, Locator, ElementHandle

import Extra as ex
import directory as dirs
import selector_config as sc
from Errors import MessageNotFound
from Shared_Resources import logger


class MessageProcessor:
    """
    This class will contain :
    - Message Fetching - Full / Live Fetching
    - Tracer

    -- So Message Fetching means :
    ==== Full :
    You will get all the messages of the page currently visible in the dom
    - can select incoming / outgoing messages / Both
    default : both

    ==== Live :
    You will get all messages + Bot will wait for the current new messages if received
    while processing the old ones.

    ----- Tracer :
    Tracer stores processed message IDs in SQLite to avoid duplicates.
    """

    def __init__(
            self,
            page: Page,
            trace_path: str = str(dirs.MessageTrace_file),
            LimitTime: int = 3600,
            MaxMessagesPerWindow: int = 10,
            WindowSeconds: int = 60,
    ) -> None:

        self.page: Page = page
        self.trace_path = trace_path

        # Rate-limit config
        self.LimitTime = LimitTime  # Max defer lifetime
        self.MaxMessagesPerWindow = MaxMessagesPerWindow
        self.WindowSeconds = WindowSeconds

        # Chat tracking
        self.ChatState: Dict[str, "ChatState"] = {}
        self.DeferQueue: Queue["BindChat"] = Queue()

        # Persistent storage (SQLite)
        from Storage import Storage
        self.storage = Storage()

    @staticmethod
    async def _wrappedMessageList(
            chat: Union[Locator, ElementHandle]
    ) -> List[Message]:
        await chat.click(timeout=3000)

        wrapped: List[Message] = []
        all_msgs = sc.messages(page=self.page)

        count = await all_msgs.count()
        for i in range(count):
            msg = all_msgs.nth(i)
            text = await sc.get_message_text(msg)
            wrapped.append(
                Message(
                    messageUI=msg,
                    Direction="in" if await msg.locator(".message-in").count() > 0 else "out",
                    text=text
                )
            )
        return wrapped

    async def MessageFetcher(
            self,
            chat: Union["Locator", "ElementHandle"],
    ) -> List[Message]:
        """
        Fetch messages → trace → filter → return deliverable messages
        """
        try:
            messages: List["Message"] = await MessageProcessor._wrappedMessageList(chat=chat)
            if not messages:
                raise MessageNotFound()

            for msg in messages:
                data_id = await sc.get_dataID(msg.messageUI)
                if not data_id:
                    continue

                if self.storage.message_exists(data_id):
                    continue

                trace_data = await ex.Trace_dict(
                    chat=chat,
                    message=msg.messageUI,
                    data_id=data_id,
                )

                if not (trace_data and self.storage.insert_message(trace_data)):
                    msg.Failed = True

            # Todo Fix to Message Wrapper class List

            return self.Filter(chat, messages)

        except Exception as e:
            logger.error(f"[MessageFetcher] {e}", exc_info=True)
            return []

    def Filter(
            self,
            chat: Union["Locator", "ElementHandle"],
            messages: List["Message"],
    ) -> List["Message"]:
        """
        Rate Limit the chat and give state based returning.
        States :
        1. Deliver
        2. Defer
        3. Drop
        """

        if not messages:
            return []

        chat_id = self._chat_key(chat)
        now = time.time()

        state = self.ChatState.get(chat_id)
        if not state:
            state = ChatState()
            self.ChatState[chat_id] = state

        # Reset window if expired
        if now - state.window_start >= self.WindowSeconds:
            state.window_start = now
            state.count = 0

        # Hard drop: chat deferred too long
        if state.defer_since and (now - state.defer_since) > self.LimitTime:
            logger.warning(f"[Filter] Dropping old deferred messages for {chat_id}")
            state.reset()
            return messages

        # Rate limit hit → defer entire chat
        if state.count + len(Message.GetIncomingMessages(messages)) > self.MaxMessagesPerWindow:
            if not state.defer_since:
                state.defer_since = now
            self.DeferQueue.put(BindChat(chat, messages, now))
            logger.info(f"[Filter] Deferred chat {chat_id}")
            return []

        # Deliver
        state.count += len(messages)
        state.last_seen = now
        return messages

    @staticmethod
    def _chat_key(chat: Union["Locator", "ElementHandle"]) -> str:
        """
        Stable identifier for chat in SDK runtime
        """
        return str(id(chat))


@dataclass
class ChatState:
    """
    Per-chat rate-limit & defer state
    """
    window_start: float = field(default_factory=time.time)
    count: int = 0
    defer_since: Optional[float] = None
    last_seen: Optional[float] = None

    def reset(self) -> None:
        """Reset the state"""
        self.window_start = time.time()
        self.count = 0
        self.defer_since = None


@dataclass
class BindChat:
    """
    Pack for per-chat filtered message batch
    """
    chat: Union["Locator", "ElementHandle"]
    messages: List[Message]
    seen_at: float


@dataclass
class Message:
    """
    Message wrapper for filtered parsing
    """
    messageUI: Union["Locator", "ElementHandle"]
    Direction: Literal["in", "out"]
    System_Hit_Time: float = field(default_factory=time.time)
    Failed: bool = False
    text: Optional[str] = None

    @staticmethod
    def GetIncomingMessages(MsgList: List["Message"]) -> List["Message"]:
        """Filter Incoming Messages"""
        Mlist: List[Message] = []
        for msg in MsgList:
            if msg.Direction == "in":
                Mlist.append(msg)
        return Mlist

    @staticmethod
    def GetOutgoingMessages(MsgList: List["Message"]) -> List["Message"]:
        """Filter Outgoing Messages"""
        Mlist: List[Message] = []
        for msg in MsgList:
            if msg.Direction == "out":
                Mlist.append(msg)
        return Mlist
