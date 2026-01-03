"""
cli.py

Project: pyads-ipc-diag
:author: Teemu Vartiainen
:license: MIT
:created on: 30.12.2025 13.11

"""
import argparse
import inspect
import pyads_ipc_diag as bhf
from dataclasses import is_dataclass, asdict
from enum import Enum
from datetime import datetime, date
import base64

def discover_modules():
    """ Get all available modules """
    names = []

    exclude = {
        "MDP",
        "CONFIG_AREA",
        "SERVICE_AREA",
        "DEVICE_AREA",
        "GENERAL_AREA",
    }

    for name in getattr(bhf, "__all__", []):
        if name in exclude:
            continue
        obj = getattr(bhf, name, None)
        if obj is None:
            continue
        if inspect.isclass(obj):
            names.append(name)
    return ["all"] + sorted(names)

AVAILABLE_MODULES = discover_modules()

def to_jsonable(obj):
    """ Convert object to jsonable
    :param obj: object to convert to json"""
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    # dataclass
    if is_dataclass(obj):
        return {k: to_jsonable(v) for k, v in asdict(obj).items()}

    # dict / list / tuple / set
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_jsonable(v) for v in obj]

    # datetime/date
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    # enum
    if isinstance(obj, Enum):
        return obj.value

    # bytes
    if isinstance(obj, (bytes, bytearray)):
        return base64.b64encode(obj).hex()

    return str(obj)

def parse_parameters():
    parser = argparse.ArgumentParser(
        prog="pyads_ipc_diag",
        description="Beckhoff IPC Diagnostics",
    )
    parser.add_argument("--ams-net-id", required=True)
    parser.add_argument("--module", required=True, choices=AVAILABLE_MODULES)
    parser.add_argument("--print", action="store_true")
    parser.add_argument("--json")
    return parser.parse_args()

def main():
    runnable = [m for m in AVAILABLE_MODULES if m != "all"]

    args = parse_parameters()

    results = {"data": {}, "errors": {}}

    targets = runnable if args.module == "all" else [args.module]

    with bhf.MDP(args.ams_net_id) as ipc:
        for name in targets:
            cls = getattr(bhf, name)
            results["device"] = args.ams_net_id
            try:
                obj = cls(ipc)
                info = obj.info()
                results["data"][name] = info
            except Exception as e:
                results["errors"][name] = str(e)

    if args.print:
        output_print(results)

    if args.json:
        output_json(args.json, results)

def output_print(results):
    for k, v in results["data"].items():
        print(f"\n=== {k} ===")
        print(v)
    for k, e in results["errors"].items():
        print(f"\n=== {k} ===")
        print(f"ERROR: {e}")

def output_json(file, results):
    import json
    json_payload = to_jsonable(results)
    with open(file, "w", encoding="utf-8") as f:
        json.dump(json_payload, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
