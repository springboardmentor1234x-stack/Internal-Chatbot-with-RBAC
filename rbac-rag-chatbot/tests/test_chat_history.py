from chat.history_store import ChatHistoryStore


def sanity_test():
    store = ChatHistoryStore()

    store.add_user_message("alice", "Hello")

    print("User history after adding message:")
    print(store.get_user_history("alice"))

    store.clear_user_history("alice")

    print("User history after clearing:")
    print(store.get_user_history("alice"))

if __name__ == "__main__":
    sanity_test()
