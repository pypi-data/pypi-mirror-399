'''opencos.utils.dict_helpers -- Various dict helpers functions'''

def dict_diff(d1: dict, d2: dict) -> dict:
    '''Returns dict of added/removed/changed keys in d1 vs d2.

    If an empty dict is returned then there were no differences'''

    diff = {
        'added': {},
        'removed': {},
        'changed': {},
    }

    # Keys added to d2
    for key in d2.keys() - d1.keys():
        diff['added'][key] = d2[key]

    # Keys removed from d1
    for key in d1.keys() - d2.keys():
        diff['removed'][key] = d1[key]

    # Keys present in both
    for key in d1.keys() & d2.keys():
        if d1[key] != d2[key]:
            diff['changed'][key] = f'{d1[key]} --> {d2[key]}'

    for key in ('added', 'removed', 'changed'):
        if not diff[key]:
            del diff[key]

    return diff
