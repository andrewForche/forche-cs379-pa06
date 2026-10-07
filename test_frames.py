"""
PA 6: The Activation Record -- verification suite.

Run: python test_frames.py
Prints ACTIVATION_RECORD_VERIFIED only if every check below passes
(this PA's success signal is a fixed literal string, not a generated
token -- see the assignment, Part B).
"""

import sys

from frames import ActivationRecord, CallStack
from symtable import Environment


def check(label: str, condition: bool, failures: list) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}")
    if not condition:
        failures.append(label)


def run_nested_example(global_env: Environment, stack: CallStack):
    """
    A nested function: `outer` defines `inner` in its own body. `inner`
    is CALLED from within `outer` (so outer's frame is inner's dynamic
    caller), and `inner` is LEXICALLY DEFINED inside outer's scope (so
    outer's frame is also inner's static parent) -- for THIS particular
    nesting shape static_link and dynamic_link end up pointing at the
    same frame either way, EXCEPT we additionally call inner a second
    time from a sibling call one level removed, so the two links can be
    told apart: static_link always points at outer's frame (where inner
    was defined), dynamic_link points at whichever frame actually
    performed this specific call.
    """
    outer_env = Environment(parent=global_env)
    outer_record = ActivationRecord("outer", {}, outer_env, "call site for outer()", static_link=None, dynamic_link=None)
    stack.push(outer_record)

    # inner() is lexically defined inside outer, so its static parent is outer's frame.
    inner_env = Environment(parent=outer_env)
    # Call inner NOT directly from outer, but through one more frame, so
    # dynamic_link (actual caller) differs from static_link (defining scope).
    relay_env = Environment(parent=global_env)
    relay_record = ActivationRecord("relay", {}, relay_env, "call site for relay()", static_link=None, dynamic_link=outer_record)
    stack.push(relay_record)

    inner_record = ActivationRecord("inner", {}, inner_env, "call site for inner()", static_link=outer_record, dynamic_link=relay_record)
    stack.push(inner_record)

    result = (inner_record, outer_record, relay_record)

    stack.pop()  # inner
    stack.pop()  # relay
    stack.pop()  # outer
    return result


def main() -> int:
    failures: list = []
    global_env = Environment()

    print("Running factorial(5) simulation...\n")
    stack = CallStack()
    depths = []

    def instrumented_run(n, genv, st, dynamic_caller=None):
        locals_env = Environment(parent=genv)
        locals_env.define("n", 0)
        record = ActivationRecord("factorial", {"n": n}, locals_env, f"call site for factorial({n})", None, dynamic_caller)
        st.push(record)
        depths.append(len(st.trace()))
        if n <= 1:
            result = 1
        else:
            result = n * instrumented_run(n - 1, genv, st, dynamic_caller=record)
        popped = st.pop()
        return result

    instrumented_run(5, global_env, stack)
    check("stack is empty after factorial(5) fully unwinds", len(stack.trace()) == 0, failures)
    check("call stack reached exactly 5 live frames at maximum depth", max(depths) == 5, failures)

    print("\nChecking dynamic_link correctness during a fresh factorial(4) run...\n")
    stack2 = CallStack()
    records_seen = []

    def tracking_run(n, genv, st, dynamic_caller=None):
        locals_env = Environment(parent=genv)
        locals_env.define("n", 0)
        record = ActivationRecord("factorial", {"n": n}, locals_env, f"call site for factorial({n})", None, dynamic_caller)
        st.push(record)
        records_seen.append(record)
        if n > 1:
            tracking_run(n - 1, genv, st, dynamic_caller=record)
        st.pop()

    tracking_run(4, global_env, stack2)
    check(
        "each frame's dynamic_link matches the frame that actually called it",
        all(records_seen[i].dynamic_link is records_seen[i - 1] for i in range(1, len(records_seen))),
        failures,
    )
    check("the outermost frame's dynamic_link is None (nothing called it)", records_seen[0].dynamic_link is None, failures)

    print("\nRunning the nested-function example...\n")
    stack3 = CallStack()
    inner_record, outer_record, relay_record = run_nested_example(global_env, stack3)
    check("nested example: static_link points to the DEFINING scope (outer)", inner_record.static_link is outer_record, failures)
    check("nested example: dynamic_link points to the actual CALLER (relay)", inner_record.dynamic_link is relay_record, failures)
    check("nested example: static_link and dynamic_link differ", inner_record.static_link is not inner_record.dynamic_link, failures)
    check("stack is empty after the nested example unwinds", len(stack3.trace()) == 0, failures)

    print("\nTesting CallStack.current()...\n")
    stack4 = CallStack()
    r1 = ActivationRecord("f", {}, Environment(), "cs1", None, None)
    r2 = ActivationRecord("g", {}, Environment(), "cs2", None, r1)
    stack4.push(r1)
    stack4.push(r2)
    check("current() returns the top frame without removing it", stack4.current() is r2, failures)
    check("current() didn't pop anything (stack still has 2 frames)", len(stack4.trace()) == 2, failures)

    print()
    if failures:
        print(f"{len(failures)} check(s) failed. No token issued.")
        return 1

    print("ACTIVATION_RECORD_VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
