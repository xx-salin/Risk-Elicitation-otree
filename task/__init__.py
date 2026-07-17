from otree.api import *
import random
import math

doc = """ Public Learning """


class C(BaseConstants):
    NAME_IN_URL = 'task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 5


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.StringField()
    incentive = models.StringField()

    #captures which of the 5 joint distributions is used
    tuplesorder = models.IntegerField()

    # bonus
    Bonus = models.IntegerField(
        initial=0,
    )

    #captures time
    sequentialTimeSpent = models.StringField(blank=True) # Record time spent on each situation in sequential_joint, in milliseconds
    simultaneousTimeSpent = models.StringField(blank=True) # Record time spent on each tooltip in simultaneous_joint, in milliseconds

    #investmentdecision
    InvestmentAsset = models.IntegerField(
        label='I choose to invest my wealth into:',
        choices=[[0, 'Asset A'],[1, 'Asset B']],
        widget=widgets.RadioSelectHorizontal(),
    )
    InvestmentPreference = models.FloatField(
        label='How strong is your preference for your chosen asset?',
        initial=None,
    )
    #capture inconsistent preferences that trigger an error messge
    PreferenceError = models.IntegerField(
        initial=0,
        blank=True,
    )

    #beliefs
    Average_Guess_Alt1 = models.FloatField(
        min=0,
        max=2.2,
    )
    Average_Guess_Alt2 = models.FloatField(
        min=0,
        max=2.2,
    )
    Prob_1_Guess_Alt1 = models.FloatField(
        min=0,
        max=100
    )
    Prob_1_Guess_Alt2 = models.FloatField(
        min=0,
        max=100
    )
    Volatility = models.IntegerField(
        label="Which asset exhibited a stronger variation in payoffs?",
        choices=[[0, 'Asset A'], [1, 'Asset B'], [2, 'No difference']],
        widget=widgets.RadioSelectHorizontal(),
    )
    ChoiceAvrgReturn = models.IntegerField(
        label='When making your choices, to what extent did you rely on the average payoff of the assets? Select a category between 1 ("Not at all") and 5 ("A lot").',
        choices=range(1, 6),
        widget=widgets.RadioSelectHorizontal()
    )
    ChoiceVolatility = models.IntegerField(
        label='When making your choices, to what extent did you rely on the variation in payoffs? Select a category between 1 ("Not at all") and 5 ("A lot").',
        choices=range(1, 6),
        widget=widgets.RadioSelectHorizontal()
    )
    ChoiceExtreme = models.IntegerField(
        label='When making your choices, to what extent did you rely on situations with an extreme difference in payoffs between the two assets? Select a category between 1 ("Not at all") and 5 ("A lot").',
        choices=range(1, 6),
        widget=widgets.RadioSelectHorizontal()
    )

# FUNCTIONS
pass



# PAGES
class Start(Page):
    form_model = "player"

    @staticmethod
    def is_displayed(player):
        player.treatment = player.participant.treatment
        player.incentive = player.participant.incentive
        return player.round_number==1



class Payoffs_Together(Page):
    form_model = "player"
    form_fields = ['sequentialTimeSpent', 'simultaneousTimeSpent']

    @staticmethod
    def vars_for_template(player):
        player.tuplesorder = player.participant.tuplesorder[player.round_number-1]
        arrayA = player.participant.payoffsA[player.round_number-1]
        arrayB = player.participant.payoffsB[player.round_number-1]

        def fmt2(x):
            return f"{x:.2f}"

        def pct0(x):
            return f"{x:.0%}"

        averageA = fmt2(sum(arrayA) / len(arrayA))
        averageB = fmt2(sum(arrayB) / len(arrayB))
        belowA = pct0(sum(x < 0.6 for x in arrayA) / len(arrayA))
        belowB = pct0(sum(x < 0.6 for x in arrayB) / len(arrayB))
        aboveA = pct0(sum(x > 1.4 for x in arrayA) / len(arrayA))
        aboveB = pct0(sum(x > 1.4 for x in arrayB) / len(arrayB))
        stdA = fmt2(math.sqrt(sum((x - (sum(arrayA) / len(arrayA))) ** 2 for x in arrayA) / len(arrayA)))
        stdB = fmt2(math.sqrt(sum((x - (sum(arrayB) / len(arrayB))) ** 2 for x in arrayB) / len(arrayB)))

        return dict(
            arrayA=arrayA,
            arrayB=arrayB,
            animation_time=0,
            max_value=2.5,
            averageA=averageA,
            averageB=averageB,
            belowA=belowA,
            belowB=belowB,
            aboveA=aboveA,
            aboveB=aboveB,
            stdA=stdA,
            stdB=stdB,
            round_number=player.round_number,
        )

