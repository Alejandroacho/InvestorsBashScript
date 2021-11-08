from utils import load_investors_data_from_json,\
                  load_investments_data_from_json

def test_load_investors_data_from_json():
    path = "../Sample_test/investors_test.json"
    investors_data = load_investors_data_from_json(path)
    assert len(investors_data) == 2
    assert investors_data[0].name == "Alejandro"
    assert investors_data[1].name == "Claudia"

def test_load_investors_data_from_json():
    path = "../Sample_test/investments_test.json"
    investors_data = load_investments_data_from_json(path)
    assert len(investors_data) == 4
    assert investors_data[0].invested_amount == 42000
    assert investors_data[1].invested_amount == 42000
    assert investors_data[2].invested_amount == 50000
    assert investors_data[3].invested_amount == 42000