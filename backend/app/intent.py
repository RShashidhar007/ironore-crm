"""
Intent classification and lightweight entity extraction.

This is deliberately rule-based (fast, deterministic, auditable) rather
than delegated to the LLM: the LLM's job is customer-friendly phrasing
of verified data, not deciding which backend function/API to call.
"""
import re
from enum import Enum


class Intent(str, Enum):
    CUSTOMER_LOGIN = "CUSTOMER_LOGIN"
    CUSTOMER_INFORMATION = "CUSTOMER_INFORMATION"
    PRODUCT_INFORMATION = "PRODUCT_INFORMATION"
    PRODUCT_CATEGORY = "PRODUCT_CATEGORY"
    IRON_ORE_SPECIFICATION = "IRON_ORE_SPECIFICATION"
    IRON_PELLET_SPECIFICATION = "IRON_PELLET_SPECIFICATION"
    QUOTATION_REQUEST = "QUOTATION_REQUEST"
    ORDER_REQUEST = "ORDER_REQUEST"
    ORDER_TRACKING = "ORDER_TRACKING"
    INVENTORY_CHECK = "INVENTORY_CHECK"
    COMPLAINT = "COMPLAINT"
    COMPLAINT_TRACKING = "COMPLAINT_TRACKING"
    WHATSAPP_CONTACT = "WHATSAPP_CONTACT"
    HUMAN_SUPPORT = "HUMAN_SUPPORT"
    GREETING = "GREETING"
    UNKNOWN = "UNKNOWN"


# Ordered: more specific intents are checked before broader ones.
_KEYWORDS = [
    (Intent.WHATSAPP_CONTACT, ["whatsapp"]),
    # Customer information must come before ORDER_TRACKING to avoid false matches
    (Intent.CUSTOMER_INFORMATION, ["my details", "my information", "my customer code",
                                    "my gst", "my pan", "my address", "my email",
                                    "my contact person", "customer details", "my account"]),
    (Intent.COMPLAINT_TRACKING, ["complaint status", "complaint progress", "track complaint", 
                                  "check complaint", "complaint id", "complaint number",
                                  "my complaint", "cmp-"]),
    (Intent.ORDER_TRACKING, ["where is my order", "dispatch status", "delivery status",
                              "eta", "vehicle number"]),
    (Intent.ORDER_REQUEST, ["place an order", "place order", "i want to order",
                             "book an order", "purchase order", "buy "]),
    (Intent.QUOTATION_REQUEST, ["quotation", "quote", "price", "pricing", "rate for"]),
    (Intent.COMPLAINT, ["complaint", "complain", "poor quality", "bad quality",
                         "issue with", "problem with", "defect", "damaged", "not satisfied",
                         "raise a complaint", "raise complaint"]),
    (Intent.INVENTORY_CHECK, ["available", "availability", "stock", "how many tonnes",
                               "how much quantity", "in stock"]),
    (Intent.IRON_PELLET_SPECIFICATION, ["pellet spec", "pellet parameter", "testing standard",
                                         "iron pellet"]),
    (Intent.IRON_ORE_SPECIFICATION, ["iron ore spec", "ore spec", "fe%", "fe percentage",
                                      "sio2", "sio₂", "al2o3", "al₂o₃", "moisture",
                                      "specification", "spec of", "lot no", "lot number",
                                      "iron ore"]),
    (Intent.PRODUCT_CATEGORY, ["category", "categories"]),
    (Intent.PRODUCT_INFORMATION, ["product", "products", "pellet", "ore "]),
    (Intent.HUMAN_SUPPORT, ["human", "agent", "representative", "talk to someone",
                             "support team", "sales team", "call me"]),
    (Intent.GREETING, ["hi", "hello", "hey", "good morning", "good afternoon",
                        "good evening", "thanks", "thank you"]),
]


def classify_intent(message: str) -> Intent:
    text = (message or "").lower().strip()
    if not text:
        return Intent.UNKNOWN
    for intent, keywords in _KEYWORDS:
        for kw in keywords:
            if kw in text:
                return intent
    return Intent.UNKNOWN


# Common chemical/physical parameter aliases -> canonical tokens used for
# fuzzy matching against whatever Parameter values actually exist in the DB.
PARAMETER_ALIASES = {
    "fe": ["fe", "iron", "fe%", "fe content"],
    "sio2": ["sio2", "sio₂", "silica"],
    "al2o3": ["al2o3", "al₂o₃", "alumina"],
    "moisture": ["moisture", "h2o"],
    "size": ["size", "sizing", "pellet size"],
    "lom": ["lom", "loss on ignition", "loi"],
    "cs": ["cs", "cold crushing strength", "crushing strength"],
    "s": ["sulphur", "sulfur"],
    "p": ["phosphorus"],
    "mn": ["manganese", "mn"],
}


def extract_product_hint(message: str) -> str | None:
    """Pull a likely product-id/name token out of free text, e.g. 'P001'."""
    match = re.search(r"\b([Pp]-?\d{2,6})\b", message or "")
    if match:
        return match.group(1)
    return None


def extract_lot_hint(message: str) -> str | None:
    match = re.search(r"lot\s*(no\.?|number)?\s*[:#]?\s*([A-Za-z0-9\-\/]+)", message or "",
                       re.IGNORECASE)
    if match:
        return match.group(2)
    return None


def extract_complaint_id(message: str) -> str | None:
    """Extract complaint ID from message, e.g., 'CMP-20240115-0001'."""
    match = re.search(r"(CMP-\d{8}-\d{4})", message or "", re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def extract_parameter_hint(message: str) -> str | None:
    text = (message or "").lower()
    for canonical, aliases in PARAMETER_ALIASES.items():
        for alias in aliases:
            if alias in text:
                return canonical
    return None
