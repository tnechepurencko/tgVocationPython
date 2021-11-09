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

    def get_keys(self):
        return self.useridToChillSessions.keys()

    def add_chill_session(self, userid, name):
        chill_session = ChillSession(name)
        self.useridToChillSessions[userid].append(chill_session)

    def add_user(self, userid):
        if userid not in self.useridToChillSessions:
            chill_sessions = []
            self.useridToChillSessions[userid] = chill_sessions

    def session_exists(self, userid, name):
        for c in self.useridToChillSessions[userid]:
            if c.name == name:
                return True
        return False

    def session_index(self, userid, name):
        for i in range(len(self.useridToChillSessions[userid])):
            if self.useridToChillSessions[userid][i].name == name:
                return i
        return -1

    def delete_chill_session(self, userid, name):
        if self.session_exists(userid, name):
            self.useridToChillSessions[userid].pop(self.session_index(userid, name))


class Communication:
    def __init__(self):
        self.chillSessionsHandler = ChillSessionsHandler()

    def get_member(self, member_index):
        return self.chillSessionsHandler.opened_session.memberList[member_index]

    def get_member_list(self):
        return self.chillSessionsHandler.opened_session.memberList

    def get_session_list(self, user_id):
        return self.chillSessionsHandler.useridToChillSessions[user_id]

    def get_session(self, user_id, session_index):
        return self.chillSessionsHandler.useridToChillSessions[user_id][session_index]

    def opened_session_name(self):
        return self.chillSessionsHandler.opened_session.name

    def create_new_session(self, message):
        self.chillSessionsHandler.add_user(message.from_user.id)
        name_of_session = message.text
        text = 'Thanks! Recommendation: set currency if needed'
        bot.send_message(message.from_user.id, text)
        self.chillSessionsHandler.add_chill_session(message.from_user.id, name_of_session)

    def delete_session(self, message):
        name_of_session = message.text
        if not self.session_exists(message):
            text = 'This session does not exist!'
            bot.send_message(message.from_user.id, text)
        else:
            self.chillSessionsHandler.delete_chill_session(message.from_user.id, name_of_session)
            text = 'The session \"' + name_of_session + '\" was deleted successfully!'
            bot.send_message(message.from_user.id, text)

    def session_exists(self, message):
        return message.from_user.id in self.chillSessionsHandler.get_keys() and \
               self.chillSessionsHandler.session_exists(message.from_user.id, message.text)

    def set_opened_session(self, session):
        self.chillSessionsHandler.opened_session = session

    def open_session(self, message):
        name_of_session = message.text
        if not self.session_exists(message):
            text = 'This session does not exist!'
            bot.send_message(message.from_user.id, text)
        else:
            ind = self.chillSessionsHandler.session_index(message.from_user.id, name_of_session)
            self.set_opened_session(self.get_session(message.from_user.id, ind))
            self.chillSessionsHandler.in_session = True
            text = 'You are in the session \"' + self.opened_session_name() + \
                   '\"!\nList of available commands:\n/exit_session\n/add_expenses\n/show_expenses\n'\
                   '/change_currency\n/delete_member\n'
            bot.send_message(message.from_user.id, text)

    def exit_session(self, message):
        self.set_opened_session(None)
        self.chillSessionsHandler.in_session = False
        text = 'You have exited the session successfully! List of available commands:\n'\
               '/new_session\n/list_of_sessions\n/delete_session\n/open_session\n'
        bot.send_message(message.from_user.id, text)

    @staticmethod
    def wrong_format(message_text):
        amount = message_text.split('.')
        if len(amount) == 1:
            amount = message_text.split(',')
            if len(amount) == 1:
                wrong_format = False
                for i in range(len(amount[0])):
                    if not str(amount[0][i]).isdigit():
                        wrong_format = True
                        break
            else:
                wrong_format = False
        else:
            wrong_format = False
        return wrong_format, amount

    def add_shared_expenses(self, message):
        wrong_format, amount = self.wrong_format(message.text)
        if wrong_format:
            text = 'Wrong format! Try Again!'
            bot.send_message(message.from_user.id, text)
        else:
            ind = self.chillSessionsHandler.session_index(
                message.from_user.id, self.opened_session_name())
            self.get_session(message.from_user.id, ind).add_to_shared_account(int(amount[0]))
            text = amount[0] + self.chillSessionsHandler.opened_session.currency + \
                ' was added to the shared account!'
            bot.send_message(message.from_user.id, text)

    def add_personal_expenses(self, message, name):
        wrong_format, amount = self.wrong_format(message.text)
        if wrong_format:
            text = 'Wrong format! Try Again!'
            bot.send_message(message.from_user.id, text)
        else:
            ind = self.chillSessionsHandler.session_index(
                message.from_user.id, self.opened_session_name())
            if not self.get_session(message.from_user.id, ind).member_exists(name):
                self.get_session(message.from_user.id, ind).add_member(name)
            self.get_session(message.from_user.id, ind).add_to_personal_account(name, int(amount[0]))
            text = amount[0] + self.chillSessionsHandler.opened_session.currency + \
                ' was added to ' + name + '\'s account!'
            bot.send_message(message.from_user.id, text)

    def enter_amount(self, message):
        name = message.text
        bot.send_message(message.from_user.id, 'amount:')
        bot.register_next_step_handler(message, self.add_personal_expenses, name)

    def personal_or_shared(self, message):
        to_personal_account = message.text.lower()
        if to_personal_account == 'y' or to_personal_account == 'yes':
            bot.send_message(message.from_user.id, 'name:')
            bot.register_next_step_handler(message, self.enter_amount)
        elif to_personal_account == 'n' or to_personal_account == 'no':
            bot.send_message(message.from_user.id, 'amount:')
            bot.register_next_step_handler(message, self.add_shared_expenses)
        else:
            text = 'Wrong format! Try Again!'
            bot.send_message(message.from_user.id, text)

    def delete_member(self, message):
        name = message.text
        ind = self.chillSessionsHandler.session_index(message.from_user.id, self.opened_session_name())
        if self.get_session(message.from_user.id, ind).member_exists(name):
            member_index = self.get_session(message.from_user.id, ind).member_index(name)
            self.get_session(message.from_user.id, ind).add_to_shared_account(self.get_member(member_index).account)
            self.get_session(message.from_user.id, ind).delete_member(name)
            text = 'The money from ' + name + '\'s account was shared!'
            bot.send_message(message.from_user.id, text)
        else:
            text = 'This member does not exist!'
            bot.send_message(message.from_user.id, text)

    @staticmethod
    def is_ruble(message):
        return message.text.lower() == 'ruble' or message.text.lower() == 'rub' or message.text.lower() == '₽' or \
               message.text.lower() == 'r'

    @staticmethod
    def is_dollar(message):
        return message.text.lower() == 'dollar' or message.text.lower() == '$' or message.text.lower() == 'd'

    @staticmethod
    def is_euro(message):
        return message.text.lower() == 'euro' or message.text.lower() == '€' or message.text.lower() == 'e'

    def set_currency(self, message):
        if self.is_ruble(message):
            ind = self.chillSessionsHandler.session_index(message.from_user.id, self.opened_session_name())
            self.get_session(message.from_user.id, ind).set_currency('ruble')
            text = 'The currency is ₽ now!'
            bot.send_message(message.from_user.id, text)
        elif self.is_dollar(message):
            ind = self.chillSessionsHandler.session_index(message.from_user.id, self.opened_session_name())
            self.get_session(message.from_user.id, ind).set_currency('dollar')
            text = 'The currency is $ now!'
            bot.send_message(message.from_user.id, text)
        elif self.is_euro(message):
            ind = self.chillSessionsHandler.session_index(message.from_user.id, self.opened_session_name())
            self.get_session(message.from_user.id, ind).set_currency('euro')
            text = 'The currency is € now!'
            bot.send_message(message.from_user.id, text)
        else:
            text = 'Wrong format! Try Again!'
            bot.send_message(message.from_user.id, text)


