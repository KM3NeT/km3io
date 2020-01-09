import os
import inspect
import numpy as np
import km3io as ki
import awkward as aw


CLASSES = tuple(m[1] for m in inspect.getmembers(ki.offline, inspect.isclass))

def to_csv(f_name, **kwargs):
    """writes data in a csv file

    Parameters
    ----------
    f_name : str
        Description
    **kwargs
        Description
    """
    if os.path.isfile(f_name):
        raise OSError("'{}' already exists! change the file name or delete it".format(f_name))

    with open(f_name+'.csv', 'a') as fp:
        for key, value in kwargs.items(): 

            # write events, hits and tracks classes
            if isinstance(value, CLASSES):
                for k, v in zip(value._keys, np.array(value._values)): # if it doesn't work change enumerate(v) to enumerate(np.array(v))
                    fp.write('# {}\n'.format(k))
                    for i, j in enumerate(v):
                        np.savetxt(fp, j, header=str(i), comments='## ')

            # write arrays
            if isinstance(value, np.ndarray): 
                np.savetxt(fp, value, header=key, comments='# ')

            else:
                try:
                    # write a jagged array
                    if value.dtype.char == 'O':  # O is the unique char that identifies 'awkward.array.chunked.ChunkedArray'
                        fp.write('# {}\n'.format(key))
                        for i, j in enumerate(value):
                                np.savetxt(fp, j, header=str(i), comments='## ')

                except Exception:
                    raise TypeError("'{}' is not a valid data structure".format(type(value)))


def from_csv(f_name, headers=None):
    """reads a csv file written by km3io

    Parameters
    ----------
    f_name : str
        Description
    headers : None, optional
        list of str of headers
    """
    if headers is None:
        keys = []
        values = []
        found_header = False
        found_sub_header = False
        # read the entire file
        with open(f_name, 'r') as fp:
            jagged_data = []
            jagged_sub_data = []
            for line in fp:
                if '# ' in line:
                    found_header = True
                    keys.append(line.split()[1]) # convert str to float

                if found_header:
                    if '# ' in line:
                    found_header = False
                    if '## ' in line:
                        found_sub_header = True
                    else:
                        jagged_data.append(line.split()[0])


                if found_header and found_sub_header:
                    if '## ' in line:
                        found_sub_header = False
                        jagged_data.append(jagged_sub_data)
                    else:
                        jagged_sub_data.append(lin.split()[0])



#write in hdf 


#write in root (NOT NECESSARY)
