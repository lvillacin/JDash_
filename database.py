import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
products_db = myclient["products"]
order_management_db = myclient["order_management"]


def get_user(username):
    customers_coll = order_management_db['customers']
    user = customers_coll.find_one({"username":username})
    return user

def get_stalls():
    stall_list = []
    stall_coll = products_db["stalls"]

    for stall in stall_coll.find({}, {"_id":0}):
        stall_list.append(stall)
    return stall_list

def get_stall(stall_name):
    stall_coll = products_db["stalls"]
    stall = stall_coll.find_one({"name":stall_name}, {"_id":0})

    return stall

def get_item(stall_name, item_name):
    stall_coll = products_db["stalls"]
    stall = stall_coll.find_one({"name":stall_name}, {"_id":0})

    menu = stall["menu"]

    for item in menu:
        if item["name"] == item_name:
            return item

def create_order(order):
    orders_coll = order_management_db['orders']
    orders_coll.insert(order)

def change_db(user_user, new1):
    pw_coll = order_management_db['customers']
    customer = {"username":user_user}
    change = {"$set": {"password":new1}}

    pw_coll.find_one_and_update(customer,change)

    return

def check_user_order(user_now):
    orders_coll = order_management_db['orders']
    num_user_orders = []
    num_user_orders = orders_coll.count({"username":user_now})
    return num_user_orders

def get_orders(username):
    order_list = []
    order_details = []
    orders_coll = order_management_db['orders']

    for o in orders_coll.find({"username": username}):
        order_list.append(o)
    return order_list
