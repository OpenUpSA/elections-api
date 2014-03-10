
def serialize_area(area_obj):

    out = area_obj.as_dict()
    out.pop('pk')  # suppress the record's primary key

    if hasattr(area_obj, 'province'):
        out.pop('province_pk')
        out['province'] = area_obj.province.province_id

    if hasattr(area_obj, 'municipality'):
        out.pop('municipality_pk')
        out['municipality'] = area_obj.municipality.municipality_id

    if hasattr(area_obj, 'ward') and area_obj.ward is not None:
        out.pop('ward_pk')
        out['ward'] = area_obj.ward.ward_id

    return out