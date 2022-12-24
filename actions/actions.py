from typing import Any, Text, Dict, List

import json
import random
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

with open('data/database.json', 'r', encoding='utf8') as f:
    data = json.load(f)

GET_PART = None
GET_EATING = None
THRESHOLD = 0.8


class ActionAdvice(Action):

    def name(self) -> Text:
        return "action_advice"

    def run(self, dispatcher: "CollectingDispatcher",
            tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global GET_PART
        conf = tracker.latest_message['intent']['confidence']

        if conf < THRESHOLD:
            dispatcher.utter_message(text='Tôi không hiểu!')
            return []

        get_part = next(tracker.get_latest_entity_values(
            "parts"), None).lower()
        GET_PART = get_part
        
        food_parts = "\n".join(data[0][get_part])
        mgs = f"Bạn cảm thấy đau {get_part}, vậy bạn muốn ăn loại thực phảm nào?\n{food_parts}"
        dispatcher.utter_message(text=mgs)

        return []


class ActionFoodAdvice(Action):

    def name(self) -> Text:
        return "action_food_advice"

    def run(self, dispatcher: "CollectingDispatcher",
            tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        global GET_EATING
        conf = tracker.latest_message['intent']['confidence']
        if conf < THRESHOLD:
            dispatcher.utter_message(text='Tôi không hiểu!')
            return []

        get_food = next(tracker.get_latest_entity_values("food"), None)
        dispatcher.utter_message(get_food)
        if GET_PART:
            if get_food in data[0][GET_PART]:
                food = random.choice(data[1][get_food])
                GET_EATING = food
                msg = f"Đây là một món ăn từ {get_food} bạn có thể tham khảo:\n{food}\n Món này rất tốt cho {GET_PART} đó nha <3"
                dispatcher.utter_message(text=msg)
            else:
                dispatcher.utter_message(
                    text="Xin lỗi bạn không ăn được món này đâu nhé! Hãy chọn món khác.")
        else:
            dispatcher.utter_message(text=f"Bạn bị sao mà muốn ăn {get_food}?")
            dispatcher.utter_message(
                text=f"Hãy cho tôi biết để tôi đề xuất những món phù hợp với sức khỏe của bạn <3")

        return []


class ActionSearchFood(Action):

    def name(self) -> Text:
        return "action_search_food"

    def run(self, dispatcher: "CollectingDispatcher",
            tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        conf = tracker.latest_message['intent']['confidence']

        if conf < THRESHOLD:
            dispatcher.utter_message(text='Tôi không hiểu!')
            return []

        get_eating = next(tracker.get_latest_entity_values("eating"), None)
        food = get_eating if get_eating != None else GET_EATING
        text = f"Cách+làm+{food.replace(' ', '+')}+ngon"
        dispatcher.utter_message(
            f"Đây là các cách nấu {food}: https://www.youtube.com/results?search_query={text}")
        return []


class ValidateNameForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_name_form"

    def validate_name(self, slot_value, dispatcher: CollectingDispatcher,
                      tracker: Tracker,
                      domain: DomainDict):

        print(slot_value)
        return {"name": slot_value}


class ActionName(Action):

    def name(self) -> Text:
        return "action_name"

    def run(self, dispatcher: "CollectingDispatcher", 
            tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:
        
        get_name = tracker.get_slot(key="name")
        if get_name == None:
            dispatcher.utter_message(text="Tôi không biết, bạn có thể cho tôi biết tên bạn được không?")
        else:
            dispatcher.utter_message(text=f"Bạn là {get_name}!")
        return []
