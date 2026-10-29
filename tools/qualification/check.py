#!/usr/bin/env python3
"""Exercise original diagnostic-controller logic, without running game code."""
import argparse
import json
import os
from pathlib import Path
import subprocess
from route import ROOT, private_output
from selection import build_selection, selection_text


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",required=True,type=private_output)
    p.add_argument("--framework",type=Path,default=ROOT/".local/psxrecomp")
    args=p.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
    binary=out/"qualification-controller-test"
    subprocess.run(["c++","-std=c++17","-O1","-I"+str(args.framework/"runtime/include"),
                    str(ROOT/"tools/qualification/compare.cpp"),str(ROOT/"tests/qualification_compare_smoke.cpp"),
                    "-o",str(binary)],check=True)
    items=[];specs=[]
    for image,crc,sha in [("FIRST",123,"a"*64),("SECOND",456,"b"*64)]:
        items.append(dict(executable=image,entries=[0x80020000],resume_entries=[dict(owner=0x80020000,entry=0x80020004)],
                          identities=[dict(owner=0x80020000,crc=crc,code_sha256=sha,ranges=[[0x80020000,8]])]))
        specs.append(dict(executable=image,start="0x80020000",size=16,entries=["0x80020000"]))
    rows=build_selection(dict(slices=items),specs);text=selection_text(rows)
    cases=[("images",text,0),("trace",text,0),("preblocked",text,0),("collect",text,91),("failfast",text,91),("budget",text,91),
           ("legacy","80020000 10\n",0),("wrong-id",text,0),
           ("tail","80020000 10\n80020000\n",92),("truncated",text.rsplit(" ",1)[0]+"\n",92),
           ("duplicate",text+text.splitlines()[1]+"\n",92)]
    results=[]
    for mode,selector,expected in cases:
        d=out/mode;d.mkdir(exist_ok=True);selection=d/"selection.tsv";selection.write_text(selector)
        env=os.environ.copy();env.update(N2O_COMPARE="1",N2O_SELECTION=str(selection))
        env.pop("N2O_COLLECT_FAILURES",None);env.pop("N2O_REPLAY_ID",None);env.pop("N2O_BLOCKED_IDS",None)
        if mode=="preblocked":
            disabled=d/"disabled.txt";disabled.write_text(next(r["id"] for r in rows if r["crc"]==123)+"\n")
            env["N2O_BLOCKED_IDS"]=str(disabled)
        env.pop("N2O_TRACE_MISSES",None)
        if mode=="trace":env["N2O_TRACE_MISSES"]="1"
        if mode=="collect":env["N2O_COLLECT_FAILURES"]="1"
        if mode=="wrong-id":env["N2O_REPLAY_ID"]=next(r["id"] for r in rows if r["crc"]==456)
        proc=subprocess.run([str(binary),mode],cwd=d,env=env,capture_output=True,text=True,timeout=20)
        (d/"runtime.log").write_text(proc.stdout+proc.stderr)
        if proc.returncode!=expected:raise RuntimeError(f"Controller test {mode}: {proc.returncode}, expected {expected}: {proc.stdout}{proc.stderr}")
        if mode=="images":
            summary=(d/"qualification-summary.txt").read_text().splitlines()
            assert "comparisons=4 failures=0 pcs=4" in summary[0] and len(list(d.glob("call-*.bin")))==4
        if mode=="collect":
            assert "TOOLS_SMOKE_PASS" in proc.stdout
            summary=(d/"qualification-summary.txt").read_text().splitlines()[0]
            assert "comparisons=3 failures=1 pcs=2" in summary
            assert (d/"blocked-identities.txt").read_text().strip()==next(r["id"] for r in rows if r["crc"]==123)
        if mode=="preblocked":assert "comparisons=2 failures=0 pcs=2" in (d/"qualification-summary.txt").read_text().splitlines()[0]
        if mode=="wrong-id":assert "TOOLS_SMOKE_PASS" in proc.stdout and not (d/"qualification-summary.txt").exists()
        if mode=="trace":assert len((d/"untranslated-pcs.tsv").read_text().splitlines())==1
        results.append(dict(case=mode,returncode=proc.returncode))
    (out/"results.json").write_text(json.dumps(results,indent=2)+"\n")
    print("QUALIFICATION_CONTROLLER_PASS",len(results))


if __name__=="__main__":main()
