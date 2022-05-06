from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import spacy
import logging
import numpy as np
import random
from utils import data, response_map

# Logger
logging.basicConfig(
    format="%(module)-20s:%(levelname)-15s| %(message)s",
    level=logging.INFO
)

class ChatBotWrapper:
    def __init__(self) -> None:
        logging.info("Starting Bot....")
        self.nlp = spacy.load("en_core_web_md")
        self.min_similarity = 0.95
        self.user_name = None
        self.bot_name = "X Æ A-XII"
        self.get_templates()


    def chatbot(self):
        intent = "greet"
        print(self.get_bot_response(intent))

        while True:
            try:
                statement = self.nlp(input("> "))
                if intent == "chitchat":
                    for ent in statement.ents:
                        if ent.label_ == "PERSON":
                            self.user_name = ent.text
                    if self.user_name:
                        self.get_templates()
                        intent = "chithcat2"
                else:
                    intent = self.get_intent(statement)

                bot_response = self.get_bot_response(intent)
                print(bot_response)

            except(KeyboardInterrupt, EOFError, SystemExit):
                break            


    def get_intent(self, statement):
        max_similarity = 0
        final_intent = None

        for intent, examples in data.items():
            for example in examples:
                # TODO: n tar smp a fazer nlp do example
                similarity = self.nlp(example).similarity(statement)

                if max_similarity < similarity:
                    max_similarity = similarity
                    final_intent = intent

        if max_similarity < self.min_similarity:
            return None

        return final_intent


    def get_bot_response(self, intent):
        if intent not in list(response_map):
            # TODO: maybe use chatterbot to generate default response
            intent = "default"

        return random.choice(self.templates[response_map[intent]])
    
    def get_templates(self):
        user_name_text = ' ' + self.user_name if self.user_name else ''
        bot_name_text = ' ' + self.bot_name if self.bot_name else ''

        self.templates = {
            "utter_greet": [f"hey there{user_name_text}! How are you?", f"Hey{user_name_text}! How you doin'? ", f"Hey{user_name_text}! What's up?"],
            "utter_options": ["ok, let me check some more"],
            "utter_goodbye": ["Great, I'll go now. Bye bye", "bye bye", "Goodbye!", "See ya!"],
            "utter_default": ["Sorry, I didn't quite follow"],
            "utter_confirm": ["Got it", "Gotcha", "Your order is confirmed now"],
            "utter_chitchat": [f"My name is{bot_name_text}. What about yours?"],
            "utter_chitchat2": [f"Nice to meet you{user_name_text}!"],
        }


if __name__ == "__main__":
    ChatBotWrapper().chatbot()