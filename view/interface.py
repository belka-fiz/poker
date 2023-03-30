from entities.round import Round


class ViewInterface:
    @staticmethod
    def round_status(game_round: Round):
        raise NotImplementedError

    @staticmethod
    def list_players(game_round: Round):
        raise NotImplementedError

    @staticmethod
    def last_move():
        raise NotImplementedError

    @staticmethod
    def pot():
        raise NotImplementedError

    @staticmethod
    def showdown():
        raise NotImplementedError

    @staticmethod
    def list_winners():
        raise NotImplementedError
