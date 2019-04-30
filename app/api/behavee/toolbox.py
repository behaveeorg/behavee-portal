'''
file to store functions used in API data processing
'''

def check_if_exist(dictionary, key):
    '''
    :param dictionary: dictionary to search
    :param key: key to search in dictionary.keys()
    :return: return value of dictionary key if exist, if not exist return dictionary data in key 0
    '''
    if key in dictionary.keys():
        return dictionary[key]
    else:
        return dictionary[0]


def check_type(item_enum):
    '''
    UNUSED
    :param item_enum:
    :return:
    '''
    if item_enum:
        return item_enum.name
    else:
        return None

def most_common(lst):
    '''
    :param lst: list to search in
    :return: return a most occuring integer in list
    '''
    if len(lst) > 0: return max(set(lst), key=lst.count)
    else: return None

def get_type(types, num = None):
    '''
    translates enum from db int to string
    :param types: type of enum
    :param num: integer from db
    :return: return a string of enum if found, if not found, returns None
    '''
    if not types:
        return None
    if not num:
        return None

    for type in types:
        if type[0] == num:
            return type[1]

    return None

def post_type(types, enum = None):
    '''
    translates enum string to db integer
    :param types: type of enum
    :param enum: string to translate
    :return: return a integer if found in enum types, return a 0 if not found
    '''
    if not types:
        return None
    if not enum:
        return None

    for type in types:
        if type[1] == enum:
            return type[0]

    return 0

def price_check(price):
    '''
    return 0 instead of None if price does not exist
    :param price: price to check
    :return: return the price if it exist, else it return 0
    '''
    if price:
        return price
    else:
        return 0

def get_att_list(lst, r_att, c_att, att_value):
    '''
    :param lst: list of items
    :param r_att: attribute of item in list to return
    :param c_att: attribute of item in list to compare
    :param att_value: attribute value
    :return: return attribute of item in list where item.c_att is equal to att_value
    '''

    for item in lst:
        if str(getattr(item, c_att)) == str(att_value):
            return getattr(item, r_att)
    return None

def delete_lists_duplicates(lst1, lst2, att1, att2):
    '''
    :param lst1: first list
    :param lst2: second list
    :return: removes all object that are in second list from first list, then returns first list
    '''

    for item2 in lst2:
        for i,item1 in enumerate(lst1):
            if getattr(item2, att1) == getattr(item1, att1) and getattr(item2, att2) == getattr(item1, att2):
                lst1.pop(i)
                break

    return lst1

