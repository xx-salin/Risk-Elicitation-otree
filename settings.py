from os import environ



## testing mode (True, False)
TESTING_MODE = True



# HIGH STAKES MULTIPLIER
# "high" = payoffs scaled by STAKES_FACTOR_F * (lower bound of their answer to STAKES_SOURCE_FIELD on the Elicit_Wealth page)
# "Low" = payoffs unscaled (multiplier 1)
# STAKES_SOURCE_FIELD: "Demographics_Household_Income", "Demographics_LiquidWealth", "Demographics_IlliquidWealth", "Demographics_DebtWealth"

STAKES_FACTOR_F = 2.0
STAKES_SOURCE_FIELD = "Demographics_LiquidWealth"
#####



# NUMBER OF SITUATIONS PER ROUND
# how many rows are read per distribution from Distributions.xlsx 
NUM_SITUATIONS = 11
#####


# BELIEF FREQUENCY THRESHOLD
# Tolerance band (e.g. 0.05 = +/-5%) around the correct answer within which a belief guess (Average_Guess_Alt1/2, Prob_1_Guess_Alt1/2) still counts as correct for the bonus payment.
GUESS_TOLERANCE = 0.05
#####



SESSION_CONFIGS = [
     dict(
         name='states',
         app_sequence=['setup','task','demographics','studyend'],
         num_demo_participants=16,
     ),
]


SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc="",
    testing=TESTING_MODE,
    stakes_factor_f=STAKES_FACTOR_F,
    stakes_source_field=STAKES_SOURCE_FIELD,
    num_situations=NUM_SITUATIONS,
    guess_tolerance=GUESS_TOLERANCE,
)

PARTICIPANT_FIELDS = ["Bonus", "bonusperiod", "BonusChoice", "random_draw", "treatment", "incentive", "stakes", "stakes_multiplier", "belieftable", "tuplesorder", "frequentbetterA","payoffsA", "payoffsB", "situation_order_a", "situation_order_b", "dependence_variation", "freq_thres_l", "freq_thres_h", "tail_thres_l", "tail_thres_h", "wealth_W", "color_treatment", "axis_scale"]
SESSION_FIELDS = []

# ISO-639 code
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '3825810478050'
