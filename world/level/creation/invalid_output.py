class InvalidOutputException(Exception):
    """
    Used as an indicator that a generator could not complete a task because
    a previous generator did not fulfil its requirements
    """

