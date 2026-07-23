from otree.api import *
import random
from pathlib import Path
from openpyxl import load_workbook
from task import C as TaskC 

doc = """
Your app description
"""

DISTRIBUTIONS_FILE = Path(__file__).resolve().parent.parent / "Distributions.xlsx"

class C(BaseConstants):
    NAME_IN_URL = 'setup'
    # 8 so that every cell of the 2x2x2 design (treatment x incentive x stakes) appears once per group.
    PLAYERS_PER_GROUP = 8
    NUM_ROUNDS = 1
    #attentionchecks
    SAMPLE_FRUITS = ['C', 'R', 'Z', 'V', 'Y', 'N', 'R', 'P']
    SAMPLE_IAMX = [1, 2, 3]
    # elicit_wealth
    CURRENCIES = {'AUD': 'A$', 'GBP': '£', 'EUR': '€', 'USD': '$'}
    DEFAULT_CURRENCY = 'GBP'  # ADJUST THIS ONE
    DEFAULT_CURRENCY_SYMBOL = CURRENCIES[DEFAULT_CURRENCY]

    # Lower bound (in DEFAULT_CURRENCY units) of each choice index, per elicit_wealth question. Used to compute the high-stakes multiplier:
    # "Prefer not to say" maps to 0 (no stakes boost).
    WEALTH_LOWER_BOUNDS = {
        "Demographics_Household_Income": {0: 0, 1: 0, 2: 10000, 3: 20000, 4: 40000, 5: 80000, 6: 160000, 7: 320000, 8: 0},
        "Demographics_LiquidWealth":      {0: 0, 1: 0, 2: 5000, 3: 10000, 4: 15000, 5: 20000, 6: 25000, 7: 0},
        "Demographics_IlliquidWealth":    {0: 0, 1: 0, 2: 20000, 3: 40000, 4: 80000, 5: 160000, 6: 320000, 7: 640000, 8: 0},
        "Demographics_DebtWealth":        {0: 0, 1: 0, 2: 20000, 3: 40000, 4: 80000, 5: 160000, 6: 320000, 7: 640000, 8: 0},
    }


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass

