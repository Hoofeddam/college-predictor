conversation_store = {}


def load(user_id):

    return conversation_store.get(user_id)


def save(user_id, state):

    conversation_store[user_id] = state


def clear(user_id):

    conversation_store.pop(user_id, None)