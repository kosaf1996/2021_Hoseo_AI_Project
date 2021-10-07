import json
class User:
    def __init__(self):
        self.__name = 'unknown'
        self.__age = -1
        self.__work = 'unknown'

class Supervisor(User):
    def __init__(self):
        self.__name = 'gu gyoung min'
        self.__age = 26
        self.__work = 'studunt'

    def pay(self,a , b):
        return self.__name,a * b


class Employee(User):
    def __init__(self):
        self.__name = 'lina'
        self.__age = 29
        self.__work = 'studunt'

    def work(self,day,overtime):
        return self.__name,(day * 8300 * 8) + (overtime * 1700)



S =Supervisor().pay(20,12000)
E = Employee().work(10,3)

li =[S,E]
with open('input.txt','w') as fp:
    for i in li:
        json.dump(i,fp)

