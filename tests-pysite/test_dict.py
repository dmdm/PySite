import yaml


def test_dict():
    D = dict(
        a_int=1,
        a_int_zero=0,
        a_float=1.1,
        a_float_zero=0.0,
        a_str='foo',
        a_str_empty='',
        a_none=None
    )
    assert 'a_int' in D
    assert D['a_int'] == 1
    assert 'a_int_zero' in D
    assert D['a_int_zero'] == 0
    assert 'a_float' in D
    assert D['a_float'] == 1.1
    assert 'a_float_zero' in D
    assert D['a_float_zero'] == 0.0
    assert 'a_str' in D
    assert D['a_str'] == 'foo'
    assert 'a_str_empty' in D
    assert D['a_str_empty'] == ''
    assert 'a_none' in D
    assert D['a_none'] is None
    
    assert (not D['a_int']) == False
    assert (not D['a_float']) == False
    assert (not D['a_str']) == False
    
    assert (not D['a_int_zero']) == True
    assert (not D['a_float_zero']) == True
    assert (not D['a_str_empty']) == True
    assert (not D['a_none']) == True