class Player(BasePlayer):
    isLeaving = models.BooleanField(choices=((True, 'leaving'), (False, 'notleaving')), initial=0)
    prolificID = models.StringField(
        label="Please enter your Prolific ID so that we can match your payment."
    )
    #attentionchecks
    attention1 = models.IntegerField(initial=2)
    attention2 = models.IntegerField(initial=2)
    attention3 = models.IntegerField(initial=2)
    attention4 = models.IntegerField(initial=2)
    checks = models.IntegerField(initial=2)
    honolulu = models.StringField(
        label='Please type the word above into the space below:', max_length=8
    )
    fruit = models.StringField(initial='blank')
    answer_fruit = models.StringField(label='', max_length=1)
    iamx1 = models.IntegerField(initial=0)
    iamx2 = models.IntegerField(initial=0)
    iamx3 = models.IntegerField(initial=0)
    answer_iamx = models.IntegerField(
        label='Which of the sentences above most accurately describes you?',
        choices=[1, 2, 3],
        widget=widgets.RadioSelect,
    )
    answer_her = models.IntegerField(
        label='',
        choices=[[1, "Tatyana's mother"], [2, "Grandma"], [3, "Tatyana"]],
        widget=widgets.RadioSelect,
    )

    # elicit_wealth
    Demographics_Household_Income = models.IntegerField(
        label='Which of the following best describes your total household income last year?',
        widget=widgets.RadioSelect(),
        choices=[
            [0, f"{C.DEFAULT_CURRENCY_SYMBOL}0"],
            [1, f"Less than {C.DEFAULT_CURRENCY_SYMBOL}10,000"],
            [2, f"Between {C.DEFAULT_CURRENCY_SYMBOL}10,000 and {C.DEFAULT_CURRENCY_SYMBOL}20,000"],
            [3, f"Between {C.DEFAULT_CURRENCY_SYMBOL}20,000 and {C.DEFAULT_CURRENCY_SYMBOL}40,000"],
            [4, f"Between {C.DEFAULT_CURRENCY_SYMBOL}40,000 and {C.DEFAULT_CURRENCY_SYMBOL}80,000"],
            [5, f"Between {C.DEFAULT_CURRENCY_SYMBOL}80,000 and {C.DEFAULT_CURRENCY_SYMBOL}160,000"],
            [6, f"Between {C.DEFAULT_CURRENCY_SYMBOL}160,000 and {C.DEFAULT_CURRENCY_SYMBOL}320,000"],
            [7, f"{C.DEFAULT_CURRENCY_SYMBOL}320,000 or more"],
            [8, "Prefer not to say"]
        ])

    Demographics_LiquidWealth = models.IntegerField(
        label='How much easily accessible savings do you own (e.g., money on bank accounts, investments in mutual funds or stocks, or other financial wealth)?',
        widget=widgets.RadioSelect(),
        choices=[
            [0, f"{C.DEFAULT_CURRENCY_SYMBOL}0"],
            [1, f"Less than {C.DEFAULT_CURRENCY_SYMBOL}5,000"],
            [2, f"Between {C.DEFAULT_CURRENCY_SYMBOL}5,000 and {C.DEFAULT_CURRENCY_SYMBOL}10,000"],
            [3, f"Between {C.DEFAULT_CURRENCY_SYMBOL}10,000 and {C.DEFAULT_CURRENCY_SYMBOL}15,000"],
            [4, f"Between {C.DEFAULT_CURRENCY_SYMBOL}15,000 and {C.DEFAULT_CURRENCY_SYMBOL}20,000"],
            [5, f"Between {C.DEFAULT_CURRENCY_SYMBOL}20,000 and {C.DEFAULT_CURRENCY_SYMBOL}25,000"],
            [6, f"{C.DEFAULT_CURRENCY_SYMBOL}25,000 or more"],
            [7, "Prefer not to say"]
        ])

    Demographics_IlliquidWealth = models.IntegerField(
        label='How much other wealth do you own (e.g., value of your home, other real estate you own, or other non-financial assets)?',
        widget=widgets.RadioSelect(),
        choices=[
            [0, f"{C.DEFAULT_CURRENCY_SYMBOL}0"],
            [1, f"Less than {C.DEFAULT_CURRENCY_SYMBOL}20,000"],
            [2, f"Between {C.DEFAULT_CURRENCY_SYMBOL}20,000 and {C.DEFAULT_CURRENCY_SYMBOL}40,000"],
            [3, f"Between {C.DEFAULT_CURRENCY_SYMBOL}40,000 and {C.DEFAULT_CURRENCY_SYMBOL}80,000"],
            [4, f"Between {C.DEFAULT_CURRENCY_SYMBOL}80,000 and {C.DEFAULT_CURRENCY_SYMBOL}160,000"],
            [5, f"Between {C.DEFAULT_CURRENCY_SYMBOL}160,000 and {C.DEFAULT_CURRENCY_SYMBOL}320,000"],
            [6, f"Between {C.DEFAULT_CURRENCY_SYMBOL}320,000 and {C.DEFAULT_CURRENCY_SYMBOL}640,000"],
            [7, f"{C.DEFAULT_CURRENCY_SYMBOL}640,000 or more"],
            [8, "Prefer not to say"]
        ])

    Demographics_DebtWealth = models.IntegerField(
        label='How much debt do you owe (e.g., mortgages, credit card debt, or lines of credit)?',
        widget=widgets.RadioSelect(),
        choices=[
            [0, f"{C.DEFAULT_CURRENCY_SYMBOL}0"],
            [1, f"Less than {C.DEFAULT_CURRENCY_SYMBOL}20,000"],
            [2, f"Between {C.DEFAULT_CURRENCY_SYMBOL}20,000 and {C.DEFAULT_CURRENCY_SYMBOL}40,000"],
            [3, f"Between {C.DEFAULT_CURRENCY_SYMBOL}40,000 and {C.DEFAULT_CURRENCY_SYMBOL}80,000"],
            [4, f"Between {C.DEFAULT_CURRENCY_SYMBOL}80,000 and {C.DEFAULT_CURRENCY_SYMBOL}160,000"],
            [5, f"Between {C.DEFAULT_CURRENCY_SYMBOL}160,000 and {C.DEFAULT_CURRENCY_SYMBOL}320,000"],
            [6, f"Between {C.DEFAULT_CURRENCY_SYMBOL}320,000 and {C.DEFAULT_CURRENCY_SYMBOL}640,000"],
            [7, f"{C.DEFAULT_CURRENCY_SYMBOL}640,000 or more"],
            [8, "Prefer not to say"]
        ])



