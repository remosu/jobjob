import jobjob.utils
import filecmp

def test_copy_input():
    jobjob.utils.copy_input('src_input', 'dst_input', 
                            var3=55, var4=100) 
    assert filecmp.cmp('dst_input', 'dst_input-good')
    
def test_read_vars():
    assert list(jobjob.utils.read_vars('src_input')) == [('var1', 10), 
                                                   ('var2', 11), 
                                                   ('var3', 43.55)]
                                                   
def test_get_value():
    assert jobjob.utils.get_value('0') == 0
    assert jobjob.utils.get_value('0.0') == 0.0
    assert jobjob.utils.get_value('0sd') == '0sd'
