import argparse
import inspect
from typing import Literal, get_origin

def fire_like(obj):
    parser = argparse.ArgumentParser()
    subparsers = None

    if inspect.isfunction(obj):
        add_args_from_sig(parser, inspect.signature(obj))
        args = vars(parser.parse_args())
        return obj(**args)

    elif inspect.isclass(obj):
        # 先处理 __init__
        init_sig = inspect.signature(obj.__init__)
        init_parser = argparse.ArgumentParser()
        add_args_from_sig(init_parser, init_sig, skip_self=True)

        subparsers = init_parser.add_subparsers(dest='command')
        methods = {
            name: m for name, m in inspect.getmembers(obj, predicate=inspect.isfunction)
            if not name.startswith('_')
        }
        method_parsers = {}
        for name, method in methods.items():
            sig = inspect.signature(method)
            subparser = subparsers.add_parser(name)
            add_args_from_sig(subparser, sig, skip_self=True)
            method_parsers[name] = method

        ns = vars(init_parser.parse_args())
        command = ns.pop("command")
        instance = obj(**{k: v for k, v in ns.items() if k in init_sig.parameters})
        if command:
            method = method_parsers[command]
            method_args = {
                k: v for k, v in ns.items() if k in inspect.signature(method).parameters
            }
            return method(instance, **method_args)
        else:
            return instance

def add_args_from_sig(parser, sig, skip_self=False):
    for name, param in sig.parameters.items():
        if skip_self and name == 'self':
            continue

        param_type = param.annotation if param.annotation != inspect.Parameter.empty else str

        default = param.default if param.default != inspect.Parameter.empty else None

        arg_name = f"--{name.replace('_', '-')}"

        if param_type == bool:
            parser.add_argument(arg_name, action='store_true' if default is False else 'store_false')
        elif get_origin(param_type) is Literal:
            choices = [v for v in param_type.__args__ if v is not None] # type: ignore
            parser.add_argument(arg_name, type=str, choices=choices, default=default)
        else:
            parser.add_argument(arg_name, type=param_type, default=default)
