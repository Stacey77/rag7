"""Check every test-drive script in drives/*.json before it goes on the site.

Run: python3 nova-digitus-catalog/check_drives.py [file ...]
Prints one line per problem and exits 1 if any are found. Checks the schema, that every {input}
and {=expression} resolves, and that expressions give finite numbers at every input's min, max
and default (the same arithmetic the browser uses: numbers, + - * / ( ) and round/ceil/floor/min/max/abs).
"""
import glob, itertools, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FN = {"round": lambda x, d=0: round(x, int(d)), "ceil": math.ceil, "floor": math.floor,
      "min": min, "max": max, "abs": abs}
TOKEN = re.compile(r"\{(=?)([^{}]+)\}")


def evaluate(src, vars_):
    s, i = src, 0

    def ws():
        nonlocal i
        while i < len(s) and s[i] == " ":
            i += 1

    def atom():
        nonlocal i
        ws()
        if i < len(s) and s[i] == "(":
            i += 1; v = expr(); ws()
            if i >= len(s) or s[i] != ")": raise ValueError("missing )")
            i += 1; return v
        if i < len(s) and s[i] == "-":
            i += 1; return -atom()
        m = re.match(r"\d+(\.\d+)?", s[i:])
        if m:
            i += len(m.group(0)); return float(m.group(0))
        m = re.match(r"[A-Za-z_][A-Za-z0-9_]*", s[i:])
        if not m: raise ValueError(f"unexpected '{s[i:i+8]}'")
        name = m.group(0); i += len(name); ws()
        if i < len(s) and s[i] == "(":
            i += 1; args = []; ws()
            if s[i] != ")":
                while True:
                    args.append(expr()); ws()
                    if s[i] == ",": i += 1; continue
                    break
            if s[i] != ")" or name not in FN: raise ValueError(f"bad function {name}")
            i += 1; return float(FN[name](*args))
        if name not in vars_: raise ValueError(f"unknown input '{name}'")
        return float(vars_[name])

    def term():
        nonlocal i
        v = atom()
        while True:
            ws()
            if i < len(s) and s[i] == "*": i += 1; v *= atom()
            elif i < len(s) and s[i] == "/":
                i += 1; d = atom()
                if d == 0: raise ValueError("division by zero")
                v /= d
            else: return v

    def expr():
        nonlocal i
        v = term()
        while True:
            ws()
            if i < len(s) and s[i] == "+": i += 1; v += term()
            elif i < len(s) and s[i] == "-": i += 1; v -= term()
            else: return v

    v = expr(); ws()
    if i != len(s): raise ValueError(f"trailing '{s[i:]}'")
    if not math.isfinite(v): raise ValueError("not a finite number")
    return v


def texts(sc):
    yield "ask", sc["ask"]
    for k, st in enumerate(sc["steps"]): yield f"step {k+1}", st[1]
    yield "result title", sc["result"]["title"]
    for r in sc["result"]["rows"]: yield f"row '{r[0]}'", r[1]
    for q in sc.get("followups", []): yield f"follow-up '{q[0][:30]}'", q[1]


def check(path, names=None):
    errs = []
    def bad(msg): errs.append(f"{os.path.basename(path)}: {msg}")
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        return [f"{os.path.basename(path)}: not valid JSON ({e})"]
    if not isinstance(d.get("name"), str) or not d["name"]: bad("missing name")
    if names is not None and d.get("name") not in names: bad(f"name '{d.get('name')}' is not a catalog app")
    if not isinstance(d.get("tag"), str) or not (8 <= len(d["tag"]) <= 140): bad("tag must be 8-140 characters")
    scs = d.get("scenarios")
    if not isinstance(scs, list) or not (2 <= len(scs) <= 4): bad("needs 2-4 scenarios"); return errs
    for n, sc in enumerate(scs, 1):
        p = f"scenario {n}"
        for key in ("title", "ask", "steps", "result"):
            if key not in sc: bad(f"{p}: missing {key}")
        if errs: continue
        if not (3 <= len(sc["steps"]) <= 6) or any(not (isinstance(s, list) and len(s) == 2) for s in sc["steps"]):
            bad(f"{p}: steps must be 3-6 [agent, text] pairs")
        if not (3 <= len(sc["result"].get("rows", [])) <= 6): bad(f"{p}: result needs 3-6 rows")
        fu = sc.get("followups", [])
        if not (2 <= len(fu) <= 4) or any(not (isinstance(q, list) and len(q) == 2) for q in fu):
            bad(f"{p}: needs 2-4 followups as [question, answer]")
        ins = sc.get("inputs", [])
        if not (1 <= len(ins) <= 4): bad(f"{p}: needs 1-4 inputs")
        ids, numeric, ranges = set(), {}, []
        for inp in ins:
            iid = inp.get("id", "")
            if not re.fullmatch(r"[a-z][a-z0-9_]*", iid) or iid in ids or iid in FN: bad(f"{p}: bad input id '{iid}'"); continue
            ids.add(iid)
            if not inp.get("label"): bad(f"{p}: input {iid} has no label")
            if inp.get("type") == "select":
                opts = inp.get("options") or []
                if len(opts) < 2 or any("label" not in o or not isinstance(o.get("n"), (int, float)) for o in opts):
                    bad(f"{p}: select {iid} needs 2+ options with label and numeric n"); continue
                if inp.get("value") not in [o["label"] for o in opts]: bad(f"{p}: select {iid} default isn't an option")
                ranges.append((iid, [o["n"] for o in opts]))
            elif inp.get("type") == "range":
                lo, hi, v = inp.get("min"), inp.get("max"), inp.get("value")
                if not all(isinstance(x, (int, float)) for x in (lo, hi, v)) or not (lo <= v <= hi) or lo >= hi:
                    bad(f"{p}: range {iid} needs numeric min < max with min <= value <= max"); continue
                ranges.append((iid, sorted({lo, hi, v})))
            else:
                bad(f"{p}: input {iid} type must be range or select")
        combos = [dict(zip([r[0] for r in ranges], vals)) for vals in itertools.product(*[r[1] for r in ranges])][:200] or [{}]
        for where, txt in texts(sc):
            if not isinstance(txt, str) or not txt.strip(): bad(f"{p}: {where} is empty"); continue
            for is_expr, body in TOKEN.findall(txt):
                if not is_expr:
                    if body not in ids: bad(f"{p}: {where} uses {{{body}}} but there's no such input")
                    continue
                for c in combos:
                    try: evaluate(body, c)
                    except Exception as e: bad(f"{p}: {where} {{={body}}} fails ({e}) at {c}"); break
    return errs


if __name__ == "__main__":
    files = sys.argv[1:] or sorted(glob.glob(os.path.join(HERE, "drives", "*.json")))
    names = None
    nf = os.path.join(HERE, "drives", "_apps.json")
    if os.path.exists(nf): names = {a["name"] for a in json.load(open(nf))}
    problems = []
    for f in files:
        if os.path.basename(f).startswith("_"): continue
        problems += check(f, names)
    for p in problems: print(p)
    print(f"{len([f for f in files if not os.path.basename(f).startswith('_')])} files checked, {len(problems)} problems")
    sys.exit(1 if problems else 0)