# FUNCTIONS


# SPOT 1: to change the marginal outcomes for a distribution edit the numbers directly in Distributions.xlsx 
# "Variation 1" (50%) / "Variation 2.1" (25%) / "Variation 2.2" (25%)


def _load_outcome_table(ws, header_row, num_situations):
    """
    Read the 'D1', 'D2', ... header at 1-indexed row `header_row` on `ws` and
    the `num_situations` data rows immediately below it. Returns a list of
    distributions, each a list of `num_situations` [option_1, option_2] pairs.
    """
    rows = list(ws.iter_rows(values_only=True))
    header = rows[header_row - 1]  # e.g. (None, 'D1', None, 'D2', None, 'D3', ...)
    data_rows = rows[header_row : header_row + num_situations]

    distributions = []
    col = 1
    while col < len(header) and header[col] is not None:
        pairs = [[row[col], row[col + 1]] for row in data_rows]
        if len(pairs) < num_situations or any(a is None or b is None for a, b in pairs):
            raise ValueError(
                f"Distributions.xlsx column '{header[col]}' starting at row {header_row} on "
                f"the 'All' sheet doesn't have {num_situations} filled-in rows (NUM_SITUATIONS "
                f"in settings.py). Add more rows to the sheet or lower NUM_SITUATIONS."
            )
        distributions.append(pairs)
        col += 2
    return distributions


def _find_variation_header_row(ws, variation_label):
    """
    Locate a "Variation 2.x" block on the "All" sheet by its section label in
    column A (e.g. "Variation 2.1: Random allocation..."), and return the
    1-indexed row of the 'D1', 'D2', ... header below it. Follows the sheet's
    layout convention: label row, one blank row, then the header row.
    """
    for (cell,) in ws.iter_rows(min_col=1, max_col=1):
        if isinstance(cell.value, str) and cell.value.startswith(variation_label):
            return cell.row + 2
    raise ValueError(
        f"Distributions.xlsx 'All' sheet: no section labeled '{variation_label}' found in column A."
    )


def load_distributions(num_situations):
    """
    Read every distribution (D1, D2, ...) from Distributions.xlsx's "All" sheet's
    original table. Returns a list of distributions, each a list of
    `num_situations` [option_1, option_2] pairs, in their original row pairing.
    """
    wb = load_workbook(DISTRIBUTIONS_FILE, data_only=True)
    ws = wb["All"]
    return _load_outcome_table(ws, header_row=2, num_situations=num_situations)


def load_locked_distributions(num_situations, variation_label):
    """
    Read every distribution from one of the "All" sheet's fixed-pairing blocks
    (variation_label="Variation 2.1" or "Variation 2.2"). Unlike
    load_distributions(), these already encode one specific, deterministic
    [option_1, option_2] pairing per situation - the "locked" structure of
    dependence described in creating_session() below.
    """
    wb = load_workbook(DISTRIBUTIONS_FILE, data_only=True)
    ws = wb["All"]
    header_row = _find_variation_header_row(ws, variation_label)
    return _load_outcome_table(ws, header_row=header_row, num_situations=num_situations)


