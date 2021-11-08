from datetime import datetime
import os
import shutil

from models import Investment, Investor, Bill, CashCall, SetOfBills
from utils import relationate_investors_and_investments

class AbstractClasses():

    def _abstract_investor(self, data={}):
        investor_data = {
            'id':data.get("id",1),
            'name':data.get("name","Test Investor"),
            'adress':data.get("adress","Test Address"),
            'phone':data.get("phone","123123123"),
            'email':data.get("email","test@email.com"),
            'credit':data.get("credit","VISA 16 digit\nTest Investor\n4470114627106836 04/24\nCVC:186\n")}
        investor = Investor(investor_data)
        return investor

    def _abstract_investment(self, data={}):
        investment_data = {
            'id':data.get("id",1),
            'investor_id':data.get("investor_id",1),
            "startup_name": data.get("startup_name","Santana PLC"),
            'invested_ammount': data.get("invested_ammount",48000),
            'date_added': data.get("date_added","2017-07-14 22:30:16+00:00"),
            'percentage_fees': data.get("percentage_fees",14),
            'fees_type': data.get("fees_type",'yearly')}
        investment = Investment(investment_data)
        return investment

    def _abstract_bill(self, data={}):
        bill_data = {
            'id':data.get("id",1),
            'investor_id':data.get("investor_id",1),
            'investment_id':data.get("investment_id",1),
            'fees_amount':data.get("fees_amount",6700),
            'date_added':data.get("date_added",datetime.strptime("2017-07-14 22:30:16+00:00", '%Y-%m-%d %H:%M:%S%z')),
            'fees_type':data.get("fees_type",'upfront')}
        bill = Bill(bill_data)
        return bill

    def _abstract_cashcall(self, data={}):
        bill_data = {
            'id':data.get("id",1),
            'investor_id':data.get('investor_id',1),
            'total_amount':data.get("total_amount",10000),
            'IBAN':data.get("IBAN",123123123),
            'email_send':data.get("email_send","email@test.com"),
            'date_added':data.get("date_added",datetime.strptime("2017-07-14 22:30:16+00:00", '%Y-%m-%d %H:%M:%S%z')),
            'invoice_status':data.get("invoice_status",'Verified'),
            'year':data.get('year', '2021')}
        bill = CashCall(bill_data)
        return bill

    def _abstract_set_of_bill(self, data={}):
        bill1 = self._abstract_bill()
        bill2 = self._abstract_bill()
        set_of_bills_data = {
            'investor':data.get('investor',self._abstract_investor()),
            'bills':data.get('bills',[bill1, bill2]),
            'year':data.get('year', '2017')
        }
        set_of_bills = SetOfBills(set_of_bills_data['investor'], set_of_bills_data['bills'], set_of_bills_data['year'])
        return set_of_bills

class TestBill(AbstractClasses):

    def test_save_bill(self):
        bill = self._abstract_bill()
        bill.save(path=f'./test_investors_bills/')
        path = f'./test_investors_bills/investor_1/2017/bill_1.json'
        assert os.path.exists(path)
        shutil.rmtree('./test_investors_bills/')

class TestCashCall(AbstractClasses):

    def test_save_cash_call(self):
        bill = self._abstract_cashcall()
        bill.save(path=f'./test_investors_cash_calls/')
        path = f'./test_investors_cash_calls/investor_1/2021/cash_call_2021.json'
        assert os.path.exists(path)
        shutil.rmtree('./test_investors_cash_calls/')

class TestSetOfBills(AbstractClasses):

    def test_calculate_total_fees(self):
        set_of_bills = self._abstract_set_of_bill()
        total_fees = set_of_bills.calculate_total_fees()
        assert total_fees == 6700*2

    def test_validate_set_of_bills(self):
        set_of_bills = self._abstract_set_of_bill()
        path = f'./test_investors_cash_calls/'
        cash_call = set_of_bills.validate_year_bills(path)
        assert cash_call.total_amount == 6700*2
        assert os.path.exists(f'./test_investors_cash_calls/investor_1/2017/cash_call_2017.json')
        shutil.rmtree('./test_investors_cash_calls/')