class InvestmentDecision(Page):
    form_model = 'player'
    form_fields = ['InvestmentAsset', 'InvestmentPreference','PreferenceError']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            round_number = player.round_number,
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.incentive == "choice"

class InvestmentDecision_Belief(Page):
    form_model = 'player'
    form_fields = ['InvestmentAsset', 'InvestmentPreference', 'PreferenceError']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            round_number = player.round_number,
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.incentive == "beliefs"


class Expectations(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        return ['Average_Guess_Alt1','Average_Guess_Alt2','Prob_1_Guess_Alt1','Prob_1_Guess_Alt2','Volatility']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            round_number = player.round_number,
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.incentive == "beliefs"

class Expectations_Choice(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        return ['Average_Guess_Alt1','Average_Guess_Alt2','Prob_1_Guess_Alt1','Prob_1_Guess_Alt2','Volatility']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            round_number = player.round_number,
        )

    @staticmethod
    def is_displayed(player: Player):
        return player.incentive == "choice"


class NextRound(Page):
    form_model = "player"

    @staticmethod
    def vars_for_template(player):
        return dict(
            next_round=player.round_number+1,
        )

    def is_displayed(player):
        player.participant.random_draw = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        if player.incentive == "beliefs":
            if player.round_number == player.participant.bonusperiod:
                random_choice = random.randint(1,5)
                if random_choice == 1:  # Average_Guess_Alt1 chosen for payoff
                    correct_value = sum(player.participant.payoffsA[player.round_number-1])/11
                    if 0.95 * correct_value <= player.Average_Guess_Alt1 <= 1.05 * correct_value:
                        player.Bonus = 1
                if random_choice == 2:  # Average_Guess_Alt2 chosen for payoff
                    correct_value = sum(player.participant.payoffsB[player.round_number-1])/11
                    if 0.95 * correct_value <= player.Average_Guess_Alt2 <= 1.05 * correct_value:
                        player.Bonus = 1
                if random_choice == 3:  # Prob_1_Guess_Alt1 chosen for payoff
                    correct_value = (5 / 11) * 100
                    if 0.95 * correct_value <= player.Prob_1_Guess_Alt1 <= 1.05 * correct_value:
                        player.Bonus = 1
                if random_choice == 4:  # Prob_1_Guess_Alt2 chosen for payoff
                    correct_value = (5 / 11) * 100
                    if 0.95 * correct_value <= player.Prob_1_Guess_Alt2 <= 1.05 * correct_value:
                        player.Bonus = 1
                if random_choice == 5:  # Volatility chosen for payoff
                    stdA = math.sqrt(sum((x - sum(player.participant.payoffsA[player.round_number - 1])/11) ** 2 for x in player.participant.payoffsA[player.round_number - 1]) / len(player.participant.payoffsA[player.round_number - 1]))
                    stdB = math.sqrt(sum((x - sum(player.participant.payoffsB[player.round_number - 1])/11) ** 2 for x in player.participant.payoffsB[player.round_number - 1]) / len(player.participant.payoffsB[player.round_number - 1]))
                    if stdA == stdB:
                        if player.Volatility == 2:
                            player.Bonus = 1
                    elif stdA < stdB:
                        if round(stdA,1) == round(stdB,1):
                            if player.Volatility == 2 or player.Volatility == 1:
                                player.Bonus = 1
                        else:
                            if player.Volatility == 1:
                                player.Bonus = 1
                    else:
                        if round(stdA,1) == round(stdB,1):
                            if player.Volatility == 2 or player.Volatility == 0:
                                player.Bonus = 1
                        else:
                            if player.Volatility == 0:
                                player.Bonus = 1
                player.participant.Bonus = player.Bonus
                player.participant.BonusChoice = player.InvestmentAsset
        if player.incentive == "choice":
            if player.round_number == player.participant.bonusperiod:
                player.participant.BonusChoice = player.InvestmentAsset
                player.participant.Bonus = player.Bonus
        return True

class Final_Questions(Page):
    form_model = "player"
    form_fields = ["ChoiceAvrgReturn","ChoiceVolatility", "ChoiceExtreme"]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == C.NUM_ROUNDS



page_sequence = [Start, Payoffs_Together, InvestmentDecision, Expectations_Choice, Expectations, InvestmentDecision_Belief, NextRound, Final_Questions]