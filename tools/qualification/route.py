#!/usr/bin/env python3
"""Original deterministic input route; screenshots and device reports stay private."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]


def private_output(value):
    path = Path(value).resolve()
    path.relative_to(ROOT / ".local")
    return path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", required=True, type=private_output)
    p.add_argument("--binary", type=Path, default=ROOT / ".local/runtime-dev/build/NitrogenSquared-dev")
    p.add_argument("--game", type=Path, default=ROOT / ".local/runtime-dev/game.toml")
    p.add_argument("--disc", required=True, type=Path)
    p.add_argument("--port", type=int, default=4370)
    p.add_argument("--timeout", type=float,
                   help="Wall-clock budget in seconds (default: 600; 1200 for --deep)")
    p.add_argument("--help-prompts", action="store_true")
    p.add_argument("--alternate-ship", action="store_true", help="Select another ship with ordinary D-pad input")
    p.add_argument("--alternate-difficulty", action="store_true", help="Change difficulty with ordinary D-pad input")
    p.add_argument("--extended", action="store_true", help="Extend ordinary controller play and scanouts through frame 12300")
    p.add_argument("--long", action="store_true", help="Extend ordinary controller play and scanouts through frame 18300")
    p.add_argument("--deep", action="store_true", help="Extend ordinary controller play and scanouts through frame 36300")
    p.add_argument("--combat-inputs", action="store_true", help="Add short ordinary face-button presses during extended gameplay")
    args = p.parse_args()
    if args.deep:args.long=True
    if args.long:args.extended=True
    if args.timeout is None:args.timeout=1200 if args.deep else 600
    if not 0 < args.timeout <= 1800:
        raise ValueError("Route timeout must be between 0 and 1800 seconds")
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(SDL_VIDEODRIVER="offscreen", SDL_AUDIODRIVER="dummy", EGL_PLATFORM="surfaceless",
               PSX_OVERLAY_AUTOCOMPILE_OFF="1", PSX_DISPLAY_RING="1", PSX_DEBUG_TOGGLES="0",
               PSX_RENDER_THREAD="1", PSX_RENDER_THREAD_FRAMES="1",
               NITROGEN_NATIVE_DISC_BIN=str(args.disc.resolve()),
               PSX_OVERLAY_CAPTURES=str(out / "overlay_captures.json"),
               PSX_OVERLAY_CAPTURE_ROOT=str(out / "overlay-private"))

    def request(command, **kwargs):
        with socket.create_connection(("127.0.0.1", args.port), timeout=3) as sock:
            sock.settimeout(15)
            sock.sendall((json.dumps(dict(id=1, cmd=command, **kwargs)) + "\n").encode())
            data = b""
            while True:
                block = sock.recv(65536)
                if not block:
                    raise RuntimeError("Debug connection closed without a response")
                data += block
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    pass

    with (out / "runtime.log").open("w") as log:
        proc = subprocess.Popen([str(args.binary.resolve()), "--game", str(args.game.resolve()),
                                 "--no-launcher", "--renderer", "opengl", "--hidden-window",
                                 "--debug-port", str(args.port), "--memcard-dir", str(out / "cards")],
                                cwd=out, env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(600):
                if proc.poll() is not None:
                    raise RuntimeError(f"Early runtime exit: {proc.returncode}")
                try:
                    request("frame")["frame"]
                    break
                except (OSError, KeyError):
                    time.sleep(.1)
            else:
                raise RuntimeError("No diagnostic server")
            request("input_route_clear")
            for n in range(6):
                request("input_route_append", buttons=0xEFFF if n == 4 and not args.help_prompts else 0xBFFF, frames=20)
                if (n == 1 and args.alternate_ship) or (n == 2 and args.alternate_difficulty):
                    request("input_route_append", buttons=0xFFFF, frames=40)
                    request("input_route_append", buttons=0xFFDF, frames=20)
                    request("input_route_append", buttons=0xFFFF, frames=120)
                else:
                    request("input_route_append", buttons=0xFFFF, frames=180)
            for buttons, frames in [(0xBFFF,240),(0xBFDF,180),(0xBF7F,180),(0xBFFF,400),
                                    (0xBFFF,200),(0xFFF7,20),(0xFFFF,180),(0xFFF7,20),(0xFFFF,180),
                                    (0xBFDF,400),(0xBF7F,500),(0xBFFF,600)]:
                request("input_route_append", buttons=buttons, frames=frames)
            if args.extended:
                for loop in range(20 if args.deep else 8 if args.long else 4):
                    for part, (buttons, frames) in enumerate([(0xBFFF,500),(0xBFDF,500),(0xBFFF,100),(0xBF7F,500),(0xFFFF,20),(0xBFFF,20)]):
                        if args.combat_inputs and part == 0:
                            request("input_route_append", buttons=buttons & ~(0x1000,0x2000,0x8000)[loop % 3], frames=20)
                            frames -= 20
                        request("input_route_append", buttons=buttons, frames=frames)
            print(request("input_route_start", at_frame=1800), flush=True)
            frames = [800,1500,1900,2100,2300,2500,2700,3000,3500,4000,4200,4300,4500,4700,5000,5500,6000]
            if args.extended:
                frames += [7500,9000,10500,12000]
            if args.long:
                frames += [13500,15000,16500,18000]
            if args.deep:
                frames += list(range(19500,36001,1500))
            done = set()
            deadline = time.monotonic() + args.timeout
            while time.monotonic() < deadline:
                if proc.poll() is not None:
                    raise RuntimeError(f"Runtime exit: {proc.returncode}")
                frame = request("frame")["frame"]
                for target in frames:
                    if target not in done and frame >= target + 3:
                        result = request("display_ring_get", frame=target, path=str(out / f"frame-{target}.png"))
                        if not result.get("ok"):
                            raise RuntimeError(str(result))
                        print(target, result, flush=True)
                        done.add(target)
                if frame >= (36300 if args.deep else 18300 if args.long else 12300 if args.extended else 6300):
                    break
                time.sleep(.15)
            else:
                raise RuntimeError("Route timeout")
            for command in ["overlay_loader_status","audio_stats","render_thread","pad_status","dirty_ram_stats","dispatch_stats"]:
                (out / (command + ".json")).write_text(json.dumps(request(command), indent=2))
            print(request("quit"), flush=True)
            proc.wait(timeout=20)
            if proc.returncode:
                raise RuntimeError(f"Shutdown exit: {proc.returncode}")
            print("ROUTE_PASS", len(done), frame, flush=True)
        finally:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=20)


if __name__ == "__main__":
    main()
