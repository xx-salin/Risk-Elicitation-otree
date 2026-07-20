from os import environ

# Set to True to show a "Skip for testing" button on every page that
# Set back to False before
TESTING_MODE = True

# High-stakes multiplier: for participants in the "high" stakes condition, payoffs are scaled by STAKES_FACTOR_F * (lower bound of their answer to STAKES_SOURCE_FIELD on the Elicit_Wealth page). 
# # "Low" stakes leaves payoffs unscaled (multiplier 1). 
# Change STAKES_SOURCE_FIELD to any of: "Demographics_Household_Income", "Demographics_LiquidWealth", "Demographics_IlliquidWealth", "Demographics_DebtWealth"
# (see setup/__init__.py's C.WEALTH_LOWER_BOUNDS for the bracket->lower bound mapping used for each).

# high-stakes multiplier settings
STAKES_FACTOR_F = 2.0
STAKES_SOURCE_FIELD = "Demographics_LiquidWealth"

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
)

PARTICIPANT_FIELDS = ["Bonus", "bonusperiod", "BonusChoice", "random_draw", "treatment", "incentive", "stakes", "stakes_multiplier", "belieftable", "tuplesorder", "frequentbetterA","payoffsA", "payoffsB", "attention_check_number"]
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
