from os import environ



## testing mode (True, False)
TESTING_MODE = True



# HIGH STAKES MULTIPLIER
# High-stakes multiplier: for participants in the "high" stakes condition, payoffs are scaled by STAKES_FACTOR_F * (lower bound of their answer to STAKES_SOURCE_FIELD on the Elicit_Wealth page)
# # "Low" stakes leaves payoffs unscaled (multiplier 1)
# Change STAKES_SOURCE_FIELD to any of: "Demographics_Household_Income", "Demographics_LiquidWealth", "Demographics_IlliquidWealth", "Demographics_DebtWealth" (see setup/__init__.py's C.WEALTH_LOWER_BOUNDS for the bracket->lower bound mapping used for each).

STAKES_FACTOR_F = 2.0
STAKES_SOURCE_FIELD = "Demographics_LiquidWealth"
#####



# NUMBER OF SITUATIONS PER ROUND
# This single value controls: how many rows are read per distribution from Distributions.xlsx (setup/__init__.py), the "N possible situations" wording shown to participants (task app templates), and the denominators used when checking belief-guess accuracy (task/__init__.py).
# Distributions.xlsx must have at least this many situation rows for every distribution column (D1, D2, ...) on its "All" sheet.
NUM_SITUATIONS = 11
#####






# BELIEF FREQUENCY THRESHOLD
# Tolerance band (as a fraction, e.g. 0.05 = +/-5%) around the correct answer within which a belief guess (Average_Guess_Alt1/2, Prob_1_Guess_Alt1/2) still counts as correct for the bonus payment. Used throughout task/__init__.py's NextRound page.
GUESS_TOLERANCE = 0.05
#####



SESSION_CONFIGS = [
     dict(
         name='states',
         app_sequence=['setup','task','demographics','studyend'],
         num_demo_participants=16,
     ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config, e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc="",
    testing=TESTING_MODE,
    stakes_factor_f=STAKES_FACTOR_F,
    stakes_source_field=STAKES_SOURCE_FIELD,
    num_situations=NUM_SITUATIONS,
    guess_tolerance=GUESS_TOLERANCE,
)

PARTICIPANT_FIELDS = ["Bonus", "bonusperiod", "BonusChoice", "random_draw", "treatment", "incentive", "stakes", "stakes_multiplier", "belieftable", "tuplesorder", "frequentbetterA","payoffsA", "payoffsB", "situation_order_a", "situation_order_b", "dependence_variation", "freq_thres_l", "tail_thres_l", "tail_thres_h", "attention_check_number", "wealth_W", "color_treatment"]
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '3825810478050'