class TestInvestor(AbstractClasses):

    def test_set_investments(self):
        investor = self._abstract_investor()
        investment = self._abstract_investment()
        investment2_data = {
            'id':2,
            'investor_id':2}
        investment2 = self._abstract_investment(investment2_data)
        investments = [investment, investment2]
        investor.set_investments(investments)
        assert investor.investments == [investment]

    def test_get_total_investments_by_year(self):
        investor = self._abstract_investor()
        investment = self._abstract_investment()
        investment2_data = {
            'id':2,
            'invested_ammount':2000,
            'date_added':"2018-07-14 22:30:16+00:00",}
        investment3_data = {
            'id':3,
            'invested_ammount':5000,
            'date_added':"2018-07-14 22:30:16+00:00",}
        investment3_data = {
            'id':3,
            'invested_ammount':5000,
            'date_added':"2019-07-14 22:30:16+00:00",}
        investment2 = self._abstract_investment(investment2_data)
        investment3 = self._abstract_investment(investment2_data)
        investment4 = self._abstract_investment(investment3_data)
        investor.investments = [investment, investment2, investment3, investment4]
        expected_investments_by_year = {
            2017:investment.invested_amount,
            2018:investment2.invested_amount + investment3.invested_amount,
            2019:investment4.invested_amount}
        investments_by_year = investor.get_total_investments_by_year()
        assert investments_by_year == expected_investments_by_year

    def test_must_pay_yearly_subscription(self):
        investor = self._abstract_investor()
        investment = self._abstract_investment()
        investment2_data = {
            'id':2,
            'invested_ammount':50000,
            'date_added':"2018-07-14 22:30:16+00:00",}
        investment2 = self._abstract_investment(investment2_data)
        investor.investments = [investment, investment2]
        # The first assersion is with True because the amount invested in abstract
        # investment is under 50k, soy the investor must pay the yearly subscription
        assert investor.must_pay_yearly_subscription(2017) == True
        assert investor.must_pay_yearly_subscription(2018) == False

    def test_generate_investor_bills(self):
        investor = self._abstract_investor()
        investment = self._abstract_investment()
        investment.set_investor(investor)
        investment2_data = {
            'id':2,
            'invested_ammount':50000,
            'date_added':"2018-07-14 22:30:16+00:00",}
        investment2 = self._abstract_investment(investment2_data)
        investment2.set_investor(investor)
        investor.investments = [investment, investment2]
        investor.generate_bills(year=2017, path=f'./test_investors_bills/')
        assert len(investor.bills) == 1
        assert investor.bills[0].investor_id == investor.id
        assert investor.bills[0].investment_id == investment.id
        assert investor.bills[0].date_added == "2017-07-14"
        assert investor.bills[0].fees_amount == 6158.4
        assert investor.bills[0].fees_type == "yearly"
        path = f'./test_investors_bills/investor_{investor.id}/2017/bill_1.json'
        assert os.path.exists(path)
        shutil.rmtree('./test_investors_bills/')

    def test_generate_sets_of_bills(self):
        investor = self._abstract_investor()
        bill1 = self._abstract_bill()
        bill2 = self._abstract_bill()
        investor.bills = [bill1, bill2]
        investor.generate_sets_of_bills()
        assert '2017' in investor.sets_of_bills

    def test_verify_set_of_bills(self):
        investor = self._abstract_investor()
        set_of_bills = self._abstract_set_of_bill()
        investor.sets_of_bills['2017'] = set_of_bills
        path = f'./test_investors_cash_calls/'
        investor.verify_set_of_bills(year=2017, path=path)
        path = f'./test_investors_cash_calls/investor_1/2017/cash_call_2017.json'
        assert os.path.exists(path)
        shutil.rmtree('./test_investors_cash_calls/')