def load_round_thresholds():
    """
    Read the per-distribution FREQ_THRES_L / FREQ_THRES_H / TAIL_THRES_L /
    TAIL_THRES_H values from the "All" sheet's "Round Thresholds" block. The
    same threshold is used for both alternatives in a round, but the value can
    differ by distribution (D1..D10) - see creating_session() below for how the
    right value is picked for a given round based on which distribution it draws.
    Returns {"FREQ_THRES_L": [...], "FREQ_THRES_H": [...], "TAIL_THRES_L": [...],
    "TAIL_THRES_H": [...]}, each a list with one value per distribution, in
    D1..Dn column order.
    """
    wb = load_workbook(DISTRIBUTIONS_FILE, data_only=True)
    ws = wb["All"]
    header_row = _find_variation_header_row(ws, "Round Thresholds")
    rows = list(ws.iter_rows(values_only=True))
    header = rows[header_row - 1]

    cols = []
    col = 1
    while col < len(header) and header[col] is not None:
        cols.append(col)
        col += 2

    thresholds = {}
    for label in ("FREQ_THRES_L", "FREQ_THRES_H", "TAIL_THRES_L", "TAIL_THRES_H"):
        row = next((r for r in rows[header_row : header_row + 10] if r and r[0] == label), None)
        if row is None:
            raise ValueError(
                f"Distributions.xlsx 'All' sheet: no row labeled '{label}' found under "
                f"the 'Round Thresholds' header (row {header_row})."
            )
        values = [row[c] for c in cols]
        if not cols or any(v is None for v in values):
            raise ValueError(
                f"Distributions.xlsx 'Round Thresholds' row '{label}' is missing a value "
                f"for one of its {len(cols)} distribution columns."
            )
        thresholds[label] = values
    return thresholds


