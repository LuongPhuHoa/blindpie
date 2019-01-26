import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import json
from argparse import ArgumentParser, ArgumentTypeError
from typing import Dict, List
from blindpie.core import IBlindpie, Blindpie, DESCRIPTION
from blindpie.logger import ILogger, Logger
from blindpie.request import Request
from blindpie.defaults import *


def one_of(string: str, param_name: str, valid_values: List[str]) -> str:

    if string not in valid_values:
        raise ArgumentTypeError("'{:s}' must be one of: {:s}".format(param_name, ', '.join(valid_values)))
    return string


def json_dict(string: str, param_name: str) -> Dict[str, str]:

    try:
        json_dict_ = json.loads(string)
        if not isinstance(json_dict_, dict):
            raise ArgumentTypeError("'{:s}' must be a JSON dictionary".format(param_name))
        return json_dict_
    except json.JSONDecodeError:
        raise ArgumentTypeError("'{:s}' must be a valid JSON dictionary".format(param_name))


def numeric_val(string: str, param_name: str, min_val: float, eq: bool, type_: type):

    try:
        numeric_val_ = type_(string)

        if not eq and numeric_val_ <= min_val:
            raise ArgumentTypeError("'{:s}' must be greater than {:s}".format(param_name, str(min_val)))
        elif eq and numeric_val_ < min_val:
            raise ArgumentTypeError("'{:s}' must be greater or equal than {:s}".format(param_name, str(min_val)))
        return numeric_val_
    except TypeError:
        raise ArgumentTypeError("'{:s}' must be a numeric value".format(param_name))


def method(string):

    return one_of(string=string, param_name="method", valid_values=["get", "post"])


def params(string) -> Dict[str, str]:

    return json_dict(string=string, param_name="params")


def headers(string) -> Dict[str, str]:

    return json_dict(string=string, param_name="headers")


def threshold(string) -> float:

    return numeric_val(string=string, param_name="threshold", min_val=1, eq=False, type_=float)


def max_interval(string) -> int:

    return numeric_val(string=string, param_name="max_interval", min_val=0, eq=True, type_=int)


def columns(string) -> List[str]:

    return string.split(',')


def from_row(string) -> int:

    return numeric_val(string=string, param_name="from_row", min_val=0, eq=True, type_=int)


def n_rows(string) -> int:

    return numeric_val(string=string, param_name="n_rows", min_val=1, eq=True, type_=int)


def min_row_length(string) -> int:

    return numeric_val(string=string, param_name="min_row_length", min_val=0, eq=True, type_=int)


def max_row_length(string) -> int:

    return numeric_val(string=string, param_name="max_row_length", min_val=1, eq=True, type_=int)


if __name__ == "__main__":

    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument("-u", "--url", metavar="url", type=str, help="the URL of the target", required=True)

    subparsers = parser.add_subparsers(help="blindpie commands", dest="command")

    test = subparsers.add_parser("test", aliases=["t"], help="test whether some parameters can be exploited")
    fetch_table = subparsers.add_parser("fetch_table", aliases=["f"], help="fetch a table by exploiting a vulnerable parameter")

    test.add_argument("-M", "--method", metavar="method", type=method, help="the HTTP method for the requests", required=True)
    test.add_argument("-P", "--params", metavar="params", type=params, help="the parameters to test and their default values (must be a JSON dictionary)", required=True)
    test.add_argument("-H", "--headers", metavar="headers", type=headers, help="the headers for the requests (must be a JSON dictionary)", required=False, default=DEFAULT_HEADERS)
    test.add_argument("-T", "--threshold", metavar="threshold", type=threshold, help="threshold used to decide if an answer is affirmative or negative (must be greater than 1)", default=DEFAULT_THRESHOLD, required=False)
    test.add_argument("-I", "--max_interval", metavar="max_interval", type=max_interval, help="max time to wait between each request in ms", default=DEFAULT_MAX_INTERVAL, required=False)

    fetch_table.add_argument("-M", "--method", metavar="method", type=method, help="the HTTP method for the requests", required=True)
    fetch_table.add_argument("-P", "--params", metavar="params", type=params, help="the parameters and their default values (must be a JSON dictionary)", required=True)
    fetch_table.add_argument("-H", "--headers", metavar="headers", type=headers, help="the headers for the request (must be a JSON dictionary)", required=False, default=DEFAULT_HEADERS)
    fetch_table.add_argument("-T", "--threshold", metavar="threshold", type=threshold, help="threshold used to decide if an answer is affirmative or negative (must be greater than 1)", default=DEFAULT_THRESHOLD, required=False)
    fetch_table.add_argument("-I", "--max_interval", metavar="max_interval", type=max_interval, help="max time to wait between each request in ms", default=DEFAULT_MAX_INTERVAL, required=False)
    fetch_table.add_argument("-p", "--vulnerable_param", metavar="vulnerable_param", type=str, help="the vulnerable parameter to exploit", required=True)
    fetch_table.add_argument("-t", "--table", metavar="table", type=str, help="the name of the table to fetch", required=True)
    fetch_table.add_argument("-c", "--columns", metavar="columns", type=columns, help="the columns to select", required=True)
    fetch_table.add_argument("-r", "--from_row", metavar="from_row", type=from_row, help="the row from which to start to select", default=0, required=False)
    fetch_table.add_argument("-n", "--n_rows", metavar="n_rows", type=n_rows, help="the number of rows to select", default=None, required=False)
    fetch_table.add_argument("--min_row_length", metavar="min_row_length", type=min_row_length, help="limit selection to rows with this min length", default=DEFAULT_MIN_ROW_LENGTH, required=False)
    fetch_table.add_argument("--max_row_length", metavar="max_row_length", type=max_row_length, help="limit selection to rows with this max length", default=DEFAULT_MAX_ROW_LENGTH, required=False)
    fetch_table.add_argument("-o", "--output_path", metavar="output_path", type=str, help="path to the output file", default="./blindpie.out", required=False)

    args = parser.parse_args()

    logger: ILogger = Logger()
    blindpie: IBlindpie = Blindpie(url=args.url, params=args.params, logger=logger)

    if args.command == "test":
        test_args = {
            "default_request": Request(params=args.params, method=args.method, headers=args.headers if args.headers is not None else DEFAULT_HEADERS),
            "params": list(args.params.keys()),
            "threshold": args.threshold,
            "max_interval": args.max_interval
        }
        blindpie.test(**test_args)
    elif args.command == "fetch_table":
        fetch_table_args = {
            "default_request": Request(method=args.method, params=args.params, headers=args.headers if args.headers is not None else DEFAULT_HEADERS),
            "param": args.vulnerable_param,
            "table": args.table,
            "columns": args.columns,
            "from_row": args.from_row,
            "n_rows": args.n_rows,
            "min_row_length": args.min_row_length,
            "max_row_length": args.max_row_length,
            "threshold": args.threshold,
            "max_interval": args.max_interval,
            "output_path": args.output_path
        }
        blindpie.fetch_table(**fetch_table_args)
