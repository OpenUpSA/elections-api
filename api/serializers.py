import json


def serialize_area(area_obj, event_type):

    out = area_obj.as_dict()
    out.pop('pk')  # suppress the record's primary key

    if hasattr(area_obj, 'province'):
        out.pop('province_pk')
        out['province'] = area_obj.province.province_id

    if hasattr(area_obj, 'municipality'):
        out.pop('municipality_pk')
        out['municipality'] = area_obj.municipality.municipality_id

    if hasattr(area_obj, 'ward'):
        out.pop('ward_pk')
        if area_obj.ward is not None:
            out['ward'] = area_obj.ward.ward_id

    if event_type == 'provincial':
        out.pop('results_national')
        out['results'] = json.loads(out['results_provincial'])
        out.pop('results_provincial')
    else:
        out.pop('results_provincial')
        out['results'] = json.loads(out['results_national'])
        out.pop('results_national')

    if hasattr(area_obj, 'year'):
        out.pop('year')

    return out