def creating_session(subsession):


    # SPOT 2: to change the number of situations per round, edit NUM_SITUATIONS in settings.py.

    num_situations = subsession.session.config["num_situations"]
    # D1-D5 = Volatility-sheet distributions (alternating high/low volatility), D6-D10 = Skewness-sheet distributions (alternating positive/negative skew)
    tuples_variations = load_distributions(num_situations)
    locked_21_variations = load_locked_distributions(num_situations, "Variation 2.1")
    locked_22_variations = load_locked_distributions(num_situations, "Variation 2.2")

    # Per-distribution FREQ_THRES_L/H TAIL_THRES_L/H (Distributions.xlsx "All" sheet)
    round_thresholds = load_round_thresholds()
    for group in subsession.get_groups():

        # one distribution per round, drawn without replacement
        tuples_order = random.sample(range(len(tuples_variations)), TaskC.NUM_ROUNDS)
        frequentbetterA = []
        payoffsA = []
        payoffsB = []

        # This round's threshold values, looked up per round from round_thresholds
        freq_thres_l_list = []
        freq_thres_h_list = []
        tail_thres_l_list = []
        tail_thres_h_list = []

        # For each round, the order in which each alternative's outcomes end up displayed.
        situation_order_a = []
        situation_order_b = []

        # Which structure-of-dependence variation was used each round: 
        # "1" = outcomes independently shuffled per alternative (dependence broken up)
        # "2.1"/"2.2" = one of the two fixed pairings 
        # Drawn per round with 50% / 25% / 25% probability respectively.

        dependence_variation = []
        for i in range(TaskC.NUM_ROUNDS):
            AorB = random.choice([0, 1])
            frequentbetterA.append(AorB)

            variation = random.choices(["1", "2.1", "2.2"], weights=[0.5, 0.25, 0.25])[0]
            dependence_variation.append(variation)

            dist_idx = tuples_order[i]
            freq_thres_l_list.append(round_thresholds["FREQ_THRES_L"][dist_idx])
            freq_thres_h_list.append(round_thresholds["FREQ_THRES_H"][dist_idx])
            tail_thres_l_list.append(round_thresholds["TAIL_THRES_L"][dist_idx])
            tail_thres_h_list.append(round_thresholds["TAIL_THRES_H"][dist_idx])

            if variation == "1":
                tuples = list(tuples_variations[tuples_order[i]])
                values_a = [pair[AorB] for pair in tuples]
                values_b = [pair[1 - AorB] for pair in tuples]

                order_a = list(range(1, num_situations + 1))
                random.shuffle(order_a)
                order_b = list(range(1, num_situations + 1))
                random.shuffle(order_b)

                situation_order_a.append(order_a)
                situation_order_b.append(order_b)
                payoffsA.append([values_a[r - 1] for r in order_a])
                payoffsB.append([values_b[r - 1] for r in order_b])
            else:
                locked_variations = locked_21_variations if variation == "2.1" else locked_22_variations
                tuples = list(locked_variations[tuples_order[i]])

                order = list(range(1, num_situations + 1))
                random.shuffle(order)

                situation_order_a.append(order)
                situation_order_b.append(order)
                payoffsA.append([tuples[r - 1][AorB] for r in order])
                payoffsB.append([tuples[r - 1][1 - AorB] for r in order])

        # "Initial wealth" offset added to bonus payoffs
        drawn_payoffs = [v for lst in payoffsA + payoffsB for v in lst]
        wealth_W = max(0, -min(drawn_payoffs))
        players = group.get_players()
        for player in players:
            player.participant.tuplesorder = tuples_order
            player.participant.frequentbetterA = frequentbetterA
            player.participant.payoffsA = payoffsA
            player.participant.payoffsB = payoffsB
            player.participant.situation_order_a = situation_order_a
            player.participant.situation_order_b = situation_order_b
            player.participant.dependence_variation = dependence_variation
            player.participant.freq_thres_l = freq_thres_l_list
            player.participant.freq_thres_h = freq_thres_h_list
            player.participant.tail_thres_l = tail_thres_l_list
            player.participant.tail_thres_h = tail_thres_h_list
            player.participant.wealth_W = wealth_W
            player.fruit = random.choice(C.SAMPLE_FRUITS)
            order_images = C.SAMPLE_IAMX.copy()
            random.shuffle(order_images)
            player.iamx1 = order_images[0]
            player.iamx2 = order_images[1]
            player.iamx3 = order_images[2]

# 2x2x2 design, balanced once per group of 8:
# chart display treatment: sequential_joint vs simultaneous_joint
            if player in players[:4]:
                player.participant.treatment = "sequential_joint"
            else:
                player.participant.treatment = "simultaneous_joint"
            if (
                player in players[:1] or player in players[2:3]
                or player in players[4:5] or player in players[6:7]
            ):
                player.participant.incentive = "beliefs"
            else:
                player.participant.incentive = "choice"

# stakes: low vs high
            if player in players[:2] or player in players[4:6]:
                player.participant.stakes = "low"
            else:
                player.participant.stakes = "high"
            player.participant.stakes_multiplier = 1
            player.participant.belieftable = 1
            player.participant.bonusperiod = random.randint(1, 10)
            # independent per-participant coin flip (not part of the 2x2x2 design above): 0 = color-coded, 1 = neutral color.
            player.participant.color_treatment = random.randint(0, 1)

# PAGES
class Elicit_Wealth(Page):
    form_model = 'player'
    form_fields = [
        "Demographics_Household_Income",
        "Demographics_LiquidWealth",
        "Demographics_IlliquidWealth",
        "Demographics_DebtWealth"
    ]

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        return {'testing': player.session.config["testing"]}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.participant.stakes == "high":
            source_field = player.session.config["stakes_source_field"]
            answer = getattr(player, source_field)
            lower_bound = C.WEALTH_LOWER_BOUNDS[source_field].get(answer, 0)
            player.participant.stakes_multiplier = player.session.config["stakes_factor_f"] * lower_bound
        else:
            player.participant.stakes_multiplier = 1


