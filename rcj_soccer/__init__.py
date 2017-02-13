from rcj_soccer import base
from rcj_soccer import models
import rcj_soccer.views.draws
import rcj_soccer.views.games
import rcj_soccer.views.leagues
import rcj_soccer.views.liveresults
import rcj_soccer.views.messaging
import rcj_soccer.views.referee
import rcj_soccer.views.requesttypes
import rcj_soccer.views.results
import rcj_soccer.views.rules
import rcj_soccer.views.scrutineer
import rcj_soccer.views.teams
import rcj_soccer.views.users

application = base.app
manager = base.manager
migrate = base.migrate