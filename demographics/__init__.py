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

    # BRET, Crosetto & Filippin (2013). 
    # config.py (dynamic=False, random=False, devils_game=True, undoable=False).
    # reimplemented as a single round with plain HTML/JS rather than the original Angular-based library, to match this project's other pages.
    BRET_NUM_BOXES = 50
    BRET_BOX_VALUE = 0.04

    # Eckel & Grossman (2002) single choice list: one choice among EG_NUM_LOTTERIES
    # paired lotteries, each paying a "low" or "high" amount with 50/50 probability.
    # Expected value and spread both increase monotonically down the list, from a
    # risk-free option (lottery 1: low == high) to the riskiest. Reimplemented from
    # scl-master's config.py (num_lotteries=5, risk_loving=False), rescaled to this
    # study's £ stakes.
    EG_NUM_LOTTERIES = 5
    EG_SURE_PAYOFF = 1.00
    EG_DELTA_LO = 0.25
    EG_DELTA_HI = 0.50
    EG_PROBABILITY_HIGH = 0.5

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

    # Which single risk elicitation method this participant sees, drawn once
    # (demographics.before_next_page below): 'HoltLaury', 'BRET', or 'EckelGrossman'.
    risk_task = models.StringField()

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

    # BRET: number of boxes the player chose to collect before stopping.
    bret_boxes_collected = models.IntegerField(min=0, max=C.BRET_NUM_BOXES, label='')
    # Position (1..BRET_NUM_BOXES) of the hidden bomb, drawn once when the page is first displayed. Never sent to the template/client.
    bret_bomb_index = models.IntegerField(blank=True)
    bret_bomb_hit = models.BooleanField(blank=True)
    bret_payoff = models.FloatField(blank=True)

    # Eckel-Grossman: index (1..EG_NUM_LOTTERIES) of the single lottery chosen.
    eg_lottery_choice = models.IntegerField(min=1, max=C.EG_NUM_LOTTERIES, label='')
    eg_outcome_lo = models.FloatField(blank=True)
    eg_outcome_hi = models.FloatField(blank=True)
    eg_outcome_to_pay = models.StringField(blank=True)
    eg_payoff = models.FloatField(blank=True)


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

    @staticmethod
    def before_next_page(player, timeout_happened):
        # Draw which single risk elicitation method this participant will see,
        # once, right before entering that block of pages.
        player.risk_task = random.choice(['HoltLaury', 'BRET', 'EckelGrossman'])


class HoltLaury(Page):
    form_model = "player"
    form_fields = [f'hl_choice_{i}' for i in range(1, C.HL_NUM_CHOICES + 1)]

    @staticmethod
    def is_displayed(player):
        return player.risk_task == 'HoltLaury'

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


class BRET(Page):
    form_model = "player"
    form_fields = ['bret_boxes_collected']

    @staticmethod
    def is_displayed(player):
        return player.risk_task == 'BRET'

    @staticmethod
    def vars_for_template(player):
        # Draw (and freeze) the bomb's position the first time this page is
        # displayed, so a page reload doesn't move the bomb mid-decision.
        if player.field_maybe_none('bret_bomb_index') is None:
            player.bret_bomb_index = random.randint(1, C.BRET_NUM_BOXES)
        return dict(
            box_indices=list(range(1, C.BRET_NUM_BOXES + 1)),
            num_boxes=C.BRET_NUM_BOXES,
            box_value=f"{C.BRET_BOX_VALUE:.2f}",
            max_payoff=f"{C.BRET_NUM_BOXES * C.BRET_BOX_VALUE:.2f}",
            # Sent to the client so the box that explodes can be revealed to the
            # player immediately on click (matching oTree_BRET-master's reference
            # implementation, which likewise determines/reveals the bomb client-side).
            # This is the same value before_next_page uses to score the round, so
            # the live reveal always matches what's actually paid.
            bomb_index=player.bret_bomb_index,
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.bret_boxes_collected >= player.bret_bomb_index:
            player.bret_bomb_hit = True
            player.bret_payoff = 0.0
        else:
            player.bret_bomb_hit = False
            player.bret_payoff = player.bret_boxes_collected * C.BRET_BOX_VALUE


class EckelGrossman(Page):
    form_model = "player"
    form_fields = ['eg_lottery_choice']

    @staticmethod
    def is_displayed(player):
        return player.risk_task == 'EckelGrossman'

    @staticmethod
    def vars_for_template(player):
        lotteries = []
        for j in range(C.EG_NUM_LOTTERIES):
            lo = C.EG_SURE_PAYOFF - C.EG_DELTA_LO * j
            hi = C.EG_SURE_PAYOFF + C.EG_DELTA_HI * j
            lotteries.append(dict(index=j + 1, lo=f"{lo:.2f}", hi=f"{hi:.2f}"))
        return dict(
            lotteries=lotteries,
            prob_lo=f"{1 - C.EG_PROBABILITY_HIGH:.0%}",
            prob_hi=f"{C.EG_PROBABILITY_HIGH:.0%}",
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        j = player.eg_lottery_choice - 1
        lo = C.EG_SURE_PAYOFF - C.EG_DELTA_LO * j
        hi = C.EG_SURE_PAYOFF + C.EG_DELTA_HI * j
        outcome_to_pay = 'high' if random.random() < C.EG_PROBABILITY_HIGH else 'low'

        player.eg_outcome_lo = lo
        player.eg_outcome_hi = hi
        player.eg_outcome_to_pay = outcome_to_pay
        player.eg_payoff = hi if outcome_to_pay == 'high' else lo


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

        # Only one of the three risk elicitation methods (demographics.before_next_page)
        # was actually shown to this participant - pull the bonus (and the details
        # needed to explain it) from whichever one that was.
        risk_task = player.risk_task
        if risk_task == 'HoltLaury':
            risk_bonus = player.hl_payoff
        elif risk_task == 'BRET':
            risk_bonus = player.bret_payoff
        else:
            risk_bonus = player.eg_payoff

        # Total = task-app bonus (belief accuracy or investment choice, depending
        # on the incentive condition) + the one risk-task bonus.
        total_bonus = task_bonus + risk_bonus

        return dict(
            incentive=incentive,
            bonus_period=player.participant.bonusperiod,
            asset=asset,
            task_bonus=f"{task_bonus:.2f}",
            risk_task=risk_task,
            risk_bonus=f"{risk_bonus:.2f}",
            hl_index_to_pay=player.hl_index_to_pay if risk_task == 'HoltLaury' else None,
            hl_option_chosen=player.hl_option_chosen if risk_task == 'HoltLaury' else None,
            bret_boxes_collected=player.bret_boxes_collected if risk_task == 'BRET' else None,
            bret_bomb_hit=player.bret_bomb_hit if risk_task == 'BRET' else None,
            bret_box_value=f"{C.BRET_BOX_VALUE:.2f}",
            eg_lottery_choice=player.eg_lottery_choice if risk_task == 'EckelGrossman' else None,
            eg_outcome_to_pay=player.eg_outcome_to_pay if risk_task == 'EckelGrossman' else None,
            total_bonus=f"{total_bonus:.2f}",
        )

page_sequence = [demographics, HoltLaury, BRET, EckelGrossman, completioncode]

