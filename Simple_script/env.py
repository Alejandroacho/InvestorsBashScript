from datetime import datetime
import pytz

INVEST_LIMIT_TO_PAY_SUBSCRIPTION = 50000
TIMEZONE = pytz.timezone("UTC")
EDGE_DATE_FOR_OLD_BILL_METRICS = datetime(2019, 4, 1, 0, 0, 0, 0, TIMEZONE)
YEARLY_SUBSCRIPTION = 3000
UPFRONT_YEARS = 5
INVOICE_STATUS = {
    'Verified': 'Verified',
    'Sent': 'Sent',
    'Paid': 'Paid',
    'Overdue':'overdue'
}