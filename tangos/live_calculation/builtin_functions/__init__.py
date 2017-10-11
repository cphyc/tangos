from __future__ import absolute_import
import numpy as np

import tangos
from tangos.util import consistent_collection
from .. import BuiltinFunction, FixedInput, FixedNumericInput, StoredProperty
from ... import core
from ...core import extraction_patterns

@BuiltinFunction.register
def match(source_halos, target):
    timestep = consistent_collection.ConsistentCollection(source_halos).timestep
    if target is None:
        results = [None]*len(source_halos)
    else:
        from ... import relation_finding
        if not isinstance(target, core.Base):
            target = tangos.get_item(target, core.Session.object_session(timestep))
        results = relation_finding.MultiSourceMultiHopStrategy(source_halos, target).all()
    assert len(results) == len(source_halos)
    return np.array(results, dtype=object)
match.set_input_options(0, provide_proxy=True, assert_class = FixedInput)

@BuiltinFunction.register
def later(source_halos, num_steps):
    timestep = consistent_collection.ConsistentCollection(source_halos).timestep.get_next(num_steps)
    return match(source_halos, timestep)

later.set_input_options(0, provide_proxy=True, assert_class = FixedNumericInput)


@BuiltinFunction.register
def earlier(source_halos, num_steps):
    return later(source_halos, -num_steps)

earlier.set_input_options(0, provide_proxy=True, assert_class = FixedNumericInput)


@BuiltinFunction.register
def latest(source_halos):
    timestep = consistent_collection.ConsistentCollection(source_halos).timestep.get_final()
    return match(source_halos, timestep)

@BuiltinFunction.register
def earliest(source_halos):
    timestep = consistent_collection.ConsistentCollection(source_halos).timestep.get_final(-1)
    return match(source_halos, timestep)

@BuiltinFunction.register
def has_property(source_halos, property):
    return np.not_equal(property,None)

has_property.set_input_options(0, provide_proxy=False, assert_class=StoredProperty)


@BuiltinFunction.register
def has_link(source_halos, link):
    return np.not_equal(link,None)

@has_link.set_initialisation
def link_exists_initialisation(input):

    input.set_extraction_pattern(
        extraction_patterns.halo_link_target_getter)



from . import arithmetic, array, reassembly