#!/usr/bin/env python3
"""Unpack verified private assets and CD music; runtime disc access is unchanged."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import wave

sys.path.insert(0,str(Path(__file__).resolve().parent))
from n2o_disc import ROOT,SECTOR,USER,IsoReader,inspect,default_data_dir
from portable_support import beneath,relative_path,sha256,write_json


def asset_path(name):
    relative_path(name)
    suffix=Path(name).suffix.upper()
    category={".TIM":"assets/textures", ".TMD":"assets/models",
              ".TRM":"assets/maps", ".SND":"assets/soundbanks",
              ".TXT":"assets/text", ".STR":"movies", ".SXA":"movies",
              ".EXE":"system/executables"}.get(suffix,"system")
    if name.upper().startswith(("SLUS_","SLES_")):category="system/executables"
    return category+"/"+name


def plan_files(entries,tracks,total_sectors):
    data_end=tracks[1].get("pregap") if len(tracks)>1 else total_sectors
    if data_end is None:data_end=tracks[1]["start"]
    music=[]
    for index,track in enumerate(tracks[1:],1):
        following=tracks[index+1] if index+1<len(tracks) else None
        stop=(following.get("pregap") if following else total_sectors)
        if stop is None:stop=following["start"]
        start=track["start"];pregap=track.get("pregap")
        if not 0<=start<stop<=total_sectors or (pregap is not None and not data_end<=pregap<=start):
            raise ValueError("Invalid audio track extent")
        music.append(dict(track=track["number"],lba=start,sectors=stop-start,
                          pregap_lba=pregap,output=f"music/track-{track['number']:02}.wav",
                          representation="pcm-s16le-stereo-44100-wave"))
    files=[];seen=set()
    for entry in entries:
        name=relative_path(entry.path);key=name.casefold()
        if key in seen:raise ValueError("Duplicate asset name")
        seen.add(key)
        sectors=(entry.size+USER-1)//USER
        row=dict(source=name,lba=entry.lba,iso_size=entry.size,sectors=sectors)
        if entry.lba>=data_end:
            track=next((t for t in music if entry.lba==t["lba"] and sectors==t["sectors"]),None)
            if not track or entry.size%USER:raise ValueError("Unrecognized ISO audio alias")
            row.update(output=track["output"],representation="audio-track-alias",track=track["track"])
        else:
            if entry.lba<0 or entry.size<0 or entry.lba+sectors>data_end:
                raise ValueError("Asset extent exceeds data track")
            raw=Path(name).suffix.upper() in (".SXA",".STR")
            row.update(output=asset_path(name),representation="raw-2352-sectors" if raw else "iso-2048-payload")
        files.append(row)
    outputs=[r["output"].casefold() for r in files if r["representation"]!="audio-track-alias"]
    outputs += [t["output"].casefold() for t in music]
    if len(outputs)!=len(set(outputs)):raise ValueError("Asset output collision")
    return data_end,files,music


def raw_chunks(source,lba,sectors):
    source.seek(lba*SECTOR)
    while sectors:
        count=min(sectors,256);data=source.read(count*SECTOR)
        if len(data)!=count*SECTOR:raise ValueError("Disc changed or ended during extraction")
        yield data;sectors-=count


def extract(installation: Path,destination: Path,identity=None,progress=print):
    identity=identity or json.loads((ROOT/"configs/disc_usa.json").read_text())
    imported=json.loads((installation/"installation.json").read_text())
    current=inspect(Path(imported["cue"]),identity,progress)
    if current["game_id"]!=imported.get("game_id") or current["bin_sha256"]!=imported.get("bin_sha256"):
        raise ValueError("The import and verified disc differ")
    destination=destination.resolve()
    if destination.exists():raise ValueError("Asset folder already exists; existing files were preserved")
    total=identity["bin_size"]//SECTOR
    end=current["tracks"][1].get("pregap") if len(current["tracks"])>1 else total
    if end is None:end=current["tracks"][1]["start"]
    with IsoReader(Path(current["bin"]),end) as iso:
        _,entries=iso.inventory()
    end,files,music=plan_files(entries,current["tracks"],total)
    destination.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix=".n2o-assets-",dir=destination.parent))
    outputs={}
    def record(name):
        path=beneath(staging,name)
        outputs[name]=dict(size=path.stat().st_size,sha256=sha256(path))
    try:
        with Path(current["bin"]).open("rb") as raw,IsoReader(Path(current["bin"]),end) as iso:
            for row in files:
                if row["representation"]=="audio-track-alias":continue
                progress("Extracting "+row["output"])
                target=beneath(staging,row["output"]);target.parent.mkdir(parents=True,exist_ok=True)
                with target.open("wb") as out:
                    if row["representation"]=="raw-2352-sectors":
                        for chunk in raw_chunks(raw,row["lba"],row["sectors"]):out.write(chunk)
                    else:
                        remaining=row["iso_size"]
                        for sector in range(row["sectors"]):
                            chunk=iso.sector(row["lba"]+sector)[:remaining]
                            out.write(chunk);remaining-=len(chunk)
                record(row["output"])
            for track in music:
                progress("Extracting "+track["output"])
                target=beneath(staging,track["output"]);target.parent.mkdir(parents=True,exist_ok=True)
                # Match the pinned player's CD-DA byte interpretation. Keep
                # sample bytes intact; WAVE adds only its PCM container header.
                with wave.open(str(target),"wb") as wav:
                    wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(44100)
                    for chunk in raw_chunks(raw,track["lba"],track["sectors"]):wav.writeframesraw(chunk)
                record(track["output"])
                pregap=track["pregap_lba"]
                if pregap is not None and pregap<track["lba"]:
                    name=f"disc/pregaps/track-{track['track']:02}.pcm"
                    p=beneath(staging,name);p.parent.mkdir(parents=True,exist_ok=True)
                    with p.open("wb") as out:
                        for chunk in raw_chunks(raw,pregap,track["lba"]-pregap):out.write(chunk)
                    record(name);track["pregap_output"]=name
        # Check the complete original again before publishing an atomic folder.
        if sha256(Path(current["bin"]))!=current["bin_sha256"]:
            raise ValueError("Disc changed during extraction")
        manifest=dict(schema=1,kind="private-extracted-assets",game_id=current["game_id"],
                      bin_sha256=current["bin_sha256"],files=files,music=music,outputs=outputs,
                      runtime_uses_catalog=False,
                      note="Original containers remain encoded. Movies retain raw sectors; CD audio aliases refer to WAVE tracks. Disc metadata/padding is not reconstructed; keep the CUE/BIN for runtime access.")
        write_json(staging/"asset-manifest.json",manifest)
        if destination.exists():raise ValueError("Asset destination appeared during extraction")
        os.rename(staging,destination)
        return manifest
    except BaseException:
        shutil.rmtree(staging,ignore_errors=True)
        raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--installation",type=Path,default=default_data_dir()/"SLUS-00637")
    p.add_argument("--output",type=Path,default=ROOT/".local/game")
    args=p.parse_args()
    if ".local" not in args.output.resolve().parts:p.error("Extracted assets must stay in a private .local folder")
    result=extract(args.installation,args.output)
    print(f"Extracted {len(result['files'])} file records and {len(result['music'])} music tracks to {args.output.resolve()}")
    print("Runtime still needs the original disc. This catalog does not enable replacement packs yet.")


if __name__=="__main__":main()
