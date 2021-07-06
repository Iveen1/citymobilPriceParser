import sqlite3

class BotDB:
    def __init__(self):
        self.db = sqlite3.connect('db.db')
        self.sql = self.db.cursor()


    def showTable(self): # Метод для возвращения всех активных маршрутов
        self.sql.execute(f"SELECT * FROM routes WHERE active = 1")
        return self.sql.fetchall()


    def checkUser(self, userData: list, register = False): # Метод для проверки наличия пользователя в БД
        self.login = userData[0]
        self.firstName = userData[1]
        self.lastName = userData[2]
        self.userId = userData[3]

        self.sql.execute(f"SELECT tm_userId FROM users WHERE tm_userId = '{self.userId}'")
        self.user = self.sql.fetchone()

        if self.user is None and register == True: # Если пользователя нет в БД и при этом мы вызывали функцию для возможной регистрации, то добавляем пользователя в БД
            self.newUser(self.login, self.firstName, self.lastName, self.userId)
            return

        elif self.user != None: # Если пользователь в БД, то возвращаем строку из БД
            return self.user

        else: # Пользователя нет в БД, не регистрируем его
            return None


    def newUser(self, login: int, firstName: str, lastName: str, userId: int): # Метод добавления нового юзера в БД
        self.sql.execute(f"INSERT INTO users (tm_login, tm_firstName, tm_lastName, tm_userId) VALUES (?, ?, ?, ?)",(login, firstName, lastName, userId))
        self.db.commit()
        return f'New user: {userId}'


    def findUser(self, userId: int): # Метод для поиска и возвращения строки со всеми данными пользователя из БД
        self.sql.execute(f"SELECT * FROM users WHERE tm_userId = '{userId}'")
        return self.sql.fetchone()


    def findUserByFK(self, fkId: int):
        self.sql.execute(f"SELECT * FROM users WHERE id = '{fkId}'")
        return self.sql.fetchone()


    def findUserFKbyUserId(self, userId):
        return self.findUser(userId)[0]


    def insertRoute(self, userId: int, latitude: float, longitude: float, type: str):
        self.fk = self.findUserFKbyUserId(userId)

        self.sql.execute(f"SELECT * FROM routes WHERE fk_user_id = '{self.fk}'")
        self.fetch = self.sql.fetchone()

        if self.fetch is None:
            self.sql.execute(f"INSERT INTO routes (fk_user_id, {type}_latitude, {type}_longitude) VALUES (?, ?, ?)", (self.fk, latitude, longitude))
            self.db.commit()
        if self.fetch is not None:
            self.sql.execute(f"UPDATE routes SET ({type}_latitude, {type}_longitude) = ({latitude}, {longitude}) WHERE fk_user_id = '{self.fk}'")
            self.db.commit()


    def updateCurrentPrice(self, fk_user_id: int, current_price: int):
        self.sql.execute(f"UPDATE routes SET (current_price) = ({current_price}) WHERE fk_user_id = '{fk_user_id}'")
        self.db.commit()


    def insertRequestPrice(self, userId, price):
        self.fk = self.findUserFKbyUserId(userId)

        self.sql.execute(f"UPDATE routes SET (request_price, active) = ({price}, {True}) WHERE fk_user_id = '{self.fk}'")
        self.db.commit()


    def stopSubInformer(self, fk_user_id: int):
        self.sql.execute( f"UPDATE routes SET (active) = ({False}) WHERE fk_user_id = '{fk_user_id}'")
        self.db.commit()


    def getRouteData(self, userId: int):
        self.fk = self.findUserFKbyUserId(userId)
        self.sql.execute(f"SELECT * FROM routes WHERE fk_user_id = '{self.fk}'")
        return self.sql.fetchone()

#
