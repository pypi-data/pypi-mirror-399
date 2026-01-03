

import datetime
from dateutil.relativedelta import relativedelta


ZERO_YEAR_AGO = datetime.date.today()
ONE_YEAR_AGO = ZERO_YEAR_AGO - relativedelta(years=1)
TWO_YEAR_AGO = ZERO_YEAR_AGO - relativedelta(years=2)
THREE_YEAR_AGO = ZERO_YEAR_AGO - relativedelta(years=3)
FOUR_YEAR_AGO = ZERO_YEAR_AGO - relativedelta(years=4)
FIVE_YEAR_AGO = ZERO_YEAR_AGO - relativedelta(years=5)
