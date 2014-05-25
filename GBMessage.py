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
def decode_gb(obj):
    gbm = GBMessage()
    return gbm.__decode__(obj)

def decode_vm(obj):
    gbm = ViewMessage()
    return gbm.__decode__(obj)

def decode_uv(obj):
    gbm = UserView()
    return gbm.__decode__(obj)

def encode(obj):
    return obj.__encode__()

class GBMessage(): 
    def __init__(self, view_id = 0, user_id = 0, seq = 0, message = ""):
        self.view_id = view_id
        self.user_id = user_id
        self.seq = seq
        self.message = message
    def __encode__(self):
        #m = "%d,%s,%d,%s" % (self.view_id, self.user_id, self.seq, self.message)
        m = {}
        m["view_id"] = self.view_id
        m["user_id"] = self.user_id
        m["seq"] = self.seq
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
        m["UID"] = UID
        m["user_list"] = user_list
        m["leader"] = leader
        m["info"] = info
        s = json.dumps(m)
        return s
    def __decode__(self, message):
        s = json.dumps(message)
        self.UID = s["UID"]
        self.user_list = s["user_list"]
        self.leader = s["leader"]
        self.info = s["info"]
        return self

class ViewMessage(): # !, #, | is used
    def __init__(self, view_id = 0):
        self.view_id = view_id
        self.users_views = {}

    def __encode__(self):
        m = {}
        m["view_id"] = self.view_id
        temp = []
        for i in users_views:
            temp.append(encode(i))
            
        m["users_views"] = temp

        s = json.dumps(m)
        return s
    
    def __decode__(self, message):
        g = json.loads(message)
        self.view_id = g["view_id"]
        temp = g["users_views"]
        self.users_views = {}
        for i in temp:
            self.users_views.append(decode_uv(i))
        #self.users_views = g["users_views"]
        return self


if __name__ == "__main__":
    view_m = ViewMessage()
    view_m.view_id = 10
    view_m.add_UID("321", ["3", '2', '1'], '1', "iajdsoaijsdoipajpjxcoijviopzxjvipjzvipozx")
    view_m.add_UID("123", ["a", 'b', 'c'], '1', "ajdofasjpiasjfpaisdjiofjadspdfijasp")

    x = encode(view_m)
    print x

    c = decode_vm(x)
    print c.view_id


    
    '''
    a = GBMessage()
    a.view_id = 10
    a.user_id = "tao123"
    a.seq = 20
    a.message = "223 is too hard"
    msg = encode(a)
    print msg
    b = decode(msg)
    print b.view_id, b.user_id, b.seq, b.message
    '''
