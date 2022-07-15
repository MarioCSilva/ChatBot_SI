from collections import defaultdict
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import spacy
import random
from utils import data, response_map, ENGLISH_LANG
from cities import airport_pt_cities, pt_cities
from spacytextblob.spacytextblob import SpacyTextBlob
import numerizer
from colorama import Style, Fore
from sutime import SUTime
import datetime
from flights_search import FlightsSearch
from places_info import PlacesInfo

class ChatBotWrapper:
    def __init__(self) -> None:
        print("Starting Bot...\n")

        self.sutime = SUTime()

        self.bot_name = "X Æ A-XII"

        self.nlp = spacy.load("en_core_web_md")
        self.nlp.add_pipe('spacytextblob')

        self.chatterbot = ChatBot(
            self.bot_name, storage_adapter="chatterbot.storage.SQLStorageAdapter", tagger_language=ENGLISH_LANG)
        trainer = ChatterBotCorpusTrainer(self.chatterbot)
        trainer.train('chatterbot.corpus.english')

        self.min_similarity = 0.9
        self.intent_nlp = defaultdict(list)
        self.process_intent_dataset()

        self.user_name = None
        self.city_departure = None
        self.city_arrival = None

        self.get_templates()

        self.fs = FlightsSearch()  # Class to search available flights
        self.pi = PlacesInfo()  # Class to search attractions of a city

    def start(self):
        intent = "greet"
        print("\nBot is ready for interaction.\n")
        print(f"{Fore.GREEN}chatbot >{Style.RESET_ALL} {self.get_bot_response(intent)}")

        while True:
            try:
                statement = self.nlp(
                    input(f"\n{Fore.BLUE}me >{Style.RESET_ALL} ").lower())
                print(f"\n{Fore.GREEN}chatbot >{Style.RESET_ALL} ", end='')

                # <------------------ begin state greetings ------------------

                if intent == "greet":
                    if not self.user_name:
                        for ent in statement.ents:
                            if ent.label_ == "PERSON":
                                self.user_name = ent.text
                        if self.user_name:
                            self.get_templates()
                            intent = self.get_intent(statement)
                            if intent == "ask_name":
                                print(f'{self.get_bot_response(intent)}\n')
                            intent = "ask_name_2"
                        else:
                            print(f'{self.get_bot_response(intent)}')
                            continue
                    else:
                        intent = self.get_intent(statement)
                elif intent == "ask_name_2":
                    intent = self.get_intent(statement)
                    if statement._.blob.polarity >= 0:
                        print(f'{self.get_bot_response("user_positive")}\n')
                    else:
                        print(f'{self.get_bot_response("user_negative")}\n')
                    if intent == "ask_well_being":
                        print(f'{self.get_bot_response(intent)}\n')
                    intent = "display_menu"

                # ------------------ end state greetings ------------------>

                # <------------------ begin state interaction ------------------

                elif intent == "search_flights":
                    for ent in statement.ents:
                        if ent.text.lower() in airport_pt_cities or ent.label_ == "GPE":
                            self.city_departure = ent.text
                    if self.city_departure:
                        intent = "city_arrival"
                    else:
                        print(f'{self.get_bot_response("default")}')
                        continue
                elif intent == "city_arrival":
                    for ent in statement.ents:
                        if ent.text.lower() in airport_pt_cities or ent.label_ == "GPE":
                            self.city_arrival = ent.text
                    if self.city_arrival:
                        intent = "flight_day"
                    else:
                        print(f'{self.get_bot_response("default")}')
                        continue
                elif intent == "flight_day":
                    try:
                        self.flight_day = self.sutime.parse(
                            str(statement))[0]["timex-value"]
                        today = datetime.date.today()
                        if len(self.flight_day.split('-')) == 1:
                            self.flight_day += f"-{today.month}-{today.day}"
                        elif len(self.flight_day.split('-')) == 2:
                            self.flight_day += f"-{today.day}"
                    except:
                        print(f'{self.get_bot_response("default")}')
                        continue
                    if self.flight_day:
                        print(
                            f"Searching for flights from {self.city_departure} to {self.city_arrival} at {self.flight_day} ...")
                        # Call Flights API
                        self.fs.print_offers(self.fs.search_offers(
                            self.city_departure, self.city_arrival, self.flight_day))

                        self.city_departure = None
                        self.city_arrival = None
                        self.flight_day = None
                        intent = "display_menu"
                    else:
                        print(f'{self.get_bot_response("default")}')
                    continue
                elif intent == "place_info":
                    city_to_search = None
                    for ent in statement.ents:
                        if ent.text.lower() in pt_cities or ent.label_ == "GPE":
                            city_to_search = ent.text
                    if city_to_search:
                        # Call Places Info API
                        self.pi.print_attractions(city_to_search, self.pi.get_attractions(city_to_search))
                        intent = "display_menu"
                    else:
                        print(f'{self.get_bot_response("default")}')
                    continue

                # ------------------ end state interaction ------------------>

                # <------------------ begin state farewell ------------------

                elif intent == "farewell":
                    curr_intent = self.get_intent(statement)
                    if (curr_intent == "affirm"):
                        intent = "give_rate"
                    elif (curr_intent == "deny"):
                        intent = "goodbye"
                    else:
                        print(self.get_bot_response("default"))
                        continue
                elif intent == "give_rate":
                    numbers = list(statement._.numerize().values())
                    if len(numbers) == 0:
                        print(self.get_bot_response("default"))
                        continue
                    else:
                        try:
                            rating = float(numbers[0])
                            if 0 < rating < 5:
                                print(
                                    f"You rated the experience: {rating} out of 5. Thank you for your time {self.user_name}!\n")
                                intent = "general_opinion"
                            else:
                                print("Please rate only from one to five!")
                                continue
                        except:
                            print(self.get_bot_response("default"))
                            continue
                elif intent == "general_opinion":
                    curr_intent = self.get_intent(statement)
                    if (curr_intent == "affirm"):
                        intent = "give_opinion"
                    elif (curr_intent == "deny"):
                        intent = "goodbye"
                    else:
                        print(self.get_bot_response("default"))
                        continue
                elif intent == "give_opinion":
                    if statement._.blob.polarity >= 0:
                        print(f'{self.get_bot_response("experience_positive")}\n')
                    else:
                        print(f'{self.get_bot_response("experience_negative")}\n')
                    intent = "goodbye"

                # ------------------ end state farewell ------------------>
                else:
                    # find cities in the statement and remove them from it
                    # so the statement matches better with the dataset of intents
                    cities_in_statement = []
                    for ent in statement.ents:
                        if ent.text.lower() in pt_cities or ent.label_ == "GPE":
                            cities_in_statement.append(ent.text)
                            statement = self.nlp(
                                statement.text.replace(ent.text, ''))
                    
                    intent = self.get_intent(statement)

                    if intent == "place_info":
                        if cities_in_statement:
                            # Call Places Info API
                            self.pi.print_attractions(
                                cities_in_statement[0], self.pi.get_attractions(cities_in_statement[0]))

                            intent = "display_menu"
                            continue
                    elif intent == "search_flights":
                        if len(cities_in_statement) == 2:
                            self.city_departure = cities_in_statement[0]
                            self.city_arrival = cities_in_statement[1]
                            try:
                                self.flight_day = self.sutime.parse(
                                    str(statement))[0]["timex-value"]
                                today = datetime.date.today()
                                if len(self.flight_day.split('-')) == 1:
                                    self.flight_day += f"-{today.month}-{today.day}"
                                elif len(self.flight_day.split('-')) == 2:
                                    self.flight_day += f"-{today.day}"
                            except:
                                self.flight_day = None
                            if self.flight_day:
                                print(
                                    f"Searching for flights from {self.city_departure} to {self.city_arrival} at {self.flight_day} ...")
                                # Call Flights API
                                self.fs.print_offers(self.fs.search_offers(
                                    self.city_departure, self.city_arrival, self.flight_day))

                                self.city_departure = None
                                self.city_arrival = None
                                self.flight_day = None
                                intent = "display_menu"
                                continue
                            else:
                                intent = "flight_day"

                print(self.get_bot_response(intent, statement=statement))

                # terminate program
                if intent == "goodbye":
                    print()
                    exit(0)

            except(KeyboardInterrupt, EOFError, SystemExit):
                break

    
    def process_intent_dataset(self):
        for intent, examples in data.items():
            for example in examples:
                self.intent_nlp[intent].append(self.nlp(example))


    def get_intent(self, statement):
        if statement.text == '' or not statement.vector_norm:
            return None

        max_similarity = 0
        final_intent = None

        for intent, proc_examples in self.intent_nlp.items():
            for example in proc_examples:
                similarity = example.similarity(statement)

                if max_similarity < similarity:
                    max_similarity = similarity
                    final_intent = intent

        if max_similarity < self.min_similarity:
            return None

        return final_intent

    def get_bot_response(self, intent, statement=None):
        if intent not in list(response_map):
            if statement:
                return self.chatterbot.get_response(text=statement)
            else:
                intent = "default"

        return random.choice(self.templates[response_map[intent]])

    def get_templates(self):
        user_name_text = ' ' + self.user_name if self.user_name else ''
        bot_name_text = ' ' + self.bot_name if self.bot_name else ''

        self.templates = {
            "utter_greet": [
                f"Hey there{user_name_text}!{' First I need to know, what is your name?' if not self.user_name else ''}",
                f"Hi{user_name_text}!{' First I need to know, what is your name?' if not self.user_name else ''}",
                f"Hello{user_name_text}!{' How can I call you?' if not self.user_name else ''}",
            ],
            "utter_ask_name": [
                f"My name is{bot_name_text}.{' What about yours?' if self.user_name == 0 else ''}",
            ],
            "utter_ask_name_2": [
                f"Nice to meet you{user_name_text}! How are you doing?",
                f"Pleasure to meet you{user_name_text}! How are you feeling today?",
                f"Nice to meet you{user_name_text}! How are you today?",
            ],
            "utter_ask_well_being": [
                "I am fine! Thanks for asking!",
                "I am doing great! Thanks for asking!",
                "I am feeling good! Thanks for asking!",
            ],
            "utter_user_negative": [
                "Hope you feel better soon!",
                "Oh! You'll feel better soon.",
                "Thats too bad :( Hope you feel better soon!",
            ],
            "utter_user_positive": [
                f"I am glad your fine{user_name_text}!",
                "Great!",
                "Awesome!",
                f"Glad to hear that{user_name_text}!",
                f"Happy to hear that{user_name_text}!",
            ],
            "utter_display_menu": [
                "Here's what I can do for you:\
                    \n - Provide available flights from a given city to another.\
                    \n - Give you a list of the main attractions in a city of your choice.\
                    \n - Advise you with key information for you to have safe flight travels."
            ],
            "utter_ask_rate": [
                f"Wait! Before you go {self.user_name}, could you rate your experience?",
                f"Wait! Before you go {self.user_name}, could you rate your experience? It would really help us improve.",
            ],
            "utter_give_rate": [
                "Awesome! On a scale from one to five, what would you rate this experience?",
                "Great! On a scale from one to five, what would you rate this experience?",
                "Thank you! On a scale from one to five, what would you rate this experience?",
            ],
            "utter_give_opinion": [
                "Thanks! Describe in a few words your experience with us!",
            ],
            "utter_general_opinion": [
                "One last thing I promise! Could you also give us a general opinion about the experience?",
            ],
            "utter_experience_negative": [
                f"We're sorry for your experience{user_name_text}. We promise we will do better next time!",
            ],
            "utter_experience_positive": [
                f"Thank you! I am glad to hear that{user_name_text}!",
                f"Great{user_name_text}! Glad you liked it!",
                f"Awesome{user_name_text}! Glad I could help! Thank your for your time!",
                f"Nice{user_name_text}! Thank your for your time!",
            ],
            "utter_goodbye": [
                f"Bye bye{user_name_text}!",
                "Hope to see you later!",
                f"Goodbye{user_name_text}!",
                f"See ya{user_name_text}!",
            ],
            "utter_default": [
                "Sorry, I didn't quite follow.",
                "Sorry, I didn't understand.",
                "Sorry, can you rephrase please.",
            ],
            "utter_search_flights": [
                "Before doing a search I need to know your location or the city of departure.",
                "What is the departure city?"
            ],
            "utter_city_arrival": [
                "What is the destination city?",
                "What is the city you would like to go?"
            ],
            "utter_search_flights_day": [
                "Tell me just one more thing. What is the day of the flight?",
                "What is the day of the flight departure?"
            ],
            "utter_safety_menu": [
                "I can give you some advises about safe travels, such as:\
                    \n - What you can bring on your luggage.\
                    \n - What you can bring on your hand luggage.\
                    \n - Prohibited items to take on a flight.\
                    \n - Smoking regulations.\
                    \n - Procedure to take if you have any forbidden item.",
            ],
            "utter_hold_luggage": [
                "You may not transport any explosive and/or incendiary devices/materials/substances in hold baggage."
            ],
            "utter_hand_luggage": [
                "Passengers are prohibited from carrying any type of weapon or tool, objects with sharp points or edges or substances classified as hazardous in restricted security areas and aboard the aircraft."
            ],
            "utter_prohibited_items": [
                "Here's a list of the items that are prohibited to take to a flight:\
                \n - Pistols, firearms or any other devices that can shoot projectiles.\
                \n - Metal or plastic toy guns/replicas, including water pistols.\
                \n - Slingshots, darts or sports clubs or bats.\
                \n - Objects with sharp points or edges, such as razors, knives, scissors and other objects with sharp blades over 6cm in length, syringes (except with medical prescription).\
                \n - Work tools.\
                \n - Fireworks, flammable liquids or solids.\
                \n - Bleach, acids and poisons.\
                \n - Objects containing compressed air or gas."
            ],
            "utter_smoker": [
                "Smoking in the plane and at the airport is absolutely forbidden.\
                    \nYou may only smoke in designated areas. However, tobacco can be carried in your hand baggage.\n\
                    \nAt the security checkpoint, any lighters or electronic cigarettes being carried in the hand baggage must be inside an authorised transparent plastic bag.\n\
                    \nPlease note that you are not allowed to use electronic cigarettes aboard the aircraft."
            ],
            "utter_procedure": [
                "In the situation where you have a prohibited item with you, you can go back and hand the prohibited or restricted item to a family member or friend, check it in as baggage, if permitted, or send it by green mail, at the post located next to the security checkpoint."
            ],
            "utter_place_info": [
                f"Ok no problem!\nJust tell me one thing {self.user_name}, what is the city you with to know more about?"
            ]
        }


if __name__ == "__main__":
    ChatBotWrapper().start()
