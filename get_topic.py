def get_topic(userText):
    """
    :param userText: textual representation of the conversation
    :return: modeled topic inferred for the conversation
    """
    # TODO: Implement this function
    return 'shopping'


if __name__ == '__main__':
    userText = "what can I do for you?"
    topic = get_topic(userText)
    print("The input text is %s.\nThe inferred topic is \"%s\"."%(userText, topic))
