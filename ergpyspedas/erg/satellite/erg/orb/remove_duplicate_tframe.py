import numpy as np

from pyspedas import tnames
from pytplot import get_data, store_data

def remove_duplicated_tframe(tvars=[]):
    
    tvars = tnames(tvars)
    
    if len(tvars) < 1:
        return
    
    for tvar in tvars:
        
        input_attr_dict = get_data(tvar, metadata=True)
        get_data_vars = get_data(tvar)

        unique_array, counts_array = np.unique(get_data_vars[0], return_counts=True)
        duplicate_time_indices = np.where(counts_array > 1)[0]
        delete_indices_array = np.array([np.where(get_data_vars[0] == unique_array[index])[0][0]
                                         for index in duplicate_time_indices])
        input_data_dictionary = {}
        input_data_dictionary['x'] = np.delete(get_data_vars[0],
                                delete_indices_array, axis=0)
        input_data_dictionary['y'] = np.delete(get_data_vars[1],
                                delete_indices_array, axis=0)
        
        if len(get_data_vars) >= 3: # for v or v1, v2.. elements. not tested yet.
            element_counts = len(get_data_vars)
            if element_counts == 3:
                input_data_dictionary['v'] = np.delete(get_data_vars[2],
                                        delete_indices_array, axis=0)
            elif element_counts > 3:
                for element_index in range(2, element_counts):
                    v_element_name = f'v{element_index-1}'
                    input_data_dictionary[v_element_name] = np.delete(
                        get_data_vars[element_index], delete_indices_array, axis=0)

        store_data(tvar,data=input_data_dictionary,attr_dict=input_attr_dict)

    return