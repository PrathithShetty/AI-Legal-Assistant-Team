"""Procedure guidance and safety checks (FR-12, FR-13, NFR-05, NFR-06)."""
import json

from .classifier import normalize
from .disclaimer import LEGAL_AID

# Situations where general information is not enough and a lawyer or official confirmation is needed (FR-13).
SERIOUS_PHRASES = {
    "arrest": "Arrest and bail matters need a lawyer quickly.",
    "arrested": "Arrest and bail matters need a lawyer quickly.",
    "bail": "Arrest and bail matters need a lawyer quickly.",
    "summons": "You have received a court or police summons; the deadline and response matter.",
    "warrant": "A warrant has legal consequences that need professional handling.",
    "chargesheet": "Criminal proceedings are involved.",
    "case against me": "A case has been filed against you.",
    "fir against me": "A case has been filed against you.",
    "court notice": "Court notices have strict deadlines.",
    "legal notice": "Replies to legal notices should be checked by an advocate.",
    "hearing": "A court hearing is involved.",
    "custody": "Custody matters are decided by courts based on detailed facts.",
    "divorce": "Divorce involves court proceedings and long-term consequences.",
    "domestic violence": "Your safety may be at risk; protection orders are available.",
    "eviction notice": "Eviction proceedings have strict timelines.",
    "property dispute": "Property disputes depend heavily on documents and local law.",
    "high court": "Proceedings in higher courts need an advocate.",
    "supreme court": "Proceedings in higher courts need an advocate.",
}

EMERGENCY_PHRASES = (
    "threat to life", "kill me", "going to kill", "beating me", "beaten", "attacked", "kidnap", "in danger",
    "unsafe", "suicide", "kill myself", "end my life",
)
SELF_HARM_PHRASES = ("suicide", "kill myself", "end my life")

EMERGENCY_MESSAGE = "If you or someone else is in immediate danger, call 112 (police) now. Women can also call 181."
SELF_HARM_MESSAGE = "If you are thinking about harming yourself, please call Tele-MANAS on 14416 for free, confidential support."


def _contains(padded, phrase):
    return f" {phrase} " in padded


def procedure_steps(category):
    return json.loads(category["steps"]) if category else []


def professional_help(text, category):
    """Return (needed, reasons) telling the user when a lawyer or official confirmation is needed."""
    padded = f" {' '.join(normalize(text).split())} "
    reasons = []
    for phrase, reason in SERIOUS_PHRASES.items():
        if _contains(padded, phrase) and reason not in reasons:
            reasons.append(reason)
    if category and category["needs_lawyer"] and not reasons:
        reasons.append(f"{category['name']} matters usually need advice from a qualified advocate.")
    return bool(reasons), reasons


def emergency_notices(text):
    padded = f" {' '.join(normalize(text).split())} "
    notices = []
    if any(_contains(padded, p) for p in EMERGENCY_PHRASES):
        notices.append(EMERGENCY_MESSAGE)
    if any(_contains(padded, p) for p in SELF_HARM_PHRASES):
        notices.append(SELF_HARM_MESSAGE)
    return notices


def lawyer_message(reasons):
    """The 'consult a lawyer' recommendation shown when FR-13 flags a query (NFR-06)."""
    if not reasons:
        return None
    return {
        "reasons": reasons,
        "advice": "We recommend speaking to a qualified advocate before you act. " + LEGAL_AID,
    }
