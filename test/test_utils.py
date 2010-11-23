import jobjob.utils
import filecmp

def test_copy_input():
    jobjob.utils.copy_input('src_input', 'dst_input', {'var3':55, 'var4':100}) 
    assert filecmp.cmp('dst_input', 'dst_input-good')
