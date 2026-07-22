import random
from otree.api import *

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'demographics'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    # Holt & Laury (2002) multiple price list: 10 decisions between a "safe" lottery (Option A) and a "risky" lottery (Option B). The probability of the high payoff rises from 10% to 100% in steps of 10% as the decision number increases; the payoffs themselves stay fixed across all 10 rows.
    HL_NUM_CHOICES = 10
    # Original Holt & Laury (2002) amounts (A: 2.00/1.60, B: 3.85/0.10) scaled by 4/7.55 and rounded to the nearest penny, so the mean of the 4 possible payoffs is exactly £1.00 while keeping the same EV crossover point.
    HL_PAYOFFS = {'A': [1.06, 0.85], 'B': [2.04, 0.05]}

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

    # Holt-Laury: one field per decision row, 0 = Option A (safe), 1 = Option B (risky)
    hl_choice_1 = models.IntegerField(choices=[[0, 'Option A'], [1, 'Option B']], widget=widgets.RadioSelect, label='')
    hl_choice_2 = models.IntegerField(choices=[[0, 'Option A'], [1, 'Option B']], widget=widgets.RadioSelect, label='')
    hl_choice_3 = models.IntegerField(choices=[[0, 'Option A'], [1, 'Option B']], widget=widgets.RadioSelect, label='')
    hl_choice_4 = models.IntegerField(choices=[[0, 'Option A'], [1, 'Option B']], widget=widgets.RadioSelect, label='')
    hl_choice_5 = models.IntegerField(choices=[[0, 'Option A'], [1, 'Option B']], widget=widgets.RadioSelect, label='')
    hl_choice_6 = models.IntegerField(choices=[[0, 'Option A'], [1, 'Option B']], widget=widgets.RadioSelect, label='')
    hl_choice_7 = models.IntegerField(choices=[[0, 'Option A'], [1, 'Option B']], widget=widgets.RadioSelect, label='')
    hl_choice_8 = models.IntegerField(choices=[[0, 'Option A'], [1, 'Option B']], widget=widgets.RadioSelect, label='')
    hl_choice_9 = models.IntegerField(choices=[[0, 'Option A'], [1, 'Option B']], widget=widgets.RadioSelect, label='')
    hl_choice_10 = models.IntegerField(choices=[[0, 'Option A'], [1, 'Option B']], widget=widgets.RadioSelect, label='')
    # Number of Option A ("safe") choices out of 10, and the corresponding
    # Holt & Laury (2002) Table 3 risk-preference classification.
    hl_num_safe_choices = models.IntegerField()
    hl_risk_category = models.StringField()
    # Bonus payment: one decision is randomly drawn and paid out according to
    # the player's choice on that decision and a probability-weighted draw.
    hl_index_to_pay = models.IntegerField()
    hl_option_chosen = models.StringField()
    hl_payoff = models.FloatField()


def classify_hl_risk(num_safe_choices):
    """Map a Holt-Laury safe-choice count (0-10) to Holt & Laury (2002) Table 3 categories."""
    if num_safe_choices <= 1:
        return 'highly risk loving'
    if num_safe_choices == 2:
        return 'very risk loving'
    if num_safe_choices == 3:
        return 'risk loving'
    if num_safe_choices == 4:
        return 'risk neutral'
    if num_safe_choices == 5:
        return 'slightly risk averse'
    if num_safe_choices == 6:
        return 'risk averse'
    if num_safe_choices == 7:
        return 'very risk averse'
    if num_safe_choices == 8:
        return 'highly risk averse'
    return 'extremely risk averse'  # 9 or 10 safe choices


# PAGES
class endexperiment(Page):
    pass

class demographics(Page):
    form_model = "player"
    form_fields = ["age","gender","riskaversion","fininterest","investor","financeprof","statistic","comments"]


class HoltLaury(Page):
    form_model = "player"
    form_fields = [f'hl_choice_{i}' for i in range(1, C.HL_NUM_CHOICES + 1)]

    @staticmethod
    def vars_for_template(player):
        n = C.HL_NUM_CHOICES
        choices = []
        for i in range(1, n + 1):
            prob = i / n
            choices.append(dict(
                index=i,
                field_name=f'hl_choice_{i}',
                prob_pct=f'{prob:.0%}',
                inverse_prob_pct=f'{1 - prob:.0%}',
            ))
        return dict(
            choices=choices,
            a_hi=f"{C.HL_PAYOFFS['A'][0]:.2f}",
            a_lo=f"{C.HL_PAYOFFS['A'][1]:.2f}",
            b_hi=f"{C.HL_PAYOFFS['B'][0]:.2f}",
            b_lo=f"{C.HL_PAYOFFS['B'][1]:.2f}",
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        num_safe = sum(
            1 for i in range(1, C.HL_NUM_CHOICES + 1)
            if getattr(player, f'hl_choice_{i}') == 0
        )
        player.hl_num_safe_choices = num_safe
        player.hl_risk_category = classify_hl_risk(num_safe)

        # Draw the paid decision: pick one of the 10 rows at random, look up
        # which option the player chose on that row, then draw the high/low
        # payoff for that option using that row's probability of the high payoff.
        index_to_pay = random.randint(1, C.HL_NUM_CHOICES)
        option_chosen = getattr(player, f'hl_choice_{index_to_pay}')
        prob_high = index_to_pay / C.HL_NUM_CHOICES
        option_letter = 'A' if option_chosen == 0 else 'B'
        payoff = C.HL_PAYOFFS[option_letter][0] if random.random() < prob_high else C.HL_PAYOFFS[option_letter][1]

        player.hl_index_to_pay = index_to_pay
        player.hl_option_chosen = option_letter
        player.hl_payoff = payoff


class completioncode(Page):
    form_model = "player"

    @staticmethod
    def vars_for_template(player):
        # Actual payment always uses the base (unscaled) amounts, regardless
        # of stakes condition: the high-stakes multiplier only affects what
        # is *displayed* to the participant during the task (the chart, the
        # guess questions), not what they are actually paid. This keeps
        # real payouts identical across stakes conditions.
        incentive = player.participant.incentive
        asset = None
        if incentive == "beliefs":
            task_bonus = player.participant.Bonus * 2
        else:
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
            task_bonus = payoffs[player.participant.random_draw] + player.participant.wealth_W

        # Total = task-app bonus (belief accuracy or investment choice, depending
        # on the incentive condition) + the separately-drawn Holt-Laury bonus.
        total_bonus = task_bonus + player.hl_payoff

        return dict(
            incentive=incentive,
            bonus_period=player.participant.bonusperiod,
            asset=asset,
            task_bonus=f"{task_bonus:.2f}",
            hl_index_to_pay=player.hl_index_to_pay,
            hl_option_chosen=player.hl_option_chosen,
            hl_bonus=f"{player.hl_payoff:.2f}",
            total_bonus=f"{total_bonus:.2f}",
        )

page_sequence = [demographics, HoltLaury, completioncode]

