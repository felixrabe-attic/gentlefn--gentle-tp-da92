#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Execute a gentle transformation.

# Author: Felix Rabe

from __future__ import print_function

import os
import re
import stat
import subprocess
import sys
import tempfile

from gentle_tp_da92 import *


CMD_PREFIX = "command_"


def _json_loadp(g, ptr):
    return json.loads(g.c[g.p[ptr]])


def _freeze_doc(g, doc, doc_p):
    doc["THIS:freezes:pointer"] = doc_p
    return g.c + json.dumps(doc)

def _freeze_ptr(g, doc, p_key, content_id=None):
    c_key = p_key.rsplit(":", 1)
    if c_key[-1] != "pointer":  # alias: not p_key.endswith(":pointer")
        print("ERROR: Cannot freeze key %r of document:" % p_key, file=sys.stderr)
        json.pprint(doc)
        sys.exit(1)
    c_key = ":".join(c_key[:-1] + ["content"])

    if content_id is None:
        content_id = g.p[doc[p_key]]
    del doc[p_key]
    doc[c_key] = content_id

def _freeze_trans(g, trans, trans_p, input_key):
    "Freeze the transformation document by turning some pointers into contents."
    trans = trans.copy()
    exec_p = trans["Exec:json:pointer"]
    exec_ = _json_loadp(g, exec_p)
    _freeze_ptr(g, exec_, "Script:pointer")
    _freeze_ptr(g, trans, "Exec:json:pointer", _freeze_doc(g, exec_, exec_p))
    if input_key.endswith(":pointer"):
        _freeze_ptr(g, trans, input_key)
    _freeze_ptr(g, trans, "Output:json:pointer")
    return _freeze_doc(g, trans, trans_p), trans


