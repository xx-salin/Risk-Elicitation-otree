from os import environ

# Set to True to show a "Skip for testing" button on every page that
# Set back to False before
TESTING_MODE = True

SESSION_CONFIGS = [
     dict(
         name='states',
         app_sequence=['setup','task','demographics','studyend'],
         num_demo_participants=16,
     ),
]

# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc="",
    testing=TESTING_MODE,
)

PARTICIPANT_FIELDS = ["Bonus", "bonusperiod", "BonusChoice", "random_draw", "treatment", "incentive", "belieftable", "tuplesorder", "frequentbetterA","payoffsA", "payoffsB"]
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
