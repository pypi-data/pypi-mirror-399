from typing import Optional, Any, List
from datetime import datetime

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from marshmallow import fields

from ._http_client import HttpClient
from .conversation import AttachmentType, ParticipantType


@dataclass_json
@dataclass(frozen=True)
class Attachment:
    # type of file that was uploaded.
    type: AttachmentType

    # file_name is the name of the file that was uploaded, or an
    # adequate placeholder for that name, which can be shown to reviewers.
    file_name: str

    # url is the publicly accessible URL where the attachment can be downloaded
    # from. This should be a fully qualified URL. If not given, the AI agent will
    # only know that an attachment exists, but will be unable to process it.
    url: Optional[str] = ""

    # description is an optional description of the attachment. This is only intended
    # to be used if you cannot give us access to the raw attachment, but can
    # run your own LLM completions on the attachment and send us a description instead.
    #
    # Chat to us first before using it!
    description: Optional[str] = ""


@dataclass_json
@dataclass(frozen=True)
class AddMessageParams:
    # id uniquely identifies this message within the conversation.
    #
    # Can be anything consisting of letters, numbers, or any of the following
    # characters: _ - + =.
    #
    # Tip: use something meaningful to your business.
    id: str

    # body contains the message text.
    body: str

    # participant_id identifies the message sender.
    participant_id: str

    # participant_type identifies the type of participant who sent this message.
    # This cannot be set to ParticipantTypeAI.
    participant_type: ParticipantType

    # created is the time at which the message was sent.
    created: Optional[datetime] = None

    # metadata is arbitrary metadata that will be attached to the message.
    metadata: Optional[Any] = None

    # attachments contains any files that were uploaded with this message.
    attachments: Optional[List[Attachment]] = None


@dataclass_json
@dataclass(frozen=True)
class Message:
    # id uniquely identifies this message within the conversation.
    #
    # Can be anything consisting of letters, numbers, or any of the following
    # characters: _ - + =.
    #
    # Tip: use something meaningful to your business.
    id: str

    # body contains the message text.
    body: str

    # participant_id identifies the message sender.
    participant_id: str

    # participant_type identifies the type of participant who sent this message.
    participant_type: ParticipantType

    # Created is the time at which the message was sent.
    created: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format="iso"),
        )
    )

    # Metadata is arbitrary metadata attached to the message.
    metadata: Optional[Any] = None

    # attachments contains any files that were uploaded with this message.
    attachments: Optional[List[Attachment]] = None

    # conversation_token is the raw sensitive token that can be optionally provided in every message.
    # The latest token of the conversation will be echoed back in future Webhooks, under the header `X-GradientLabs-Token`,
    # as well as in HTTP Tools using templates.
    conversation_token: Optional[str] = None


def add_message(
    *, client: HttpClient, conversation_id: str, params: AddMessageParams
) -> Message:
    body = {
        "id": params.id,
        "body": params.body,
        "participant_id": params.participant_id,
        "participant_type": params.participant_type.value,
    }
    if params.created is not None:
        body["created"] = HttpClient.localize(params.created)
    if params.metadata is not None:
        body["metadata"] = params.metadata
    if params.attachments is not None:
        body["attachments"] = [a.to_dict() for a in params.attachments]
    if params.conversation_token is not None:
        body["conversation_token"] = params.conversation_token

    rsp = client.post(path=f"conversations/{conversation_id}/messages", body=body)
    return Message.from_dict(rsp)
