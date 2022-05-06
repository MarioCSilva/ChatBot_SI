data = {
    "greet": ["hello","hey there","howdy","hello","hi","hey","hey ho"],
    "chitchat": ["whats your name?"],
    "inform": [
        "i'd like something asian",
        "maybe korean",
        "what mexican options do i have",
        "what italian options do i have",
        "i want korean food",
        "i want german food",
        "i want vegetarian food",
        "i would like chinese food",
        "i would like indian food",
        "what japanese options do i have",
        "korean please",
        "what about indian",
        "i want some chicken",
        "maybe thai",
        "i'd like something vegetarian",
        "show me french restaurants",
        "show me a cool malaysian spot",
        "where can I get some spicy food"
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