import datetime
import json
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from langchain.schema import HumanMessage, SystemMessage, AIMessage

from .db_session import SqlAlchemyBase


class Game(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'games'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    messages = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def make_new(self, id):
        self.id = id
        self.messages = json.dumps({"messages": [1,
                                                 "Ты ведущий игры Dungeon and Dragons, твоя задача выдавать роли и придумывать игровую историю для участников игры."]})

    @property
    def message_list(self):
        message_list = []
        for message in json.loads(self.messages)["messages"]:
            if message[0] == "1":
                message_list.append(SystemMessage(content=message[1]))
            elif message[0] == "2":
                message_list.append(HumanMessage(content=message[1]))
            else:
                message_list.append(AIMessage(content=message[1]))

        return message_list

    def add_message(self, cur_message):
        message_list = self.message_list
        message_list.append(cur_message)
        balanced_message_list = []
        for message in message_list:
            if type(message) == HumanMessage:
                balanced_message_list.append(["2", message.content])
            elif type(message) == SystemMessage:
                balanced_message_list.append(["1", message.content])
            else:
                balanced_message_list.append(["3", message.content])

        self.messages = json.dumps({"messages": balanced_message_list})