class Welcome(Page):
    form_model = "player"
    form_fields = ['isLeaving']

    @staticmethod
    def is_displayed(player):
        return player.round_number==1

class LeavePage(Page):
    form_model = "player"

    @staticmethod
    def is_displayed(player):
        return player.isLeaving

class ProlificID(Page):
    form_model = "player"
    form_fields = ["prolificID"]

    def error_message(player, values):
        length = values["prolificID"]
        if len(length) < 24 or len(length) > 24:
            return "Your Prolific ID consists of 24 characters."

    @staticmethod
    def is_displayed(player):
        #arrays = assign_arrays(player)
        #player.participant.payoffsA = arrays[0]
        #player.participant.payoffsB = arrays[1]
        return player.round_number==1

class BotScreening(Page):
    form_model = "player"

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class AttentionCheck1(Page):
    form_model = 'player'
    form_fields = ['honolulu']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        answer1 = player.honolulu
        if answer1.upper() == "HONOLULU":
            player.attention1 = 1
        else:
            player.attention1 = 0

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class AttentionCheck2(Page):
    form_model = 'player'
    form_fields = ['answer_fruit']

    @staticmethod
    def vars_for_template(player: Player):
        fruitletter = dict(
            dict(
                zip(
                    ['C', 'R', 'Z', 'V', 'Y', 'N', 'R', 'P'],
                    [
                        'apple',
                        'strawberry',
                        'mango',
                        'raspberry',
                        'blueberry',
                        'blackberry',
                        'avocado',
                        'tangerine',
                    ],
                )
            )
        )
        for i in fruitletter:
            if player.fruit == i:
                return dict(
                    fruit = fruitletter.get(i),
                )

    @staticmethod
    def js_vars(player: Player):
        fruitletter = dict(
            dict(
                zip(
                    ['C', 'R', 'Z', 'V', 'Y', 'N', 'R', 'P'],
                    [
                        'apple',
                        'strawberry',
                        'mango',
                        'raspberry',
                        'blueberry',
                        'blackberry',
                        'avocado',
                        'tangerine',
                    ],
                )
            )
        )

        for i in fruitletter:
            if player.fruit == i:
                return dict(
                    fruit=fruitletter.get(i),
                    fruitletter=fruitletter,
                )

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.fruit == player.answer_fruit.upper():
            player.attention2 = 1
        else:
            player.attention2 = 0

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class AttentionCheck3(Page):
    form_model = 'player'
    form_fields = ['answer_iamx']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        images = dict(
            dict(zip(['human', 'lion', 'rabbit'], [player.iamx1, player.iamx2, player.iamx3]))
        )
        return {'images': images,}

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.iamx1 == player.answer_iamx:
            player.attention3 = 1
        else:
            player.attention3 = 0


class AttentionCheck4(Page):
    form_model = 'player'
    form_fields = ['answer_her']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.answer_her == 1:
            player.attention4 = 1
        else:
            player.attention4 = 0


class AttentionCheckResult(Page):
    form_model = "player"

    @staticmethod
    def is_displayed(player: Player):
        player.checks = int(
            player.attention1 == 1
            and player.attention2 == 1
            and player.attention3 == 1
            and player.attention4 == 1
        )
        return player.round_number == 1

class Instructions(Page):
    form_model = "player"

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

    @staticmethod
    def vars_for_template(player: Player):
        # Wealth is expressed on the same scale as the outcomes the participant sees (i.e. scaled by the same stakes multiplier)
        multiplier = player.participant.stakes_multiplier
        return dict(
            wealth_W=f"{player.participant.wealth_W * multiplier:.2f}",
            stakes_factor=f"{multiplier:.2f}",
        )

page_sequence = [Welcome, LeavePage, ProlificID, BotScreening, AttentionCheck1, AttentionCheck2, AttentionCheck3, AttentionCheck4, AttentionCheckResult, Elicit_Wealth, Instructions]


