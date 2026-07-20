from otree.api import *

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'demographics'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.IntegerField(
        label = "Please enter your age in years.",
        min=0,
        max=100
    )
    gender = models.StringField(
        label = "Please select your gender.",
        choices = [["Female","Female"],["Male","Male"],["Non-Binary","Non-Binary"],["Do not want to disclose", "Do not want to disclose"]]
    )
    statistic = models.IntegerField(
        label = "How do you rate your statistical skill compared to the general public?",
        widget = widgets.RadioSelectHorizontal,
        choices = [[1, "1 (very bad)"], [2, "2"], [3, "3"], [4, "4"],[5, "5 (very good)"]]
    )
    riskaversion = models.IntegerField(
        label="In general, how willing are you to take financial risks?",
        widget=widgets.RadioSelectHorizontal,
        choices=[[1, "1 (completely unwilling to take risks)"], [2, "2"], [3, "3"], [4, "4"], [5, "5"], [6, "6"], [7,"7 (very willing to take risks)"]]
    )
    fininterest = models.IntegerField(
        label='Are you interested in financial markets?',
        choices=[[1, "1 (not at all)"], [2, "2"], [3, "3"], [4, "4"], [5, "5"], [6, "6"], [7, "7 (very much)"]],
        initial=None,
        widget=widgets.RadioSelectHorizontal(),
        blank=True,
    )
    investor = models.IntegerField(
        initial=None,
        verbose_name='Do you own stocks or mutual funds?',
        choices=[[0, 'No'],[1, 'Yes']],
        blank=True,
    )
    financeprof = models.IntegerField(
        initial=None,
        verbose_name='Have you ever had a job in the financial industry?',
        choices=[[0, 'No'],[1, 'Yes']],
        blank=True,
    )
    comments = models.StringField(
        label = "Would you like to comment on the study?",
        blank = True,
    )

# PAGES
class endexperiment(Page):
    pass

class demographics(Page):
    form_model = "player"
    form_fields = ["age","gender","riskaversion","fininterest","investor","financeprof","statistic","comments"]


class completioncode(Page):
    form_model = "player"

    @staticmethod
    def vars_for_template(player):
        # Actual payment always uses the base (unscaled) amounts, regardless
        # of stakes condition: the high-stakes multiplier only affects what
        # is *displayed* to the participant during the task (the chart, the
        # guess questions), not what they are actually paid. This keeps
        # real payouts identical across stakes conditions.
        bonusamount = player.participant.Bonus*2
        if player.participant.BonusChoice == 0:
            payoffs = player.participant.payoffsA[player.participant.bonusperiod-1]
            asset = "Asset A"
        else:
            payoffs = player.participant.payoffsB[player.participant.bonusperiod-1]
            asset = "Asset B"
        # Add the initial-wealth offset (see setup/Instructions.html) so a loss
        # situation never results in a negative bonus payment. This offset is
        # deliberately stakes-independent: for the "high" stakes group the
        # displayed outcome and displayed wealth are both scaled up by the same
        # multiplier and then that multiplier is divided back out, so the real
        # payment here works out the same as for the "low" stakes group.
        payoff = payoffs[player.participant.random_draw] + player.participant.wealth_W
        return dict(
            bonusamount=f"{bonusamount:.2f}",
            bonus_period=player.participant.bonusperiod,
            payoff = f"{payoff:.2f}",
            asset = asset,
        )

page_sequence = [demographics, completioncode]

