from otree.api import *
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'setup'
    # 8 so that every cell of the 2x2x2 design (treatment x incentive x stakes) appears exactly once per group.
    PLAYERS_PER_GROUP = 8
    NUM_ROUNDS = 1
    #attentionchecks
    SAMPLE_FRUITS = ['C', 'R', 'Z', 'V', 'Y', 'N', 'R', 'P']
    SAMPLE_IAMX = [1, 2, 3]
    # elicit_wealth
    CURRENCIES = {'AUD': 'A$', 'GBP': '£', 'EUR': '€', 'USD': '$'}
    DEFAULT_CURRENCY = 'GBP'  # ADJUST THIS ONE
    DEFAULT_CURRENCY_SYMBOL = CURRENCIES[DEFAULT_CURRENCY]

    # Lower bound (in DEFAULT_CURRENCY units) of each choice index, per
    # elicit_wealth question. Used to compute the high-stakes multiplier:
    # multiplier = STAKES_FACTOR_F (settings.py) * this lower bound, for
    # whichever field STAKES_SOURCE_FIELD (settings.py) names.
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


#####!!!!
    Demographics_LiquidityConstraints_1 = models.IntegerField(
        label='Please assess the following statement: "I would be able to spend more today by using my disposable income."',
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, 'Strongly disagree'], [2, 'Disagree'], [3, 'Neutral'],
            [4, 'Agree'], [5, 'Strongly agree'], [6, 'Do not know'], [7, 'Prefer not to say'],
        ])

    Demographics_LiquidityConstraints_2 = models.IntegerField(
        label='Please assess the following statement: "I would be able to spend more today by using my net wealth (e.g., savings invested in bank accounts or stocks)."',
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, 'Strongly disagree'], [2, 'Disagree'], [3, 'Neutral'],
            [4, 'Agree'], [5, 'Strongly agree'], [6, 'Do not know'], [7, 'Prefer not to say'],
        ])

    Demographics_LiquidityConstraints_3 = models.IntegerField(
        label='Please assess the following statement: "I would be able to spend more today by borrowing money (e.g., using consumer credit).”',
        widget=widgets.RadioSelectHorizontal,
        choices=[
            [1, 'Strongly disagree'], [2, 'Disagree'], [3, 'Neutral'],
            [4, 'Agree'], [5, 'Strongly agree'], [6, 'Do not know'], [7, 'Prefer not to say'],
        ])
####!!!!


# FUNCTIONS
def creating_session(subsession):
    for group in subsession.get_groups():
        tuples_variations = [[[0.0, 0.2], [0.2, 0.4], [0.4, 0.6], [0.6, 0.8], [0.8, 1.0], [1.0, 1.2], [1.2, 1.4], [1.4, 1.6],[1.6, 1.8], [1.8, 2.0], [2, 0]],
                  [[0.0, 0.15], [0.2, 0.35], [0.4, 0.55], [0.6, 0.75], [0.8, 0.95], [1.0, 1.15], [1.2, 1.35], [1.4, 1.55], [1.6, 1.75], [1.8, 1.95], [2, 0]],
                  [[0.0, 0.25], [0.2, 0.45], [0.4, 0.65], [0.6, 0.85], [0.8, 1.05], [1.0, 1.25], [1.2, 1.45], [1.4, 1.65], [1.6, 1.85], [1.8, 2.05], [2, 0]],
                  [[0.0, 0.15], [0.25, 0.35], [0.45, 0.55], [0.65, 0.75], [0.85, 1.0], [1.0, 1.25], [1.15, 1.45], [1.35, 1.65], [1.55, 1.85], [1.75, 2.0], [2, 0]],
                  [[0.0, 0.25], [0.15, 0.45], [0.35, 0.65], [0.55, 0.85], [0.75, 1.0], [1.0, 1.15], [1.25, 1.35], [1.45, 1.55], [1.65, 1.75], [1.85, 2.0], [2, 0]]
                  ]
        tuples_order = [0,1,2,3,4] #0: equalmargins, 1: FO_FOSDominated, 2: FOSDominates, 3: FO_MoreRisky, 4: FO_LessRisky
        random.shuffle(tuples_order)
        frequentbetterA = []
        payoffsA = []
        payoffsB = []
        for i in range(5):
            helpA = []
            helpB = []
            AorB = random.choice([0, 1])
            frequentbetterA.append(AorB)
            tuples = tuples_variations[tuples_order[i]]
            random.shuffle(tuples)
            j = 0
            while j < 11:
                helpA.append(tuples[j][AorB])
                helpB.append(tuples[j][1 - AorB])
                j = j + 1
            payoffsA.append(helpA)
            payoffsB.append(helpB)
        players = group.get_players()
        for player in players:
            player.participant.tuplesorder = tuples_order
            player.participant.frequentbetterA = frequentbetterA
            player.participant.payoffsA = payoffsA
            player.participant.payoffsB = payoffsB
            player.fruit = random.choice(C.SAMPLE_FRUITS)
            order_images = C.SAMPLE_IAMX.copy()
            random.shuffle(order_images)
            player.iamx1 = order_images[0]
            player.iamx2 = order_images[1]
            player.iamx3 = order_images[2]
            # 2x2x2 design, balanced once per group of 8:
            # chart display treatment: sequential_joint reveals situations
            # one at a time; simultaneous_joint shows all 11 at once.
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
# stakes: low keeps payoffs as generated above; high scales them by STAKES_FACTOR_F * (lower bound of the participant's answerto STAKES_SOURCE_FIELD on Elicit_Wealth). 
# The multiplier itself is computed once that answer is known, in Elicit_Wealth.before_next_page below; default to 1 until then.
            if player in players[:2] or player in players[4:6]:
                player.participant.stakes = "low"
            else:
                player.participant.stakes = "high"
            player.participant.stakes_multiplier = 1
            player.participant.belieftable = 1
            player.participant.bonusperiod = random.randint(1, 5)
            # only one of AttentionCheck1-4 is shown per participant
            player.participant.attention_check_number = random.randint(1, 4)

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
        player.checks = player.attention1

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.participant.attention_check_number == 1

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
        player.checks = player.attention2

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.participant.attention_check_number == 2

class AttentionCheck3(Page):
    form_model = 'player'
    form_fields = ['answer_iamx']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.participant.attention_check_number == 3

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
        player.checks = player.attention3


class AttentionCheck4(Page):
    form_model = 'player'
    form_fields = ['answer_her']

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1 and player.participant.attention_check_number == 4

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if player.answer_her == 1:
            player.attention4 = 1
        else:
            player.attention4 = 0
        player.checks = player.attention4


class AttentionCheckResult(Page):
    form_model = "player"

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

class Instructions(Page):
    form_model = "player"

    @staticmethod
    def is_displayed(player: Player):
        return player.round_number == 1

page_sequence = [Welcome, LeavePage, ProlificID, BotScreening, AttentionCheck1, AttentionCheck2, AttentionCheck3, AttentionCheck4, AttentionCheckResult, Elicit_Wealth, Instructions]
#page_sequence = [Welcome, LeavePage, ProlificID, Instructions]

