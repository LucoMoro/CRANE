from network.communication.message import Message


class Conversation:
    def __init__(self, moderator, reviewers):
        self.moderator = moderator
        self.reviewers = reviewers
        self.history = []


    def set_message(self, message: Message) -> None:
        self.history.append(message)