def get_sentiment_score(userText):
    """
    :param userText: textual representation of the conversation
    :return: sentiment score for the conversation
    """
    # TODO: Implement this function
    return 0.0


if __name__ == '__main__':
    userText = "what can I do for you?"
    score = get_sentiment_score(userText)
    print("The input text is %s.\nThe sentiemnt score is %.2f."%(userText, score))
