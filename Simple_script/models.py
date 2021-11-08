from datetime import datetime
import calendar
import json
import os

from env import *


CURRENT_BILL_ID = 1
CURRENT_CASH_CALL_ID = 1


class CashCall():

    def __init__(self, data):
        self.id = data['id']
        self.investor_id = data['investor_id']
        self.total_amount = data['total_amount']
        self.IBAN = data['IBAN']
        self.email_send = data['email_send']
        self.date_added = data['date_added'].strftime('%Y-%m-%d')
        self.invoice_status = data['invoice_status']
        self.year = data['year']

    def save(self, path=None):
        if not path:
            path = f'./investors_cash_calls/investor_{self.investor_id}/'
        folder_path = os.path.dirname(path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_name = f'cash_call_{self.year}.json'
        path = path + file_name
        with open(path, 'w+') as file:
            json.dump(self.__dict__, file, indent=4)

class Bill():

    def __init__(self, data):
        self.id = data['id']
        self.investor_id = data['investor_id']
        self.investment_id = data['investment_id']
        self.fees_amount = data['fees_amount']
        self.date_added = data['date_added'].strftime('%Y-%m-%d')
        self.fees_type = data['fees_type']
        self.year = data['date_added'].strftime('%Y')

    def save(self, path=None):
        if not path:
            path = f'./investors_bills/investor_{self.investor_id}/{self.year}/'
        folder_path = os.path.dirname(path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_name = f'bill_{self.id}.json'
        path = path + file_name
        with open(path, 'w+') as file:
            json.dump(self.__dict__, file, indent=4)


class SetOfBills():

    def __init__(self, investor, bills, year):
        self.investor = investor
        self.bills = bills
        self.year = year

    def validate_year_bills(self, path=None):
        global CURRENT_CASH_CALL_ID
        fees_amount = self.calculate_total_fees()
        data = {
            'id': CURRENT_CASH_CALL_ID,
            'investor_id': self.investor.id,
            'total_amount': fees_amount,
            'IBAN': self.investor.credit,
            'email_send': self.investor.email,
            'date_added': datetime.now().replace(year=int(self.bills[0].year)),
            'invoice_status': INVOICE_STATUS['Verified'],
            'year': self.bills[0].year
        }
        cash_call = CashCall(data)
        self.investor.cash_calls.append(cash_call)
        cash_call.save(path)
        CURRENT_CASH_CALL_ID += 1
        return cash_call

    def calculate_total_fees(self):
        total_fees = 0
        for bill in self.bills:
            total_fees += bill.fees_amount
        return total_fees


class Investor():

    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.email = data['email']
        self.phone = data['phone']
        self.address = data['adress']
        self.credit = data['credit']
        self.bills = []
        self.sets_of_bills = {}
        self.cash_calls = []

    def set_investments(self, investments):
        self.investments = []
        for investment in investments:
            if investment.investor_id == self.id:
                self.investments.append(investment)
        return self.investments

    def get_total_investments_by_year(self):
        investments_by_year = {}
        for investment in self.investments:
            investment_year = investment.date_added.year
            if investment_year in investments_by_year:
                investments_by_year[investment_year] += investment.invested_amount
            else:
                investments_by_year[investment_year] = investment.invested_amount
        return investments_by_year

    def must_pay_yearly_subscription(self, year):
        investments_a_year = self.get_total_investments_by_year()
        for investment_year in investments_a_year.keys():
            invested = investments_a_year[investment_year]
            if investment_year <= year and invested >= INVEST_LIMIT_TO_PAY_SUBSCRIPTION:
                return False
        return True

    def generate_bills(self, year=None, all=None, path=None):
        for investment in self.investments:
            if year and investment.date_added.year <= year:
                if all:
                    initial_year = investment.date_added.year
                    final_year = year
                    for current_year in range(initial_year, final_year + 1):
                        if investment.fees_type == "yearly":
                            investment.generate_bill(current_year, path)
                        elif investment.fees_type == "upfront" and investment.date_added.year == current_year:
                            investment.generate_bill(current_year, path)
                elif not all:
                    investment.generate_bill(year, path)
            elif all and not year:
                initial_year = investment.date_added.year
                final_year = datetime.now().year
                for current_year in range(initial_year, final_year + 1):
                    if investment.fees_type == "yearly":
                        investment.generate_bill(current_year, path)
                    elif investment.fees_type == "upfront" and investment.date_added.year == current_year:
                        investment.generate_bill(current_year, path)
        return self.bills

    def generate_sets_of_bills(self):
        for bill in self.bills:
            year = bill.year
            if year in self.sets_of_bills:
                set_of_bill = self.sets_of_bills[year]
                bills = set_of_bill.bills
                if not bill in bills:
                    set_of_bill.bills.append(bill)
            else:
                self.sets_of_bills[year] = SetOfBills(self, [bill], year)
        return self.sets_of_bills

    def verify_set_of_bills(self, year, path=None):
        set_of_bills = self.sets_of_bills[str(year)]
        cash_call = set_of_bills.validate_year_bills(path)
        self.cash_calls.append(cash_call)
        return cash_call

    def __str__(self):
        investments = [f"{str(investment)}" for investment in self.investments]
        return f"{self.name}: {str(investments)}"


class Investment():

    def __init__(self, data):
        self.id = data['id']
        self.investor_id = data['investor_id']
        self.startup_name = data['startup_name']
        self.invested_amount = data['invested_ammount']
        self.percentage_fees = data['percentage_fees']
        self.date_added = datetime.strptime(data['date_added'], '%Y-%m-%d %H:%M:%S%z')
        self.fees_type = data['fees_type']
        self.percentage = self.percentage_fees / 100

    def set_investor(self, investor):
        self.investor = investor
        return self.investor

    def generate_bill(self, year=None, path=None):
        global CURRENT_BILL_ID
        fees_amount = self.get_fees(year)
        data = {
            'id': CURRENT_BILL_ID,
            'investor_id': self.investor_id,
            'investment_id': self.id,
            'fees_amount': fees_amount,
            'date_added': self.date_added.replace(year=year),
            'fees_type': self.fees_type
        }
        bill = Bill(data)
        self.investor.bills.append(bill)
        bill.save(path)
        CURRENT_BILL_ID += 1
        return bill

    def get_fees(self, year=None):
        if self.fees_type == 'upfront':
            year = self.date_added.year
            fees_amount = self.invested_amount * self.percentage * UPFRONT_YEARS
        elif self.fees_type == 'yearly':
            if not year:
                year = datetime.now().year
            fees_amount = self.get_yearly_fees_amount(year)
        if self.investor.must_pay_yearly_subscription(year):
            fees_amount += YEARLY_SUBSCRIPTION
        return round(fees_amount,2)

    def get_yearly_fees_amount(self, year):
        if year < self.date_added.year:
            raise Exception(f'Year given {year} must be greater than {self.date_added.year}')
        years_since_investment = year - self.date_added.year
        if self.date_added < EDGE_DATE_FOR_OLD_BILL_METRICS:
            fees_amount =  self.get_fees_with_old_yearly_bill_format(years_since_investment)
        else:
            fees_amount = self.get_fees_with_current_yearly_bill_format(years_since_investment)
        return fees_amount

    def get_fees_with_old_yearly_bill_format(self, years_since_investment=0):
        if years_since_investment == 0:
            day_number = self.date_added.timetuple().tm_yday
            day_percentage = 1 - ( day_number / 365)
            fees_amount = (self.percentage * round(day_percentage,2)) * self.invested_amount
        else:
            fees_amount = self.invested_amount * self.percentage
        return fees_amount

    def get_fees_with_current_yearly_bill_format(self, years_since_investment=0):
        bill_year = self.date_added.year + years_since_investment
        if years_since_investment == 0:
            day_number = self.date_added.timetuple().tm_yday
            day_percentage = 1 - ( day_number / (366 if calendar.isleap(bill_year) else 365))
            fees_amount = (self.percentage * round(day_percentage,2)) * self.invested_amount
        elif years_since_investment == 1:
            fees_amount = self.percentage * self.invested_amount
        elif years_since_investment == 2:
            fees_amount = (self.percentage - 0.002) * self.invested_amount
        elif years_since_investment == 3:
            fees_amount = (self.percentage - 0.005) * self.invested_amount
        elif years_since_investment > 3:
            fees_amount = (self.percentage - 0.01) * self.invested_amount
        return fees_amount

    def __str__(self):
        return f"{self.date_added} | {str(self.invested_amount)} - {self.fees_type}"

