#!/usr/bin/python
#-*- coding: utf-8 -*-

'''
GBMessage
view_id
user_id
seq
message
'''
import json

class GBMessage(): 
    def __init__(self, view_id = 0, action = "", user_id = "", seq = 0, message = ""):
        self.view_id = view_id
        self.user_id = user_id
        self.seq = seq
        self.action = action
        self.message = message
    def __encode__(self):
        m = {}
        m["view_id"] = self.view_id
        m["user_id"] = self.user_id
        m["seq"] = self.seq
        m["action"] = self.action
        m["message"] = self.message
        json_string = json.dumps(m)
        return json_string
    def __str__(self):
        return self.__encode__()
    def __decode__(self, message):
        g = json.loads(message)
        self.view_id = g["view_id"]
        self.user_id = g["user_id"]
        self.seq = g["seq"]
        self.action = g["action"]
        self.message = g["message"]
        return self
'''
ViewMessage
view id
UID, user_list, leader, AB/CBCAST Info

'''
class UserView():
    def __init__(self):
        self.UID = ""
        self.user_list = []
        self.leader = ""
        self.info = ""
    def __encode__(self):
        m = {}
        m["UID"] = self.UID
        m["user_list"] = self.user_list
        m["leader"] = self.leader
        m["info"] = self.info
        s = json.dumps(m)
        return s
    def __str__(self):
        return self.__encode__()
    def __decode__(self, message):
        s = json.loads(message)
        self.UID = s["UID"]
        self.user_list = s["user_list"]
        self.leader = s["leader"]
        self.info = s["info"]
        return self

class ViewMessage(): 
    def __init__(self, view_id = 0):
        self.view_id = view_id
        self.users_views = {}

    def add_user_view(self, user_view):
        self.users_views[user_view.UID] = user_view

    def __str__(self):
        self.__encode__()

    def __encode__(self):
        m = {}
        m["view_id"] = self.view_id

        temp = []
        for key in self.users_views:
            temp.append(uv_encode(self.users_views[key]))
            
        m["users_views"] = temp

        s = json.dumps(m)
        return s
    
    def __decode__(self, message):
        g = json.loads(message)
        self.view_id = g["view_id"]
        temp = g["users_views"]
        self.users_views = {}

        for i in temp:
            x = uv_decode(i)
            self.users_views[x.UID] = x

        #self.users_views = g["users_views"]
        return self

def gm_encode(obj):
    return str(obj)
def gm_decode(obj):
    return GBMessage().__decode__(obj)

def uv_encode(obj):
    return obj.__encode__()
def uv_decode(obj):
    return UserView().__decode__(obj)

def vm_encode(obj):
    return obj.__encode__()
def vm_decode(obj):
    return ViewMessage().__decode__(obj)

if __name__ == "__main__":
    vm = ViewMessage()

    vm.view_id = 1

    for i in range(5):
        a = UserView()
        a.UID = "tao" + str(i)
        a.user_list = ["123", "124", "125"]
        a.leader = "123"
        a.info = "omaodijfasdjpoiajsdpfjasdifdsaipojfdpiasfa"
        vm.add_user_view(a)

    msg = vm_encode(vm)
    print msg


    v = vm_decode(msg)
    print v.view_id
    print v.users_views
    



'''
    a = UserView()
    a.UID = "tao"
    a.user_list = ["123", "124", "125"]
    a.leader = "123"
    a.info = "omaodijfasdjpoiajsdpfjasdifdsaipojfdpiasfa"
    msg = uv_encode(a)
    print msg

    u = uv_decode(msg)
    print u.UID
    print u.user_list[0] == a.user_list[0]
    '''
    
'''
    a = GBMessage()
    a.view_id = 10
    a.user_id = "tao123"
    a.action = "prepare"
    a.seq = 20
    a.message = "223 is too hard"
    msg = gm_encode(a)

    print msg
    b = gm_decode(msg)
    print b.view_id, b.user_id, b.action,  b.seq, b.message
    '''
