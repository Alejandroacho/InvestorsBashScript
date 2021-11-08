import json

from models import Investment, Investor

def load_investors_data_from_json(path='../Samples/Investors/investor.json'):
    json_file = open(path)
    investors_in_json_file = json.load(json_file)
    investors = []

    for investor_data in investors_in_json_file:
        investor = Investor(investor_data)
        investors.append(investor)

    return investors

def load_investments_data_from_json(path='../Samples/Investments/investments.json'):
    json_file = open(path)
    investment_in_json_file = json.load(json_file)
    investments = []

    for investment_data in investment_in_json_file:
        investment = Investment(investment_data)
        investments.append(investment)

    return investments

def relationate_investors_and_investments(investors, investments):
    for investor in investors:
        invest_investments = investor.set_investments(investments)

        for investment in invest_investments:
            investment.set_investor(investor)
