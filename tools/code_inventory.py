"""Evidence-labelled private code/data inventory; never infer a code-only percent.

Reports ranges and hashes only. Static and string hints remain hypotheses, and
an observed short prefix is not executable identity or qualification evidence.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re

from n2o_disc import ROOT,digest,exe_header
from native_progress import covered_ranges,report


def merge(spans):
    result=[]
    for lo,hi in sorted(spans):
        if lo>=hi:raise ValueError("Empty or reversed inventory range")
        if result and lo<=result[-1][1]:result[-1]=(result[-1][0],max(hi,result[-1][1]))
        else:result.append((lo,hi))
    return result


def subtract(spans,removed):
    remaining=[]
    for lo,hi in merge(spans):
        at=lo
        for start,end in merge(removed):
            if end<=at:continue
            if start>=hi:break
            if start>at:remaining.append((at,min(start,hi)))
            at=max(at,end)
            if at>=hi:break
        if at<hi:remaining.append((at,hi))
    return remaining


def intersect(a,b):
    return merge([(max(lo,x),min(hi,y)) for lo,hi in merge(a) for x,y in merge(b) if max(lo,x)<min(hi,y)])


def size(spans):return sum(hi-lo for lo,hi in spans)


def fnv(data):
    value=14695981039346656037
    for byte in data:value=((value^byte)*1099511628211)&0xffffffffffffffff
    return value


def range_text(text,base,length):
    covered_ranges(text,base,length)
    return merge([(int(p[1],16),int(p[1],16)+int(p[2],16)) for line in text.splitlines() if (p:=line.split()) and p[0]=="R"])


def classify(payload,base,linked,analysis):
    end=base+len(payload)
    for lo,hi in linked:
        if not base<=lo<hi<=end:raise ValueError("Linked range outside payload")
    static_code=[];data=[]
    for f in analysis.get("functions",[]):
        lo,hi=f["addr"],f["end"]
        if not base<=lo<hi<=end:raise ValueError("Analysis function outside payload")
        if f.get("is_data"):data.append((lo,hi))
        elif not f.get("partial") and f.get("confidence") in ("verified","high","medium"):
            static_code.append((lo,hi))
    # Printable NUL-terminated runs are only data hints: instruction bytes can
    # coincidentally be printable too. Never use this to suppress code discovery.
    data += [(base+m.start(),base+m.end()) for m in re.finditer(rb"[\x20-\x7e]{8,}\x00",payload)]
    linked=merge(linked)
    conflict=subtract(intersect(static_code,data),linked)
    static_only=subtract(static_code,linked+data)
    data_only=subtract(data,linked+static_code)
    unknown=subtract([(base,end)],linked+static_code+data)
    buckets=dict(linked_translation=linked,static_code_hint=static_only,data_hint=data_only,
                 conflicting_hints=conflict,unclassified=unknown)
    assert sum(map(size,buckets.values()))==len(payload)
    return {key:dict(bytes=size(value),ranges=[[lo,hi-lo] for lo,hi in value]) for key,value in buckets.items()}


def load_inputs(installation):
    identity=json.loads((ROOT/"configs/disc_usa.json").read_text())
    result={}
    for item in identity["executables"]:
        path=installation/"executables"/item["path"]
        if path.stat().st_size!=item["size"] or digest(path)!=item["sha256"]:
            raise ValueError("Executable does not match the verified identity: "+item["path"])
        data=path.read_bytes();header=exe_header(data)
        result[item["path"]]=dict(payload=data[2048:2048+header["text_size"]],base=header["load_address"],sha256=item["sha256"])
    return result


def trace_entries(paths,images):
    result={name:set() for name in images}
    for path in paths:
        for line in path.read_text().splitlines():
            fields=line.split()
            if len(fields)!=4:raise ValueError("Malformed private PC trace")
            _,pc,prefix,_=[int(v,16) if i<3 else int(v) for i,v in enumerate(fields)]
            if pc%4:raise ValueError("Unaligned trace PC")
            for name,image in images.items():
                offset=pc-image["base"]
                if 0<=offset<=len(image["payload"])-32 and fnv(image["payload"][offset:offset+32])==prefix:
                    result[name].add(pc)
    return result


def propose(images,linked,analyses,observed,exclusions):
    roots=[]
    for name,image in images.items():
        base=image["base"];end=base+len(image["payload"])
        denied=[(int(e["start"],16),int(e["start"],16)+e["size"]) for e in exclusions if e["executable"]==name]
        functions={f["addr"]:f for f in analyses.get(name,{}).get("functions",[])}
        seeds=set(observed[name])|{pc for pc,f in functions.items() if not f.get("is_data") and not f.get("partial") and f.get("ends_jr_ra") and f.get("confidence") in ("verified","high","medium")}
        for pc in sorted(seeds):
            if any(lo<=pc<hi for lo,hi in linked[name]+denied):continue
            if name=="NEW.EXE" and pc<0x80024000:continue
            exact=functions.get(pc)
            containing=exact or next((f for f in functions.values() if f["addr"]<=pc<f["end"]),None)
            if exact and (exact.get("partial") or exact.get("sig",{}).get("syscall") or exact.get("sig",{}).get("mmio")):continue
            stops=[end,pc+65536]
            if containing:stops.append(containing["end"])
            stops += [lo for lo,hi in linked[name]+denied if lo>pc]
            stops += [s for s in seeds if s>pc]
            stop=min(stops)
            stop-=stop%4
            if stop<=pc:continue
            roots.append(dict(executable=name,start=f"0x{pc:08X}",size=stop-pc,entries=[f"0x{pc:08X}"],
                              purpose="Observed indirect entry" if pc in observed[name] else "Static code candidate; qualification required"))
    return roots


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--work-dir",type=Path,default=ROOT/".local/runtime-dev")
    p.add_argument("--analysis",type=Path,action="append",default=[])
    p.add_argument("--trace",type=Path,action="append",default=[])
    p.add_argument("--exclusions",type=Path,default=ROOT/"configs/native_exclusions_usa.json")
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--candidates",type=Path)
    args=p.parse_args()
    for path in [args.output]+([args.candidates] if args.candidates else []):path.resolve().relative_to(ROOT/".local")
    receipt=json.loads((args.work_dir/"runtime-build.json").read_text())
    progress=report(args.work_dir)
    images=load_inputs(Path(receipt["installation"]))
    linked={name:[] for name in images}
    for selected in receipt.get("native_slices",[]):
        manifest=Path(selected["manifest"])
        for item in json.loads(manifest.read_text())["slices"]:
            image=images[item["executable"]]
            linked[item["executable"]]+=range_text((manifest.parent/item["ranges"]).read_text(),image["base"],len(image["payload"]))
    for name in receipt["linked_executables"]:
        image=images[name]
        linked[name]+=range_text((Path(receipt["generated_dir"])/name/(name+"_full.ranges")).read_text(),image["base"],len(image["payload"]))
    linked={name:merge(spans) for name,spans in linked.items()}
    analyses={}
    for path in args.analysis:
        value=json.loads(path.read_text());name=value["image"]
        if name not in images or value.get("source_sha256")!=images[name]["sha256"] or value.get("image_size")!=len(images[name]["payload"]):
            raise ValueError("Static analysis lacks the verified source identity")
        if name in analyses:raise ValueError("Duplicate static image analysis")
        analyses[name]=value
    observed=trace_entries(args.trace,images)
    rows=[]
    for name,image in images.items():
        buckets=classify(image["payload"],image["base"],linked[name],analyses.get(name,{}))
        rows.append(dict(executable=name,source_sha256=image["sha256"],payload_bytes=len(image["payload"]),
                         buckets=buckets,observed_prefix_entries=sorted(observed[name])))
    result=dict(schema=1,kind="evidence-labelled-code-data-inventory",executables=rows,
                linked_metric=progress,note="Hints are not proven code/data. Unknown bytes remain unknown; no code-only denominator or qualification credit is inferred.")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    if args.candidates:
        exclusions=json.loads(args.exclusions.read_text())
        candidates=propose(images,linked,analyses,observed,exclusions)
        args.candidates.write_text(json.dumps(candidates,indent=2)+"\n")
        print(f"Private candidate metadata: {len(candidates)} roots; none is qualified by discovery")
    for row in rows:print(row["executable"],{k:v["bytes"] for k,v in row["buckets"].items()},"prefix entries",len(row["observed_prefix_entries"]))


if __name__=="__main__":main()
