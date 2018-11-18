from collections import namedtuple

ValueDataTuple = namedtuple('ValueDataTuple', ['name', 'type_name', 'value', 'byte_size', 'address'])


def get_value(value):
    val = value.GetSummary()
    if val is None:
        val = value.GetValue()
    if val is None and value.GetNumChildren() > 0:
        val = '%s (location)' % value.GetLocation()
    if val is None:
        return None
    return str(val)


def format_value(value):
    val = get_value(value)
    name = value.GetName()
    type_name = value.GetDisplayTypeName()
    byte_size = value.GetByteSize()
    address = value.GetLoadAddress()
    val_data = ValueDataTuple(name=name, type_name=type_name, value=val, byte_size=byte_size, address=address)
    return val_data


FrameDataTuple = namedtuple('FrameDataTuple', ['name', 'return_type_name', 'arg_names', 'arg_type_names',
                                               'arg_values', 'address'])


def format_frame(frame):
    name = frame.GetDisplayFunctionName()
    return_type_name = frame.GetFunction().GetType().GetFunctionReturnType().GetName()
    args = frame.GetVariables(True, False, False, True)
    arg_names = [x.GetName() for x in args]
    arg_type_names = [x.GetDisplayTypeName() for x in args]
    arg_values = [get_value(x) for x in args]
    address = frame.GetPCAddress().GetLoadAddress(frame.GetThread().GetProcess().GetTarget())
    f_data = FrameDataTuple(name=name, return_type_name=return_type_name, arg_names=arg_names,
                            arg_type_names=arg_type_names, arg_values=arg_values, address=address)
    return f_data