class TestInvestment(AbstractClasses):

    def test_set_investor(self):
        investor = self._abstract_investor()
        investment = self._abstract_investment()
        investment.set_investor(investor)
        assert investment.investor == investor

    def test_generate__upfront_bill_with_less_than_50k_euro(self):
        investor = self._abstract_investor()
        investment_data = {
            "fees_type": "upfront"
        }
        investment = self._abstract_investment(investment_data)
        investor.set_investments([investment])
        investment.set_investor(investor)
        path = f'./test_investors_bills/'
        bill = investment.generate_bill(year=2017, path=path)
        expected_fees_mount = investment.invested_amount * investment.percentage_fees/100 * 5 + 3000
        assert bill.investor_id == investor.id
        assert bill.investment_id == investment.id
        assert bill.date_added == investment.date_added.strftime("%Y-%m-%d")
        assert bill.fees_amount == round(expected_fees_mount, 2)
        assert bill.fees_type == investment.fees_type
        shutil.rmtree('./test_investors_bills/')

    def test_generate__upfront_bill_with_more_than_50k_euro(self):
        investor = self._abstract_investor()
        investment_data = {
            "invested_ammount": 50000,
            "fees_type": "upfront"
        }
        investment = self._abstract_investment(investment_data)
        investor.set_investments([investment])
        investment.set_investor(investor)
        path = f'./test_investors_bills/'
        bill = investment.generate_bill(year=2017, path=path)
        expected_fees_mount = investment.invested_amount * investment.percentage_fees/100 * 5
        assert bill.investor_id == investor.id
        assert bill.investment_id == investment.id
        assert bill.date_added == investment.date_added.strftime("%Y-%m-%d")
        assert bill.fees_amount == round(expected_fees_mount, 2)
        assert bill.fees_type == investment.fees_type
        shutil.rmtree('./test_investors_bills/')

    def test_generate_yearly_bill_before_2019_04_with_less_than_50k_euro(self):
        investor = self._abstract_investor()
        investment = self._abstract_investment()
        relationate_investors_and_investments([investor], [investment])

        first_year = 2017
        second_year = 2018
        third_year = 2019

        path = f'./test_investors_bills/'

        # Test the first year
        expected_bill_fees_for_first_year =  6158.4
        # (1 - 0.53) (1 - day number / 365) * 0.14 (percentage fee) * 48000 (amount) + 3000 (subscription) = 6561.6
        bill_generated_fees_amount = investment.generate_bill(year=first_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_first_year

        # Test the second year
        expected_bill_fees_for_second_year = 9720
        #  0.14 (percentage fee) * 48000 (amount) + 3000 (subscription) = 9720
        bill_generated_fees_amount = investment.generate_bill(year=second_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_second_year

        # Test the third year
        expected_bill_fees_for_third_year = 9720
        # 0.14 (percentage fee) * 48000 (amount) + 3000 (subscription) = 9720
        bill_generated = investment.generate_bill(year=third_year, path=path)
        assert bill_generated.fees_amount == expected_bill_fees_for_third_year
        assert bill_generated.investor_id == investor.id
        assert bill_generated.investment_id == investment.id
        assert bill_generated.date_added == investment.date_added.replace(year=third_year).strftime("%Y-%m-%d")
        assert bill_generated.fees_type == investment.fees_type
        shutil.rmtree('./test_investors_bills/')

    def test_generate_yearly_bill_before_2019_04_with_more_than_50k_euro(self):
        investor = self._abstract_investor()
        investment_data = {'invested_ammount': 50000}
        investment = self._abstract_investment(investment_data)
        relationate_investors_and_investments([investor], [investment])

        path = f'./test_investors_bills/'

        first_year = 2017
        second_year = 2018
        third_year = 2019

        # Test the first year
        expected_bill_fees_for_first_year =  3290
        # (1 - 0.53) (1 - day number / 365) * 0.14 (percentage fee) * 50000 (amount) = 3290
        bill_generated_fees_amount = investment.generate_bill(year=first_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_first_year

        # Test the second year
        expected_bill_fees_for_second_year = 7000
        # 0.14 (percentage fee) * 50000 (amount) = 7000
        bill_generated_fees_amount = investment.generate_bill(year=second_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_second_year

        # Test the third year
        expected_bill_fees_for_third_year = 7000
        # 0.14 (percentage fee) * 50000 (amount) = 7000
        bill_generated = investment.generate_bill(year=third_year, path=path)
        assert bill_generated.fees_amount == expected_bill_fees_for_third_year
        assert bill_generated.investor_id == investor.id
        assert bill_generated.investment_id == investment.id
        assert bill_generated.date_added == investment.date_added.replace(year=third_year).strftime("%Y-%m-%d")
        assert bill_generated.fees_type == investment.fees_type
        shutil.rmtree('./test_investors_bills/')

    def test_generate_yearly_bill_before_2019_04_with_less_than_50k_euro_edge(self):
        investor = self._abstract_investor()
        investment_data = {
            'date_added': "2019-03-31 23:59:59+00:00",
            'invested_ammount': 49999.99}
        investment = self._abstract_investment(investment_data)
        relationate_investors_and_investments([investor], [investment])

        path = f'./test_investors_bills/'

        first_year = 2019

        # Test the first year
        expected_bill_fees_for_first_year =  8250
        # (1 - 0.53) (1 - day number / 365) * 0.14 (percentage fee) * 49999.99 (amount) + 3000 = 8250
        bill_generated_fees_amount = investment.generate_bill(year=first_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_first_year
        shutil.rmtree('./test_investors_bills/')

    def test_generate_yearly_bill_before_2019_04_with_more_than_50k_euro_edge(self):
        investor = self._abstract_investor()
        investment_data = {
            'date_added': "2019-03-31 23:59:00+00:00",
            'invested_ammount': 50000}
        investment = self._abstract_investment(investment_data)
        relationate_investors_and_investments([investor], [investment])

        path = f'./test_investors_bills/'

        first_year = 2019

        # Test the first year
        expected_bill_fees_for_first_year =  5250
        # (1 - 0.53) (1 - day number / 365) * 0.14 (percentage fee) * 50000 (amount) = 5250
        bill_generated_fees_amount = investment.generate_bill(year=first_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_first_year
        shutil.rmtree('./test_investors_bills/')

    def test_generate_yearly_bill_after_2019_04_with_less_than_50k_euro(self):
        investor = self._abstract_investor()
        investment_data = {'date_added': "2019-07-14 22:30:16+00:00"}
        investment = self._abstract_investment(investment_data)
        relationate_investors_and_investments([investor], [investment])

        path = f'./test_investors_bills/'

        first_year = 2019
        second_year = 2020
        third_year = 2021
        fourth_year = 2022
        fifth_year = 2023
        sixth_year = 2024

        # Test the first year
        expected_bill_fees_for_first_year =  6158.4
        # (1 - 0.53) (1 - day number / 365) * 0.14 (percentage fee) * 48000 (amount) + 3000 (subscription) = 6158.4
        bill_generated_fees_amount = investment.generate_bill(year=first_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_first_year

        # Test the second year
        expected_bill_fees_for_second_year = 9720
        # 0.14 (percentage fee) * 48000 (amount) + 3000 (subscription) = 9720.0
        bill_generated_fees_amount = investment.generate_bill(year=second_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_second_year

        # Test the third year
        expected_bill_fees_for_third_year = 9624
        # (0.14 - 0.002) (percentage fee - 0.20%) * 48000 (amount) + 3000 (subscription) = 9624
        bill_generated_fees_amount = investment.generate_bill(year=third_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_third_year

        # Test the fourth year
        expected_bill_fees_for_fourth_year = 9480
        # (0.14 - 0.005) (percentage fee - 0.50%) * 48000 (amount) + 3000 (subscription) = 9480
        bill_generated_fees_amount = investment.generate_bill(year=fourth_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_fourth_year

        # Test the fifth year
        expected_bill_fees_for_fifth_year = 9240
        # (0.14 - 0.01) (percentage fee - 1%) * 48000 (amount) + 3000 (subscription) = 9240
        bill_generated_fees_amount = investment.generate_bill(year=fifth_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_fifth_year

        # Test the sixth year
        expected_bill_fees_for_third_year = 9240
        # (0.14 - 0.01) (percentage fee - 1%) * 48000 (amount) + 3000 (subscription) = 9240
        bill_generated = investment.generate_bill(year=sixth_year, path=path)
        assert bill_generated.fees_amount == expected_bill_fees_for_third_year
        assert bill_generated.investor_id == investor.id
        assert bill_generated.investment_id == investment.id
        assert bill_generated.date_added == investment.date_added.replace(year=sixth_year).strftime("%Y-%m-%d")
        assert bill_generated.fees_type == investment.fees_type
        shutil.rmtree('./test_investors_bills/')

    def test_generate_yearly_bill_after_2019_04_with_more_than_50k_euro(self):
        investor = self._abstract_investor()
        investment_data = {'invested_ammount': 50000,
                        'date_added': "2019-07-14 22:30:16+00:00",
                        'percentage_fees': 14}
        investment = self._abstract_investment(investment_data)
        relationate_investors_and_investments([investor], [investment])

        path = f'./test_investors_bills/'

        first_year = 2019
        second_year = 2020
        third_year = 2021
        fourth_year = 2022
        fifth_year = 2023
        sixth_year = 2024

        # Test the first year
        expected_bill_fees_for_first_year =  3290
        # (1 - 0.53) (1 - day number / 365) * 0.14 (percentage fee) * 50000 (amount) = 3290
        bill_generated_fees_amount = investment.generate_bill(year=first_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_first_year

        # Test the second year
        expected_bill_fees_for_second_year = 7000
        # 0.14 (percentage fee) * 48000 (amount) = 7000
        bill_generated_fees_amount = investment.generate_bill(year=second_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_second_year

        # Test the third year
        expected_bill_fees_for_third_year = 6900
        # (0.14 - 0.002) (percentage fee - 0.20%) * 50000 (amount) = 6900
        bill_generated_fees_amount = investment.generate_bill(year=third_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_third_year

        # Test the fourth year
        expected_bill_fees_for_fourth_year = 6750
        # (0.14 - 0.005) (percentage fee - 0.50%) * 50000 (amount) = 6750
        bill_generated_fees_amount = investment.generate_bill(year=fourth_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_fourth_year

        # Test the fifth year
        expected_bill_fees_for_fifth_year = 6500
        # (0.14 - 0.01) (percentage fee - 1%) * 50000 (amount) = 6500
        bill_generated_fees_amount = investment.generate_bill(year=fifth_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_fifth_year

        # Test the sixth year
        expected_bill_fees_for_third_year = 6500
        # (0.14 - 0.01) (percentage fee - 1%) * 50000 (amount) = 6500
        bill_generated = investment.generate_bill(year=sixth_year, path=path)
        assert bill_generated.fees_amount == expected_bill_fees_for_third_year
        assert bill_generated.investor_id == investor.id
        assert bill_generated.investment_id == investment.id
        assert bill_generated.date_added == investment.date_added.replace(year=sixth_year).strftime("%Y-%m-%d")
        assert bill_generated.fees_type == investment.fees_type
        shutil.rmtree('./test_investors_bills/')

    def test_generate_yearly_bill_after_2019_04_with_less_than_50k_euro_edge(self):
        investor = self._abstract_investor()
        investment_data = {
            'date_added': "2019-03-31 23:59:59+00:00",
            'invested_ammount': 49999.99}
        investment = self._abstract_investment(investment_data)
        relationate_investors_and_investments([investor], [investment])

        path = f'./test_investors_bills/'

        first_year = 2019

        # Test the first year
        expected_bill_fees_for_first_year =  8250
        # (1 - 0.53) (1 - day number / 365) * 0.14 (percentage fee) * 49999.99 (amount) = 3290
        bill_generated_fees_amount = investment.generate_bill(year=first_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_first_year
        shutil.rmtree('./test_investors_bills/')

    def test_generate_yearly_bill_after_2019_04_with_more_than_50k_euro_edge(self):
        investor = self._abstract_investor()
        investment_data = {
            'date_added': "2019-04-01 00:00:01+00:00",
            'invested_ammount': 50000}
        investment = self._abstract_investment(investment_data)
        relationate_investors_and_investments([investor], [investment])

        path = f'./test_investors_bills/'

        first_year = 2019

        # Test the first year
        expected_bill_fees_for_first_year =  5250
        # (1 - 0.53) (1 - day number / 365) * 0.14 (percentage fee) * 50000 (amount) = 5250
        bill_generated_fees_amount = investment.generate_bill(year=first_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_first_year
        shutil.rmtree('./test_investors_bills/')

    def test_generate_yearly_bill_after_2019_04_on_leap_year(self):
        investor = self._abstract_investor()
        investment_data = {
            'date_added': "2019-04-03 00:00:01+00:00",
            'invested_ammount': 50000}
        investment = self._abstract_investment(investment_data)
        relationate_investors_and_investments([investor], [investment])

        path = f'./test_investors_bills/'

        first_year = 2019

        # Test the first year on non leap year
        expected_bill_fees_for_first_year =  5250
        # (1 - 0.25) (1 - day number / 365) * 0.14 (percentage fee) * 50000 (amount) = 5250
        bill_generated_fees_amount = investment.generate_bill(year=first_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_first_year

        investment_data = {
            'date_added': "2020-04-03 00:00:01+00:00",
            'invested_ammount': 50000}
        investment = self._abstract_investment(investment_data)
        relationate_investors_and_investments([investor], [investment])
        first_year = 2020

        # Test the first year on leap year
        expected_bill_fees_for_first_year =  5180
        # (1 - 0.26) (1 - day number / 366) * 0.14 (percentage fee) * 50000 (amount) = 5180
        bill_generated_fees_amount = investment.generate_bill(year=first_year, path=path).fees_amount
        assert bill_generated_fees_amount == expected_bill_fees_for_first_year
        shutil.rmtree('./test_investors_bills/')