def _execute(input, script):
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.write(script)
    tmp.close()

    mode = os.stat(tmp.name)[stat.ST_MODE]
    os.chmod(tmp.name, mode | stat.S_IXUSR)

    t_start = time.time.time()
    ts_start = time.format_time_with_offset(t_start)

    proc = subprocess.Popen(tmp.name, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    output = proc.communicate(input)[0]
    os.unlink(tmp.name)
    if proc.returncode != 0:
        print("ERROR: Execution failed with status code %u" % proc.returncode, file=sys.stderr)
        return 1

    t_end = time.time.time()
    ts_end = time.format_time_with_offset(t_end)

    return output, ts_start, ts_end


def command_copy(trans_pid):
    "Copy a transformation (PID), return new PID."
    g = Gentle(fs_based)

    # Get the transformation document:
    trans_pid = g.p.findone(trans_pid)
    trans = _json_loadp(g, trans_pid)

    # Copy the output document:
    output_cid = g.p[trans["Output:json:pointer"]]
    new_output_pid = utilities.random()
    g.p[new_output_pid] = output_cid
    trans["Output:json:pointer"] = new_output_pid

    # Create new transformation content, assigning to new PID:
    new_pid = utilities.random()
    g.p[new_pid] = g.c + json.dumps(trans)

    # Return new PID:
    print(new_pid)
    return 0


def command_exec(trans_p):
    "Execute a gentle transformation."
    g = Gentle(fs_based)

    trans_p = g.p.findone(trans_p)
    trans = _json_loadp(g, trans_p)

    exec_p = trans["Exec:json:pointer"]
    exec_ = _json_loadp(g, exec_p)
    exec_output_valid_for_secs = exec_["Output valid for:seconds"]

    # Grab the input key:
    input_key = [k for k in trans.keys() if k.startswith("Input:") or k == "Input"]
    if len(input_key) != 1:
        print("ERROR: Bad 'Input' key - should occur exactly once:", file=sys.stderr)
        json.pprint(trans)
        return 1
    input_key = input_key[0]

    # Freeze the transformation; this will be used in the output:
    trans_f, trans_f_doc = _freeze_trans(g, trans, trans_p, input_key)

    # First, look at the previous output - it might still be valid:
    output_p = trans["Output:json:pointer"]
    prev_output = _json_loadp(g, output_p)
    if "Transformation:json:content" in prev_output:
        t = json.loads(g.c[prev_output["Transformation:json:content"]])
        t_minus_output = t.copy()
        del t_minus_output["Output:json:content"]
        trans_f_doc_minus_output = trans_f_doc.copy()
        del trans_f_doc_minus_output["Output:json:content"]
        if t_minus_output == trans_f_doc_minus_output:
            e = json.loads(g.c[t["Exec:json:content"]])
            if e["Output valid for:seconds"] == -1:
                print("Transformation the same and output still valid - not executing", file=sys.stderr)
                return 0
            if False:  # TODO: implement 'Output valid for:seconds' check
                if "End:timestamp" in prev_output:
                    t, offset = time.parse_time_with_offset(prev_output["End:timestamp"])
                    # TODO: Implement
                    return 0

    # Grab the input:
    input = trans[input_key]
    input_orig = input
    input_type = input_key.split(":")[1:]
    if input_type[-1:] == ["pointer"]:
        input_type[-1] = "content"
        input = g.p[input]
    if input_type[-1:] == ["content"]:
        input = g.c[input]

    script_p = exec_["Script:pointer"]
    script_c = g.p[script_p]
    script = g.c[script_c]

    output, ts_start, ts_end = _execute(input, script)

    outdoc = {
        "Transformation:json:content": trans_f,
        "Start:timestamp": ts_start,
        "Output:content": g.c + output,
        "End:timestamp": ts_end
    }
    g.p[output_p] = g.c + json.dumps(outdoc)


def command_help(*args):
    "Show the usage."
    print("Usage: %s command [args]" % sys.argv[0])
    print()
    print("Commands available:")
    commands = []
    for k in globals().keys():
        if k.startswith(CMD_PREFIX):
            commands.append((k[len(CMD_PREFIX):], globals()[k]))
    commands.sort()
    for (cmd_name, cmd_func) in commands:
        print("  %-12s %s" % (cmd_name, cmd_func.__doc__))
    return 0


def command_pipe(script_pid):
    "Pipe through a script (given as PID)."
    script_pid = g.p.findone(script_pid)
    script_code = g.c[g.p[script_pid]]
    print("WORK IN PROGRESS / Not yet implemented", file=sys.stderr)
    return 1


def command_prepare(input, exec_):
    "Prepare some input for transformation."
    g = Gentle(fs_based)
    exec_ = g.p.find(exec_)[0]

    input_type = ""
    input_id = None
    m = re.match(r'^([:a-z]+)=(.*)$', input)
    if m:
        input_type, input = m.groups()
    if input == "-":  # take it from stdin
        input = sys.stdin.read()
    elif os.path.exists(input):  # take it from the file
        input = open(input, "rb").read()
    else:  # try gentle
        try:
            found_p = g.p.find(input)
            found_c = g.c.find(input)
        except:  # happens if input is not a valid identifier, which is fine
            pass
        else:  # input is a valid identifier
            combined_len = len(found_p) + len(found_c)
            if combined_len > 1:
                print("Ambiguous identifier: %r" % input)
                return 1
            if combined_len == 1:
                if found_c:
                    input_id = found_c[0]
                    input_type += ":content"
                else:
                    input_id = found_p[0]
                    input_type += ":pointer"
    if input_type and not input_type.startswith(":"):
        input_type = ":" + input_type

    if input_id is None:
        if ":json:" in "%s:" % input_type:
            # Canonicalize:
            obj = json.loads(input)
            input = json.dumps(obj)
        if input_type.endswith(":content"):
            input_id = g.c + input
            input = input_id
        elif input_type.endswith(":pointer"):
            input_id = utilities.random()
            g.p[input_id] = g.c + input
            input = input_id

    if input_id is not None:
        input = input_id

    new_output_id = utilities.random()
    g.p[new_output_id] = g.c + "{}"

    doc = {
        "Exec:json:pointer": exec_,
        ("Input%s" % input_type): input,
        "Output:json:pointer": new_output_id
    }
    new_doc_id = utilities.random()
    g.p[new_doc_id] = g.c + json.dumps(doc)

    #origin_doc = {
    #    input_key: input_orig,
    #    "Exec:pointer": exec_p,
    #    "Exec (frozen):content": g.p[exec_p],
    #    "Script (frozen):content": script_c
    #}
    #input_type = input_key.split(":")[1:]
    #if input_type[-1:] == ["pointer"]:
    #    origin_doc["Input (frozen):content"] = g.p[input_orig]
    #output_doc = {
    #    "Origin": origin_doc
    #}
    #g.p[new_output_id] = g.c + json.dumps(output_doc)

    print(new_doc_id)
    return 0


def main(argv):
    if len(argv) < 2:
        return command_help()
    command_name = argv[1]
    command_key = CMD_PREFIX + command_name
    if command_key not in globals():
        print("Unknown command: " + command_name)
        print()
        return command_help()
    return globals()[command_key](*argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
