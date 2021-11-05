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
        self.sharedAccount: int = 0
        self.memberList = []
        self.currency = '₽'

    def set_currency(self, currency):
        if currency == 'ruble':
            self.currency = '₽'
        elif currency == 'dollar':
            self.currency = '$'
        elif currency == 'euro':
            self.currency = '€'

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
        self.in_session = False
        self.opened_session = None

    def add_chill_session(self, userid, name):
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

    def new_session(self, message):
        self.chillSessionsHandler.add_user(message.from_user.id)
        name_of_session = message.text
        bot.send_message(message.from_user.id, 'Thanks! Recommendation: set currency if needed')
        self.chillSessionsHandler.add_chill_session(message.from_user.id, name_of_session)

    def delete_session(self, message):
        name_of_session = message.text
        if message.from_user.id not in self.chillSessionsHandler.useridToChillSessions.keys():
            bot.send_message(message.from_user.id, 'this session does not exist')
        elif not self.chillSessionsHandler.chill_session_exists(message.from_user.id, name_of_session):
            bot.send_message(message.from_user.id, 'this session does not exist')
        else:
            self.chillSessionsHandler.delete_chill_session(message.from_user.id, name_of_session)
            bot.send_message(message.from_user.id, 'The session \"' + name_of_session + '\" was deleted successfully!')

    def set_opened_session(self, session):
        self.chillSessionsHandler.opened_session = session

    def open_session(self, message):
        name_of_session = message.text
        if message.from_user.id not in self.chillSessionsHandler.useridToChillSessions.keys():
            bot.send_message(message.from_user.id, 'this session does not exist')
        elif not self.chillSessionsHandler.chill_session_exists(message.from_user.id, name_of_session):
            bot.send_message(message.from_user.id, 'this session does not exist')
        else:
            ind = self.chillSessionsHandler.chill_session_index(message.from_user.id, name_of_session)
            self.set_opened_session(self.chillSessionsHandler.useridToChillSessions[message.from_user.id][ind])
            self.chillSessionsHandler.in_session = True
            bot.send_message(message.from_user.id, 'You are in the session \"' +
                             self.chillSessionsHandler.opened_session.name +
                             '\"!\nList of available commands:\n/exit_session\n/add_expenses\n/show_expenses\n'
                             '/change_currency\n/delete_member\n')

    def exit_session(self, message):
        self.set_opened_session(None)
        self.chillSessionsHandler.in_session = False
        bot.send_message(message.from_user.id, 'You have exited the session successfully! List of available commands:\n'
                                               '/new_session\n/list_of_sessions\n/delete_session\n/open_session\n')

    def add_expenses_3(self, message):
        amount = message.text.split('.')
        if len(amount) == 1:
            amount = message.text.split(',')
            if len(amount) == 1:
                wrong_format = False
                for i in range(len(amount[0])):
                    if not str(amount[0][i]).isdigit():
                        wrong_format = True
                        break
                if wrong_format:
                    bot.send_message(message.from_user.id, 'wrong format! try again!')
                else:
                    ind = self.chillSessionsHandler.chill_session_index(
                        message.from_user.id, communication.chillSessionsHandler.opened_session.name)
                    self.chillSessionsHandler.useridToChillSessions[message.from_user.id][ind]. \
                        add_to_shared_account(int(amount[0]))
                    bot.send_message(message.from_user.id, amount[0] +
                                     communication.chillSessionsHandler.opened_session.currency +
                                     ' was added to the shared account!')
        else:
            bot.send_message(message.from_user.id, 'wrong format! try again!')

    def add_expenses_2(self, message, name):
        amount = message.text.split('.')
        if len(amount) == 1:
            amount = message.text.split(',')
            if len(amount) == 1:
                wrong_format = False
                for i in range(len(amount[0])):
                    if not str(amount[0][i]).isdigit():
                        wrong_format = True
                        break
                if wrong_format:
                    bot.send_message(message.from_user.id, 'wrong format! try again!')
                else:
                    ind = self.chillSessionsHandler.chill_session_index(
                        message.from_user.id, communication.chillSessionsHandler.opened_session.name)
                    if not self.chillSessionsHandler.useridToChillSessions[message.from_user.id][ind]. \
                            member_exists(name):
                        self.chillSessionsHandler.useridToChillSessions[message.from_user.id][ind].add_member(name)
                    self.chillSessionsHandler.useridToChillSessions[message.from_user.id][ind]. \
                        add_to_personal_account(name, int(amount[0]))
                    bot.send_message(message.from_user.id, amount[0] +
                                     communication.chillSessionsHandler.opened_session.currency +
                                     ' was added to ' + name + '\'s account!')
        else:
            bot.send_message(message.from_user.id, 'wrong format! try again!')

    @staticmethod
    def add_expenses_1(message):
        name = message.text
        bot.send_message(message.from_user.id, 'amount:')
        bot.register_next_step_handler(message, communication.add_expenses_2, name)

    @staticmethod
    def add_expenses_0(message):
        to_personal_account = message.text.lower()
        if to_personal_account == 'y' or to_personal_account == 'yes':
            bot.send_message(message.from_user.id, 'name:')
            bot.register_next_step_handler(message, communication.add_expenses_1)
        elif to_personal_account == 'n' or to_personal_account == 'no':
            bot.send_message(message.from_user.id, 'amount:')
            bot.register_next_step_handler(message, communication.add_expenses_3)
        else:
            bot.send_message(message.from_user.id, 'Wrong format! Try Again!')

    def delete_member(self, message):
        name = message.text
        ind = self.chillSessionsHandler.chill_session_index(
            message.from_user.id, communication.chillSessionsHandler.opened_session.name)
        if self.chillSessionsHandler.useridToChillSessions[message.from_user.id][ind].member_exists(name):
            member_index = self.chillSessionsHandler.useridToChillSessions[message.from_user.id][ind].member_index(name)
            self.chillSessionsHandler.useridToChillSessions[message.from_user.id][ind]. \
                add_to_shared_account(communication.chillSessionsHandler.opened_session.
                                      memberList[member_index].account)
            self.chillSessionsHandler.useridToChillSessions[message.from_user.id][ind].delete_member(name)
            bot.send_message(message.from_user.id, 'The money from ' + name + '\'s account was shared!')
        else:
            bot.send_message(message.from_user.id, 'This member does not exist!')

    def set_currency(self, message):
        if message.text.lower() == 'ruble' or message.text.lower() == 'rub' or message.text.lower() == '₽' or message.text.lower() == 'r':
            ind = self.chillSessionsHandler.chill_session_index(
                message.from_user.id, communication.chillSessionsHandler.opened_session.name)
            self.chillSessionsHandler.useridToChillSessions[message.from_user.id][ind].set_currency('ruble')
            bot.send_message(message.from_user.id, 'The currency is ₽ now!')
        elif message.text.lower() == 'dollar' or message.text.lower() == '$' or message.text.lower() == 'd':
            ind = self.chillSessionsHandler.chill_session_index(
                message.from_user.id, communication.chillSessionsHandler.opened_session.name)
            self.chillSessionsHandler.useridToChillSessions[message.from_user.id][ind].set_currency('dollar')
            bot.send_message(message.from_user.id, 'The currency is $ now!')
        elif message.text.lower() == 'euro' or message.text.lower() == '€' or message.text.lower() == 'e':
            ind = self.chillSessionsHandler.chill_session_index(
                message.from_user.id, communication.chillSessionsHandler.opened_session.name)
            self.chillSessionsHandler.useridToChillSessions[message.from_user.id][ind].set_currency('euro')
            bot.send_message(message.from_user.id, 'The currency is € now!')
        else:
            bot.send_message(message.from_user.id, 'Wrong format! Try Again!')


