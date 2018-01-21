from six.moves import range
import numpy as np
from . query_masking import QueryMask

class QueryMultivalueFolding(object):
    """This class manages a situation where a query returns multiple outputs per input, and one temporarily wants
    to explore all those outputs then later fold them back to a single output per input"""

    def __init__(self, determiner_mode, determiner_column):
        assert determiner_mode in ['max', 'min']
        self.determiner_mode = determiner_mode
        self.determiner_column = determiner_column

    def unfold(self, input):
        input_unfolded = []
        slices_for_original_rows = []
        for input_row_index, input_row in enumerate(input):
            startpoint = len(input_unfolded)
            input_unfolded+=input_row
            endpoint = len(input_unfolded)
            slices_for_original_rows.append(slice(startpoint,endpoint))
        self.slices_for_original_rows = slices_for_original_rows
        self.num_original_rows = len(input)
        return input_unfolded

    def refold(self, results_to_refold):
        shape = list(results_to_refold.shape)
        shape[-1] = self.num_original_rows
        out_results = np.empty(shape=shape, dtype=results_to_refold.dtype)
        for i in range(self.num_original_rows):
            results_slice = results_to_refold.T[self.slices_for_original_rows[i]].T
            determiner_slice = results_slice[self.determiner_column]
            mask = QueryMask()
            mask.mark_nones_as_masked(determiner_slice)
            results_slice = mask.mask(results_slice.T).T
            determiner_slice = mask.mask(determiner_slice)
            if len(determiner_slice)!=0:
                if self.determiner_mode=='max':
                    select_index = determiner_slice.argmax()
                else:
                    select_index = determiner_slice.argmin()
                out_results_place = out_results.T[i].T
                out_results_place[:] = results_slice.T[select_index].T
        return out_results