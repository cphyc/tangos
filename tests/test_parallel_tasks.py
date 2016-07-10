from tangos import parallel_tasks as pt
from tangos import testing
import tangos
import sys

def setup():
    pt.use("multiprocessing")
    testing.init_blank_db_for_testing(timeout=5.0, verbose=False)

    generator = testing.TestSimulationGenerator()
    generator.add_timestep()
    generator.add_halos_to_timestep(9)

    tangos.core.get_default_session().commit()


def _add_property():
    for i in pt.distributed(range(1,10)):
        tangos.get_halo(i)['my_test_property']=i
        tangos.core.get_default_session().commit()

def test_add_property():
    pt.launch(_add_property,3)
    for i in range(1,10):
        assert tangos.get_halo(i)['my_test_property']==i

def _add_two_properties_different_ranges():
    for i in pt.distributed(range(1,10)):
        tangos.get_halo(i)['my_test_property_2']=i
        tangos.core.get_default_session().commit()

    for i in pt.distributed(range(1,8)):
        tangos.get_halo(i)['my_test_property_3'] = i
        tangos.core.get_default_session().commit()

def test_add_two_properties_different_ranges():
    pt.launch(_add_two_properties_different_ranges,3)
    for i in range(1,10):
        assert tangos.get_halo(i)['my_test_property_2']==i
        if i<8:
            assert 'my_test_property_3' in tangos.get_halo(i)
            assert tangos.get_halo(i)['my_test_property_3'] == i
        else:
            assert 'my_test_property_3' not in tangos.get_halo(i)