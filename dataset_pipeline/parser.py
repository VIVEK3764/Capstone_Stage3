def extract_input_signals(slither_json):
    return {"contracts": slither_json["results"]["contracts"]}