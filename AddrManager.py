
class AddrManager():
    def __init__(self, addr, UID):
        self.localaddr = addr
        self.UID = UID
        self.user_dict = {}
        self.user_dict[UID] = addr

    def update_dict(self, user_dict):
        for user in user_dict:
            if user not in self.user_dict:
                self.user_dict[user] = user_dict[user]
    def remove_dict(self, user_id):
        if user_id in self.user_dict:
            del self.user_dict[user_id]

    def get_dict(self):
        return self.user_dict

if __name__ == "__main__":
    localaddr = ("localhost", 33333)
    addrs = {}
    for i in range(3):
        addrs["UID" + str(i)] = ("localhost", i)

    addrmanager = AddrManager(localaddr, "me")
    addrmanager.update_dict(addrs)

    addrs["new_id"] = ("localhost", 30000)

    addrmanager.update_dict(addrs)

    temp = {"1":("192.168.1.1", 10)}

    addrmanager.update_dict(temp)

    print addrmanager.get_dict()