communication = Communication()


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '/help':
        if communication.chillSessionsHandler.in_session:
            bot.send_message(message.from_user.id, 'You are in session! List of available commands:\n'
                                                   '/exit_session\n'
                                                   '/add_expenses\n'
                                                   '/show_expenses\n'
                                                   '/change_currency\n'
                                                   '/delete_member\n'
                             )
        else:
            bot.send_message(message.from_user.id, 'List of available commands:\n'
                                                   '/new_session\n'
                                                   '/list_of_sessions\n'
                                                   '/delete_session\n'
                                                   '/open_session\n'
                             )
    elif message.text == '/start':
        bot.send_message(message.from_user.id, 'Hello! Here you can manage your expenses if you spend your money with '
                                               'your friends! Try /help for more details')
    elif message.text == '/new_session':
        if communication.chillSessionsHandler.in_session:
            bot.send_message(message.from_user.id, 'You cannot use this command inside the session')
        else:
            bot.send_message(message.from_user.id, 'name:')
            bot.register_next_step_handler(message, communication.new_session)
    elif message.text == '/list_of_sessions':
        if communication.chillSessionsHandler.in_session:
            bot.send_message(message.from_user.id, 'You cannot use this command inside the session')
        else:
            if message.from_user.id in communication.chillSessionsHandler.useridToChillSessions.keys() and \
                    len(communication.chillSessionsHandler.useridToChillSessions[message.from_user.id]) > 0:
                bot.send_message(message.from_user.id, 'You have ' +
                                 str(len(communication.chillSessionsHandler.
                                         useridToChillSessions[message.from_user.id])) + ' sessions\n')
                name = ''
                for i in range(len(communication.chillSessionsHandler.useridToChillSessions[message.from_user.id])):
                    name += communication.chillSessionsHandler.useridToChillSessions[message.from_user.id][i].name
                    name += '\n'
                bot.send_message(message.from_user.id, name)
            else:
                bot.send_message(message.from_user.id, 'You have no chill session')
    elif message.text == '/delete_session':
        if communication.chillSessionsHandler.in_session:
            bot.send_message(message.from_user.id, 'You cannot use this command inside the session')
        else:
            bot.send_message(message.from_user.id, 'name:')
            bot.register_next_step_handler(message, communication.delete_session)
    elif message.text == '/open_session':
        if communication.chillSessionsHandler.in_session:
            bot.send_message(message.from_user.id, 'You cannot use this command inside the session')
        else:
            bot.send_message(message.from_user.id, 'name:')
            bot.register_next_step_handler(message, communication.open_session)
    elif message.text == '/exit_session':
        if not communication.chillSessionsHandler.in_session:
            bot.send_message(message.from_user.id, 'You are not inside a session')
        else:
            communication.exit_session(message)
    elif message.text == '/add_expenses':
        if not communication.chillSessionsHandler.in_session:
            bot.send_message(message.from_user.id, 'You are not inside a session')
        else:
            bot.send_message(message.from_user.id, 'to personal account? (yes/no)')
            bot.register_next_step_handler(message, communication.add_expenses_0)
    elif message.text == '/show_expenses':
        if not communication.chillSessionsHandler.in_session:
            bot.send_message(message.from_user.id, 'You are not inside a session')
        else:
            list_of_expenses = ''
            if communication.chillSessionsHandler.opened_session.sharedAccount == 0 and \
                    len(communication.chillSessionsHandler.opened_session.memberList) == 0:
                list_of_expenses += 'You did not have expenses yet!'
            elif communication.chillSessionsHandler.opened_session.sharedAccount != 0:
                list_of_expenses += 'List of expenses:\nShared account: '
                list_of_expenses += str(communication.chillSessionsHandler.opened_session.sharedAccount)
                list_of_expenses += communication.chillSessionsHandler.opened_session.currency + '\n'
            for i in range(len(communication.chillSessionsHandler.opened_session.memberList)):
                list_of_expenses += communication.chillSessionsHandler.opened_session.memberList[i].name
                list_of_expenses += ': '
                list_of_expenses += str(communication.chillSessionsHandler.opened_session.memberList[i].account) + \
                    communication.chillSessionsHandler.opened_session.currency
                list_of_expenses += '\n'
            bot.send_message(message.from_user.id, list_of_expenses)
    elif message.text == '/change_currency':
        bot.send_message(message.from_user.id, 'currency: (ruble/dollar/euro)')
        bot.register_next_step_handler(message, communication.set_currency)
    elif message.text == '/delete_member':
        if not communication.chillSessionsHandler.in_session:
            bot.send_message(message.from_user.id, 'You are not inside a session')
        else:
            bot.send_message(message.from_user.id, 'name:')
            bot.register_next_step_handler(message, communication.delete_member)
    else:
        bot.send_message(message.from_user.id, 'try \'/help\'')


bot.polling(none_stop=True, interval=0)
