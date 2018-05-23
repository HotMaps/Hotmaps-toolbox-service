import json


def find_key_in_dict(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find_key_in_dict(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find_key_in_dict(key, d):
                    yield result

def retrieveCrossIndicator(denominator_indicator_name, numerator_indicator_name, layers, payload_output):
    if denominator_indicator_name in layers and numerator_indicator_name in layers:
        numerator = getValuesFromName(numerator_indicator_name,payload_output)
        denominator = getValuesFromName(denominator_indicator_name,payload_output)
        generateCrossIndicator(numerator, denominator,numerator_indicator_name, payload_output)

def generateCrossIndicator(numerator, denominator, value_to_append, output):
    denominator_val = float(denominator.get('value', 1))
    denominator_val = denominator_val if denominator_val > 0 else 1
    numerator_val = float(numerator.get('value', 0))
    v = {
        'name': numerator['name'] + '_per_' + denominator['name'],
        'value': numerator_val / denominator_val,
        'unit': numerator.get('unit') + '/' + denominator.get('unit')
    }
    for x in output:
        if x['name'] == value_to_append:
            x['values'].append(v)

def getValuesFromName(name, output):
    values = None
    for i in output:
        if i['name'] == name:
            values = i['values'][0]
            break
    return values

def getDictFromJson(output):
    outputdumps = json.dumps(output)
    outputloads = json.loads(outputdumps)[0]
    return outputloads

def roundValue(value):
    return round(value, 1)