class Commands:
    def __init__(self):
        self.communication = Communication()

    def help(self, message):
        if self.communication.chillSessionsHandler.in_session:
            text = '/exit_session\n/add_expenses\n/show_expenses\n/change_currency\n/delete_member\n'
            bot.send_message(message.from_user.id, 'You are in session! List of available commands:\n' + text)
        else:
            text = '/new_session\n/list_of_sessions\n/delete_session\n/open_session\n'
            bot.send_message(message.from_user.id, 'List of available commands:\n' + text)

    @staticmethod
    def start(message):
        text = 'Hello! Here you can manage your expenses if you spend your money with ' \
                'your friends! Try /help for more details'
        bot.send_message(message.from_user.id, text)

    def new_session(self, message):
        if self.communication.chillSessionsHandler.in_session:
            text = 'You cannot use this command inside the session!'
            bot.send_message(message.from_user.id, text)
        else:
            bot.send_message(message.from_user.id, 'name:')
            bot.register_next_step_handler(message, self.communication.create_new_session)

    def list_of_sessions(self, message):
        if self.communication.chillSessionsHandler.in_session:
            text = 'You cannot use this command inside the session!'
            bot.send_message(message.from_user.id, text)
        else:
            if message.from_user.id in self.communication.chillSessionsHandler.get_keys() and \
                    len(self.communication.get_session_list(message.from_user.id)) > 0:
                text = 'You have ' + str(len(self.communication.get_session_list(message.from_user.id))) + ' sessions\n'
                bot.send_message(message.from_user.id, text)
                name = ''
                for i in range(len(self.communication.get_session_list(message.from_user.id))):
                    name += self.communication.get_session(message.from_user.id, i).name
                    name += '\n'
                bot.send_message(message.from_user.id, name)
            else:
                text = 'You have no chill session!'
                bot.send_message(message.from_user.id, text)

    def delete_session(self, message):
        if self.communication.chillSessionsHandler.in_session:
            text = 'You cannot use this command inside the session!'
            bot.send_message(message.from_user.id, text)
        else:
            bot.send_message(message.from_user.id, 'name:')
            bot.register_next_step_handler(message, self.communication.delete_session)

    def open_session(self, message):
        if self.communication.chillSessionsHandler.in_session:
            text = 'You cannot use this command inside the session!'
            bot.send_message(message.from_user.id, text)
        else:
            bot.send_message(message.from_user.id, 'name:')
            bot.register_next_step_handler(message, self.communication.open_session)

    def exit_session(self, message):
        if not self.communication.chillSessionsHandler.in_session:
            text = 'You are not inside a session!'
            bot.send_message(message.from_user.id, text)
        else:
            self.communication.exit_session(message)

    def add_expenses(self, message):
        if not self.communication.chillSessionsHandler.in_session:
            text = 'You are not inside a session!'
            bot.send_message(message.from_user.id, text)
        else:
            text = 'To personal account? (yes/no)'
            bot.send_message(message.from_user.id, text)
            bot.register_next_step_handler(message, self.communication.personal_or_shared)

    def show_expenses(self, message):
        if not self.communication.chillSessionsHandler.in_session:
            text = 'You are not inside a session!'
            bot.send_message(message.from_user.id, text)
        else:
            list_of_expenses = ''
            lml = len(self.communication.get_member_list())
            shared_account = self.communication.chillSessionsHandler.opened_session.sharedAccount
            if shared_account == 0 and lml == 0:
                list_of_expenses += 'You did not have expenses yet!'
            elif shared_account != 0:
                list_of_expenses += 'List of expenses:\nShared account: '
                list_of_expenses += str(shared_account)
                list_of_expenses += self.communication.chillSessionsHandler.opened_session.currency + '\n'
            for i in range(lml):
                list_of_expenses += self.communication.get_member(i).name
                list_of_expenses += ': '
                list_of_expenses += str(self.communication.get_member(i).account) + \
                    self.communication.chillSessionsHandler.opened_session.currency
                list_of_expenses += '\n'
            bot.send_message(message.from_user.id, list_of_expenses)

    def change_currency(self, message):
        text = 'currency: (ruble/dollar/euro)'
        bot.send_message(message.from_user.id, text)
        bot.register_next_step_handler(message, self.communication.set_currency)

    def delete_member(self, message):
        if not self.communication.chillSessionsHandler.in_session:
            text = 'You are not inside a session!'
            bot.send_message(message.from_user.id, text)
        else:
            bot.send_message(message.from_user.id, 'name:')
            bot.register_next_step_handler(message, self.communication.delete_member)

    @staticmethod
    def default(message):
        bot.send_message(message.from_user.id, 'Try \'/help\'')


commands = Commands()


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '/help':
        commands.help(message)
    elif message.text == '/start':
        commands.start(message)
    elif message.text == '/new_session':
        commands.new_session(message)
    elif message.text == '/list_of_sessions':
        commands.list_of_sessions(message)
    elif message.text == '/delete_session':
        commands.delete_session(message)
    elif message.text == '/open_session':
        commands.open_session(message)
    elif message.text == '/exit_session':
        commands.exit_session(message)
    elif message.text == '/add_expenses':
        commands.add_expenses(message)
    elif message.text == '/show_expenses':
        commands.show_expenses(message)
    elif message.text == '/change_currency':
        commands.change_currency(message)
    elif message.text == '/delete_member':
        commands.delete_member(message)
    else:
        commands.default(message)


bot.polling(none_stop=True, interval=0)
