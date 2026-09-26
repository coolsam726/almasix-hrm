"""Directory-adjacent records, posts, claims, and language packs."""

from app.models.hrm import BuzzPost, ClaimRequest, ClaimType, LanguagePack
from app.orbit.hrm.resources.factory import crud

BuzzPostResource = crud(
    "BuzzPostResource",
    model=BuzzPost,
    label="Posts",
    group="Workplace",
    data_group="buzz",
    icon="heroicon-o-chat-bubble-left",
    sort=1,
    fields=("employee_id", "body"),
    mutable=False,
)
ClaimTypeResource = crud(
    "ClaimTypeResource",
    model=ClaimType,
    label="Claim types",
    group="Workplace",
    data_group="claim",
    icon="heroicon-o-tag",
    sort=2,
    fields=("name",),
)
ClaimRequestResource = crud(
    "ClaimRequestResource",
    model=ClaimRequest,
    label="Claims",
    group="Workplace",
    data_group="claim",
    icon="heroicon-o-receipt-percent",
    sort=3,
    fields=("employee_id", "amount", "state"),
    mutable=False,
)
LanguagePackResource = crud(
    "LanguagePackResource",
    model=LanguagePack,
    label="Language packs",
    group="Admin",
    data_group="admin",
    icon="heroicon-o-language",
    sort=21,
    fields=("code", "name"),
    mutable=False,
)
