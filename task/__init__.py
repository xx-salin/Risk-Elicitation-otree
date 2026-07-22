from otree.api import *
import random
import math

doc = """ Public Learning """


class C(BaseConstants):
    NAME_IN_URL = 'task'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.StringField()
    incentive = models.StringField()
    stakes = models.StringField()
    # 0 = payoff bars are color-coded red/green for loss/gain, 1 = bars keep
    # their current neutral per-asset color. Randomized once per participant
    # in setup/__init__.py; copied here per round for the CSV export.
    color_treatment = models.IntegerField()

    #captures which of the 5 joint distributions is used
    tuplesorder = models.IntegerField()
    # order (1-indexed, matching Distributions.xlsx row order) in which this round's
    # N situations' Option A / Option B outcomes were drawn - comma-separated since
    # a list can't be stored directly. Under dependence_variation "1" the two
    # differ (each alternative shuffled independently); under "2.1"/"2.2" they're
    # identical (the pairing is locked - see setup/__init__.py's creating_session).
    # Copied per round from participant.situation_order_a/_b (setup/__init__.py)
    # so they show up as columns in this app's own CSV export.
    situation_order_a = models.StringField()
    situation_order_b = models.StringField()
    # "1" = this round's outcomes were independently shuffled per alternative
    # (structure of dependence broken up); "2.1"/"2.2" = one of the two fixed
    # pairings from Distributions.xlsx (structure of dependence preserved).
    # Drawn per round in setup/__init__.py's creating_session with 50%/25%/25%
    # probability; copied here per round for the CSV export.
    dependence_variation = models.StringField()
    # Per-distribution thresholds (Distributions.xlsx "All" sheet, "Round
    # Thresholds" block) for this round's distribution - same threshold used for
    # both alternatives. Copied per round from participant.freq_thres_l/
    # freq_thres_h/tail_thres_l/tail_thres_h (setup/__init__.py) for the CSV export.
    freq_thres_l = models.FloatField()
    freq_thres_h = models.FloatField()
    tail_thres_l = models.FloatField()
    tail_thres_h = models.FloatField()

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
    # min=None: otree defaults a numeric field's min to 0 unless told
    # otherwise, which would silently reject negative guesses. Payoffs (and
    # so the correct guess) can be negative and, at high stakes, can exceed
    # the low-stakes range of +/-2.2, scaled by stakes_multiplier. Bounds are
    # enforced dynamically per player - see Expectations.error_message /
    # Expectations_Choice.error_message below.
    Average_Guess_Alt1 = models.FloatField(min=None)
    Average_Guess_Alt2 = models.FloatField(min=None)
    Prob_1_Guess_Alt1 = models.FloatField(
        min=0,
        max=100
    )
    Prob_1_Guess_Alt2 = models.FloatField(
        min=0,
        max=100
    )
    Prob_2_Guess_Alt1 = models.FloatField(
        min=0,
        max=100
    )
    Prob_2_Guess_Alt2 = models.FloatField(
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
    def vars_for_template(player):
        return dict(
            num_situations=player.session.config["num_situations"],
        )

    @staticmethod
    def is_displayed(player):
        player.treatment = player.participant.treatment
        player.incentive = player.participant.incentive
        player.stakes = player.participant.stakes
        return player.round_number==1



class Payoffs_Together(Page):
    form_model = "player"
    form_fields = ['sequentialTimeSpent', 'simultaneousTimeSpent']

    @staticmethod
    def vars_for_template(player):
        player.tuplesorder = player.participant.tuplesorder[player.round_number-1]
        player.situation_order_a = ','.join(str(s) for s in player.participant.situation_order_a[player.round_number-1])
        player.situation_order_b = ','.join(str(s) for s in player.participant.situation_order_b[player.round_number-1])
        player.dependence_variation = player.participant.dependence_variation[player.round_number-1]
        player.freq_thres_l = player.participant.freq_thres_l[player.round_number-1]
        player.freq_thres_h = player.participant.freq_thres_h[player.round_number-1]
        player.tail_thres_l = player.participant.tail_thres_l[player.round_number-1]
        player.tail_thres_h = player.participant.tail_thres_h[player.round_number-1]
        player.color_treatment = player.participant.color_treatment
        multiplier = player.participant.stakes_multiplier
        arrayA = [x * multiplier for x in player.participant.payoffsA[player.round_number-1]]
        arrayB = [x * multiplier for x in player.participant.payoffsB[player.round_number-1]]

        def fmt2(x):
            return f"{x:.2f}"

        def pct0(x):
            return f"{x:.0%}"

        # TAIL_THRES_L/H (per-distribution, Distributions.xlsx "All" sheet) -
        # thresholds scale with stakes so "below/above" stays meaningful
        # regardless of the multiplier
        below_threshold = player.tail_thres_l * multiplier
        above_threshold = player.tail_thres_h * multiplier

        averageA = fmt2(sum(arrayA) / len(arrayA))
        averageB = fmt2(sum(arrayB) / len(arrayB))
        belowA = pct0(sum(x < below_threshold for x in arrayA) / len(arrayA))
        belowB = pct0(sum(x < below_threshold for x in arrayB) / len(arrayB))
        aboveA = pct0(sum(x > above_threshold for x in arrayA) / len(arrayA))
        aboveB = pct0(sum(x > above_threshold for x in arrayB) / len(arrayB))
        stdA = fmt2(math.sqrt(sum((x - (sum(arrayA) / len(arrayA))) ** 2 for x in arrayA) / len(arrayA)))
        stdB = fmt2(math.sqrt(sum((x - (sum(arrayB) / len(arrayB))) ** 2 for x in arrayB) / len(arrayB)))

        return dict(
            arrayA=arrayA,
            arrayB=arrayB,
            animation_time=0,
            max_value=2.2 * multiplier,
            averageA=averageA,
            averageB=averageB,
            belowA=belowA,
            belowB=belowB,
            aboveA=aboveA,
            aboveB=aboveB,
            below_threshold=fmt2(below_threshold),
            above_threshold=fmt2(above_threshold),
            stdA=stdA,
            stdB=stdB,
            color_treatment=player.color_treatment,
            round_number=player.round_number,
            num_situations=player.session.config["num_situations"],
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
        return ['Average_Guess_Alt1','Average_Guess_Alt2','Prob_1_Guess_Alt1','Prob_1_Guess_Alt2','Prob_2_Guess_Alt1','Prob_2_Guess_Alt2','Volatility']

    @staticmethod
    def vars_for_template(player: Player):
        multiplier = player.participant.stakes_multiplier
        return dict(
            round_number = player.round_number,
            average_guess_min = f"{-2.2 * multiplier:.2f}",
            average_guess_max = f"{2.2 * multiplier:.2f}",
            freq_thres_l = f"{player.participant.freq_thres_l[player.round_number-1] * multiplier:.2f}",
            freq_thres_h = f"{player.participant.freq_thres_h[player.round_number-1] * multiplier:.2f}",
        )

    @staticmethod
    def error_message(player: Player, values):
        multiplier = player.participant.stakes_multiplier
        guess_min, guess_max = -2.2 * multiplier, 2.2 * multiplier
        for field in ['Average_Guess_Alt1', 'Average_Guess_Alt2']:
            if not (guess_min <= values[field] <= guess_max):
                return f"Value must be between {guess_min:.2f} and {guess_max:.2f}"

    @staticmethod
    def is_displayed(player: Player):
        return player.incentive == "beliefs"

class Expectations_Choice(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        return ['Average_Guess_Alt1','Average_Guess_Alt2','Prob_1_Guess_Alt1','Prob_1_Guess_Alt2','Prob_2_Guess_Alt1','Prob_2_Guess_Alt2','Volatility']

    @staticmethod
    def vars_for_template(player: Player):
        multiplier = player.participant.stakes_multiplier
        return dict(
            average_guess_min = f"{-2.2 * multiplier:.2f}",
            average_guess_max = f"{2.2 * multiplier:.2f}",
            freq_thres_l = f"{player.participant.freq_thres_l[player.round_number-1] * multiplier:.2f}",
            freq_thres_h = f"{player.participant.freq_thres_h[player.round_number-1] * multiplier:.2f}",
            round_number = player.round_number,
        )

    @staticmethod
    def error_message(player: Player, values):
        multiplier = player.participant.stakes_multiplier
        guess_min, guess_max = -2.2 * multiplier, 2.2 * multiplier
        for field in ['Average_Guess_Alt1', 'Average_Guess_Alt2']:
            if not (guess_min <= values[field] <= guess_max):
                return f"Value must be between {guess_min:.2f} and {guess_max:.2f}"

    @staticmethod
    def is_displayed(player: Player):
        return player.incentive == "choice"


class NextRound(Page):
    form_model = "player"

    @staticmethod
    def vars_for_template(player):
        return dict(
            next_round=player.round_number+1,
            num_situations=player.session.config["num_situations"],
        )

    def is_displayed(player):
        player.participant.random_draw = random.choice([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        if player.incentive == "beliefs":
            if player.round_number == player.participant.bonusperiod:
                random_choice = random.randint(1,7)
                payoffsA_this_round = player.participant.payoffsA[player.round_number - 1]
                payoffsB_this_round = player.participant.payoffsB[player.round_number - 1]
                # +/-GUESS_TOLERANCE (settings.py) band around the correct answer
                tol = player.session.config["guess_tolerance"]
                if random_choice == 1:  # Average_Guess_Alt1 chosen for payoff
                    # scale by stakes_multiplier: the guess was made against
                    # the displayed (possibly scaled) chart, so the
                    # correctness check must use the same scale
                    correct_value = player.participant.stakes_multiplier * sum(payoffsA_this_round) / len(payoffsA_this_round)
                    # correct_value can now be negative (losses), so the tolerance
                    # band must be sorted rather than assumed low-to-high
                    lo, hi = sorted([(1 - tol) * correct_value, (1 + tol) * correct_value])
                    if lo <= player.Average_Guess_Alt1 <= hi:
                        player.Bonus = 1
                if random_choice == 2:  # Average_Guess_Alt2 chosen for payoff
                    correct_value = player.participant.stakes_multiplier * sum(payoffsB_this_round) / len(payoffsB_this_round)
                    lo, hi = sorted([(1 - tol) * correct_value, (1 + tol) * correct_value])
                    if lo <= player.Average_Guess_Alt2 <= hi:
                        player.Bonus = 1
                if random_choice == 3:  # Prob_1_Guess_Alt1 chosen for payoff
                    # threshold matches freq_thres_l for this round's distribution
                    # (Distributions.xlsx "All" sheet, "Round Thresholds" block) *
                    # multiplier shown on the Expectations page; multiplier cancels out
                    # here since payoffsA_this_round is unscaled
                    freq_thres_l = player.participant.freq_thres_l[player.round_number - 1]
                    correct_value = 100 * sum(x < freq_thres_l for x in payoffsA_this_round) / len(payoffsA_this_round)
                    if (1 - tol) * correct_value <= player.Prob_1_Guess_Alt1 <= (1 + tol) * correct_value:
                        player.Bonus = 1
                if random_choice == 4:  # Prob_1_Guess_Alt2 chosen for payoff
                    freq_thres_l = player.participant.freq_thres_l[player.round_number - 1]
                    correct_value = 100 * sum(x < freq_thres_l for x in payoffsB_this_round) / len(payoffsB_this_round)
                    if (1 - tol) * correct_value <= player.Prob_1_Guess_Alt2 <= (1 + tol) * correct_value:
                        player.Bonus = 1
                if random_choice == 6:  # Prob_2_Guess_Alt1 chosen for payoff
                    # threshold matches freq_thres_h for this round's distribution
                    # (Distributions.xlsx "All" sheet, "Round Thresholds" block) *
                    # multiplier shown on the Expectations page; multiplier cancels out
                    # here since payoffsA_this_round is unscaled
                    freq_thres_h = player.participant.freq_thres_h[player.round_number - 1]
                    correct_value = 100 * sum(x > freq_thres_h for x in payoffsA_this_round) / len(payoffsA_this_round)
                    if (1 - tol) * correct_value <= player.Prob_2_Guess_Alt1 <= (1 + tol) * correct_value:
                        player.Bonus = 1
                if random_choice == 7:  # Prob_2_Guess_Alt2 chosen for payoff
                    freq_thres_h = player.participant.freq_thres_h[player.round_number - 1]
                    correct_value = 100 * sum(x > freq_thres_h for x in payoffsB_this_round) / len(payoffsB_this_round)
                    if (1 - tol) * correct_value <= player.Prob_2_Guess_Alt2 <= (1 + tol) * correct_value:
                        player.Bonus = 1
                if random_choice == 5:  # Volatility chosen for payoff
                    stdA = math.sqrt(sum((x - sum(payoffsA_this_round) / len(payoffsA_this_round)) ** 2 for x in payoffsA_this_round) / len(payoffsA_this_round))
                    stdB = math.sqrt(sum((x - sum(payoffsB_this_round) / len(payoffsB_this_round)) ** 2 for x in payoffsB_this_round) / len(payoffsB_this_round))
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