data = {
    "greet": ["hello","hey there","howdy","hello","hi","hey","hey ho"],
    "chitchat": ["whats your name?"],
    "inform": [
        "flights are safe",
    ],
    "deny": [
        "nah",
        "any other places ?",
        "anything else",
        "no thanks"
        "not that one",
        "i do not like that place",
        "something else please",
        "no please show other options"
    ],
    "affirm": [
        "yeah",
        "that works",
        "good, thanks",
        "this works",
        "sounds good",
        "thanks, this is perfect",
        "just what I wanted"
    ],
}

response_map = {
    "greet": "utter_greet",
    "affirm": "utter_goodbye",
    "deny": "utter_options",
    "inform": "utter_confirm",
    "default": "utter_default",
    "chitchat": "utter_chitchat",
    "chithcat2": "utter_chitchat2"
}
