from pydantic import BaseModel, Field

from typing import List, Optional, Dict, TypedDict


class AttachmentPayload(BaseModel):
    url: str


class Attachment(BaseModel):
    type: str
    payload: AttachmentPayload


class QuickReply(BaseModel):
    payload: str


class AdsContextData(BaseModel):
    ad_title: str
    photo_url: str
    video_url: str


class Referral(BaseModel):
    ref: Optional[str]
    ad_id: Optional[str]
    source: Optional[str]
    type: Optional[str]
    ads_context_data: Optional[AdsContextData]


class ReplyToStory(BaseModel):
    url: str
    id: str


class ReplyTo(BaseModel):
    mid: Optional[str]
    story: Optional[ReplyToStory]


class Message(BaseModel):
    mid: str
    attachments: Optional[List[Attachment]] = None
    is_deleted: Optional[bool] = None
    is_echo: bool = Field(default=False)
    is_unsupported: Optional[bool] = None
    quick_reply: Optional[QuickReply] = None
    referral: Optional[Referral] = None
    reply_to: Optional[ReplyTo] = None
    text: Optional[str] = None


class Messaging(BaseModel):
    sender: Dict[str, str]
    recipient: Dict[str, str]
    timestamp: int
    message: Message


class Entry(BaseModel):
    id: str
    time: int
    messaging: List[Messaging]

class Update(BaseModel):
    object: str
    entry: List[Entry]

class InstagramUser(BaseModel):
    id: str
    username: str
    name: str
    
class SendResponse(TypedDict):
    recipient_id: str
    message_id: str



