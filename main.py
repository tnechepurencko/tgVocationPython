import telebot

bot = telebot.TeleBot('1931778515:AAEDB-WOSq0oV2WCFzZ0NYV2CmXQGRSp8aQ')


class Person:
    def __init__(self, name):
        self.name = name
        self.account = 0

    def change_name(self, name):
        self.name = name

    def add_to_account(self, amount):
        self.account += amount


class ChillSession:
    def __init__(self, name):
        self.name = name
        self.sharedAccount = 0
        self.memberList = []

    def change_name(self, name):
        self.name = name

    def add_to_shared_account(self, amount):
        self.sharedAccount += amount

    def member_exists(self, name):
        for m in self.memberList:
            if m.name == name:
                return True
        return False

    def member_index(self, name):
        for i in range(len(self.memberList)):
            if self.memberList[i].name == name:
                return i
        return -1

    def add_to_personal_account(self, name, amount):
        if self.member_exists(name):
            self.memberList[self.member_index(name)].add_to_account(amount)

    def add_member(self, name):
        person = Person(name)
        self.memberList.append(person)

    def get_account_of(self, name):
        if self.member_exists(name):
            return self.memberList[self.member_index(name)].account + self.sharedAccount // len(self.memberList)
        return -1
        # TODO change an algo of money rounding

    def delete_member(self, name):
        if self.member_exists(name):
            self.memberList.pop(self.member_index(name))


class ChillSessionsHandler:
    def __init__(self):
        self.useridToChillSessions = dict()

    def add_chill_session(self, userid, name):
        # if userid not in self.useridToChillSessions.keys():
        #     self.useridToChillSessions[userid] = []
        chill_session = ChillSession(name)
        self.useridToChillSessions[userid].append(chill_session)

    def add_user(self, userid):
        if userid not in self.useridToChillSessions:
            chill_sessions = []
            self.useridToChillSessions[userid] = chill_sessions

    def chill_session_exists(self, userid, name):
        for c in self.useridToChillSessions[userid]:
            if c.name == name:
                return True
        return False

    def chill_session_index(self, userid, name):
        for i in range(len(self.useridToChillSessions[userid])):
            if self.useridToChillSessions[userid][i].name == name:
                return i
        return -1

    def delete_chill_session(self, userid, name):
        if self.chill_session_exists(userid, name):
            self.useridToChillSessions[userid].pop(self.chill_session_index(userid, name))


class Communication:
    def __init__(self):
        self.chillSessionsHandler = ChillSessionsHandler()

    def input_name_of_new_session(self, message):
        self.chillSessionsHandler.add_user(message.from_user.id)
        name_of_session = message.text
        bot.send_message(message.from_user.id, 'thanks')
        self.chillSessionsHandler.add_chill_session(message.from_user.id, name_of_session)


communication = Communication()


@bot.message_handler(content_types=['text'])  # получает
def get_text_messages(message):
    if message.text == '/help':
        bot.send_message(message.from_user.id, 'list of commands:\n'
                                               '/new_session\n'
                                               '/list_of_sessions\n')
    elif message.text == '/new_session':
        bot.send_message(message.from_user.id, 'name:')
        bot.register_next_step_handler(message, communication.input_name_of_new_session)
    elif message.text == '/list_of_sessions':
        if message.from_user.id in communication.chillSessionsHandler.useridToChillSessions.keys():
            name = ''
            for i in range(len(communication.chillSessionsHandler.useridToChillSessions[message.from_user.id])):
                name += communication.chillSessionsHandler.useridToChillSessions[message.from_user.id][i].name
                name += '\n'
            bot.send_message(message.from_user.id, name)
        else:
            bot.send_message(message.from_user.id, 'You have no chill session')
    else:
        bot.send_message(message.from_user.id, 'try \'/help\'')


bot.polling(none_stop=True, interval=0)
