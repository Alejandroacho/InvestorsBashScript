import argparse
import sys

from utils import load_investments_data_from_json,\
                  load_investors_data_from_json,\
                  relationate_investors_and_investments

SCRIPT_DESCRIPTION = 'Process bills and cash calls generator for investors.\
    Even that "year" and "all" parameters are not required, you must pass at least one of them.\
    The process type options are "generate" and "verify", and it stands for choosing if your are making the investors bill or you are verifying a set of bills of one investor, so if you choose verify you must pass the year and the investor id. If you choose generate you can pass investor id and/or year and if not it will make all the bills for all the years of all the investors.\
    "Origin path" flag is for the origin path to take the information from.\
    "Destination path" flag is for where the bills or cashcall will be stored in.'

def main():
    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument('--year', type=int, help='[NOT REQUIRED] Year to process')
    parser.add_argument('--all', type=bool, help='[NOT REQUIRED] Process all years')
    parser.add_argument('--investor', type=int, help='[NOT REQUIRED] Investor to process')
    parser.add_argument('--type', type=str, help='[NOT REQUIRED] Type of process to apply')
    parser.add_argument('--investors-path', type=str, help='[NOT REQUIRED] Origin path to take the investors information from')
    parser.add_argument('--investments-path', type=str, help='[NOT REQUIRED] Origin path to take the investments information from')
    parser.add_argument('--destination', type=str, help='[NOT REQUIRED] Destination path to save the information in')
    arguments = parser.parse_args()

    year = arguments.year
    all = arguments.all
    investor_id = arguments.investor
    operation_type = arguments.type
    investors_origin_path = arguments.investors_path
    investments_origin_path = arguments.investments_path
    destination_path = arguments.destination

    operation_type = verify_flags_and_get_operation_type(operation_type, investor_id, year, all)
    destination_path = verify_path(destination_path)
    investors = get_investors_and_investments(investors_origin_path, investments_origin_path)
    process_operation(investor_id, investors, operation_type, year, all, destination_path)

def verify_path(path):
    if not path.endswith('/'):
        path = path + '/'
    return path

def verify_flags_and_get_operation_type(operation_type, investor_id, year, all):
    if not operation_type or operation_type == 'generate':
        operation_type = 'generate'
        if not year and not all:
            raise ValueError('At least year or all are required')
    elif operation_type == 'verify':
        if not investor_id:
            raise ValueError('Investor id is required for verify')
        if not year:
            raise ValueError('Year is required for verify')
    return operation_type

def get_investors_and_investments(investors_origin_path, investments_origin_path):
    if investors_origin_path:
        investors = load_investors_data_from_json(path=investors_origin_path)
    else:
        investors = load_investors_data_from_json()
    if investments_origin_path:
        investments = load_investments_data_from_json(path=investments_origin_path)
    else:
        investments = load_investments_data_from_json()
    relationate_investors_and_investments(investors, investments)
    return investors

def process_operation(investor_id, investors, operation_type, year, all, destination_path):
    if investor_id:
        investor = [investor for investor in investors if investor.id == int(investor_id)][0]
        if operation_type == 'generate':
            investor.generate_bills(year=year, path=destination_path, all=all)
            investor.generate_sets_of_bills()
            sys.stdout.write(f'Bills of {year if year else "alls"} year, for investor id {investor_id}.')
        elif operation_type == 'verify':
            investor.generate_bills(year=year, path=destination_path, all=all, save=False)
            investor.generate_sets_of_bills()
            investor.verify_set_of_bills(year=year, path=destination_path)
            sys.stdout.write(f'Verified bills of year {year}, for investor {investor_id}.')
    else:
        for investor in investors:
            if operation_type == 'generate':
                investor.generate_bills(year=year, path=destination_path, all=all)
                investor.generate_sets_of_bills()
            elif operation_type == 'verify':
                raise ValueError('Verify option is not available for all investors.')
        sys.stdout.write(f'Bills of {year if year else "alls"} year/s, for investor all investors.')

if __name__ == '__main__':
    main()
