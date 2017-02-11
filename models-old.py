from app import db


class User(db.Model):
    username = db.Column(db.String(64), primary_key=True)
    phone = db.Column(db.String(12), unique=True)
    session_token = db.Column(db.String(255), unique=True)
    session_expires = db.Column(db.DateTime)
    auth_token = db.Column(db.Integer)
    auth_expires = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)


class League(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competition = db.Column(
        db.Enum("dance", "rescue", "soccer", name="competition_enum"))
    name = db.Column(db.String(64))
    areas = db.Column(db.Integer, default=1)
    teams = db.relationship("Team", lazy="dynamic", backref="team")
    duration = db.Column(db.Integer)
    requirements = db.Column(db.Text)


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey("league.id"))
    league = db.relationship("League", uselist=False, backref="league")
    pool = db.Column(db.Integer, default=1)
    name = db.Column(db.String(64))
    school = db.Column(db.String(64))
    is_bye = db.Column(db.Boolean, default=False)
    is_system = db.Column(db.Boolean, default=False)
    scrutineer_1 = db.Column(db.Boolean, default=False)
    scrutineer_2 = db.Column(db.Boolean, default=False)

    _score = None

    _home_games = None

    def valid_robots(self):
        robots = 0
        if self.scrutineer_1:
            robots += 1
        if self.scrutineer_2:
            robots += 1
        return robots

    def get_home_games(self):
        if self._home_games is not None:
            return self._home_games
        self._home_games = SoccerGame.query.filter_by(home_team_id=self.id)\
            .filter_by(game_finished=True).all()
        return self._home_games

    _away_games = None

    def get_away_games(self):
        if self._away_games is not None:
            return self._away_games
        self._away_games = SoccerGame.query.filter_by(away_team_id=self.id)\
            .filter_by(game_finished=True).all()
        return self._away_games

    def score(self, finals_only=False):
        if self._score is not None:
            return self._score
        goals = map(lambda game: game.home_goals - game.away_goals,
                    self.get_home_games())
        goals += map(lambda game: game.away_goals - game.home_goals,
                     self.get_away_games())
        self._score = sum(map(lambda goals: 3 if goals >
                              0 else (1 if goals == 0 else 0), goals))
        return self._score

    _goals_for = None

    def goals_for(self, finals_only=False):
        if self._goals_for is not None:
            return self._goals_for
        goals = map(lambda game: game.home_goals, self.get_home_games())
        goals += map(lambda game: game.away_goals, self.get_away_games())
        self._goals_for = sum(goals)
        return self._goals_for

    _goals_against = None

    def goals_against(self, finals_only=False):
        if self._goals_against is not None:
            return self._goals_against
        goals = map(lambda game: game.away_goals, self.get_home_games())
        goals += map(lambda game: game.home_goals, self.get_away_games())
        self._goals_against = sum(goals)
        return self._goals_against

    def goal_difference(self, finals_only=False):
        return self.goals_for(finals_only) - self.goals_against(finals_only)

    _games_played = None

    def games_played(self, finals_only=False):
        if self._games_played is not None:
            return self._games_played
        self._games_played = len(self.get_home_games()) + \
            len(self.get_away_games())
        return self._games_played

    def cache(self):
        self.score()
        self.goals_for()
        self.goals_against()
        self.games_played()

    def compare(self, other, finals_only=False):
        score = self.score(finals_only) - other.score(finals_only)
        if score is not 0:
            return score

        goal_difference = self.goal_difference(
            finals_only) - other.goal_difference(finals_only)
        if goal_difference is not 0:
            return goal_difference

        goals_for = self.goals_for(finals_only) - other.goals_for(finals_only)
        if goals_for is not 0:
            return goals_for

        games_played = self.games_played(
            finals_only) - other.games_played(finals_only)
        if games_played is not 0:
            return games_played

        if sorted([self.name, other.name])[0] == self.name:
            return 1
        else:
            return -1


class SoccerGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey("league.id"))
    league = db.relationship("League", uselist=False, backref="sc_league")
    home_team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    away_team_id = db.Column(db.Integer, db.ForeignKey("team.id"))
    home_team = db.relationship("Team", uselist=False, backref="home_team",
                                primaryjoin="SoccerGame.home_team_id==Team.id")
    away_team = db.relationship("Team", uselist=False, backref="away_team",
                                primaryjoin="SoccerGame.away_team_id==Team.id")
    field = db.Column(db.Integer)
    round = db.Column(db.Integer)
    scheduled_time = db.Column(db.DateTime)
    winner_agrees = db.Column(db.Boolean, default=False)
    loser_agrees = db.Column(db.Boolean, default=False)
    home_goals = db.Column(db.Integer, default=0)
    away_goals = db.Column(db.Integer, default=0)
    game_finished = db.Column(db.Boolean, default=False)
    timer_start = db.Column(db.DateTime)
    first_half_finished = db.Column(db.Boolean, default=False)
    half_time_finished = db.Column(db.Boolean, default=False)
    second_half_finished = db.Column(db.Boolean, default=False)
    is_final = db.Column(db.Boolean, default=False)
    home_damaged_1 = db.Column(db.DateTime)
    home_damaged_2 = db.Column(db.DateTime)
    away_damaged_1 = db.Column(db.DateTime)
    away_damaged_2 = db.Column(db.DateTime)
    ref_id = db.Column(db.String(64), db.ForeignKey("user.username"))
    referee = db.relationship("User", uselist=False, backref="referee")

    def time(self):
        return self.scheduled_time.strftime("%a %H:%M")

    def is_system_game(self):
        return (self.home_team.is_system and not self.home_team.is_bye) \
            or (self.away_team.is_system and not self.away_team.is_bye)

    def is_bye(self):
        return (self.home_team.is_bye or self.away_team.is_bye)

    def can_populate(self):
        if not self.is_system_game():
            return False
        games = SoccerGame.query.filter_by(game_finished=False).filter_by(
            league_id=self.league_id)\
            .filter(SoccerGame.round < self.round).all()
        for game in games:
            if not game.home_team.is_bye and not game.away_team.is_bye:
                return False
        return True


class RequestType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    only_admin = db.Column(db.Boolean, default=False)
    priority = db.Column(db.Integer, default=50)
    send_text = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.String(64), db.ForeignKey("user.username"))
    user = db.relationship("User", uselist=False, backref="user")


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_type_id = db.Column(db.Integer, db.ForeignKey("request_type.id"))
    request_type = db.relationship(
        "RequestType", uselist=False, backref="request_type")
    user_id = db.Column(db.String(64), db.ForeignKey("user.username"))
    user = db.relationship("User", uselist=False, backref="request_user")
    received = db.Column(db.DateTime, server_default=db.func.now())
    game_id = db.Column(db.Integer, db.ForeignKey("soccer_game.id"))
    game = db.relationship("SoccerGame", uselist=False, backref="game")
    actioned = db.Column(db.Boolean, default=False)
