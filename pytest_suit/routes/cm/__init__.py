from .. import BASE_URL, test_tif_file

test_tif_file_name = test_tif_file[:-4]
test_cm_id = 10
inputs_cm = [
    {'input_name': 'Multiplication factor',
     'input_type': 'input',
     'input_parameter_name': 'multiplication_factor',
     'input_value': '1',
     'input_priority': 0,
     'input_unit': 'none',
     'input_min': 0,
     'input_max': 10, 'cm_id': test_cm_id
     },
]
signature_cm = {
    "cm_id": test_cm_id,
    "cm_name": "test cm name",
    "cm_url": "Do not add something",
    "cm_description": "this computation module does not really exist",
    "category": "Buildings",
    "layers_needed": [
        "heat_tot_curr_density",
    ],
    "type_layer_needed": [
        "heat",
    ],
    "vectors_needed": [
        "heating_technologies_eu28",
    ],
    'inputs_calculation_module': inputs_cm
}
