# USA disc findings — 2026-10-25

Directly inspected the supplied merged BIN/CUE. No game bytes are in this report.

| Item | Observed value |
| --- | --- |
| Boot identity | SLUS-00637 |
| Volume label | N2O |
| Raw sector size | 2352 bytes, Track 1 MODE2 |
| BIN size | 540,680,112 bytes |
| Tracks | 1 data + 10 audio |
| BIN SHA-256 | `99b2e8c6c61dfaf64755e5164f25b6f6ad4598556ecfef585e21dbc6128757ae` |

That hash covers the **entire merged BIN including audio**, not merely Track 1.
The upstream probe labels its first-BIN hash `data_track_*`; for this merged layout
those values also cover the entire file. Do not present them as Redump Track 1
hashes or use them to reject a separately verified split-track image.

| Executable | File size | Load address | Entry address | Header text size |
| --- | ---: | --- | --- | ---: |
| SLUS_006.37 | 55,296 | 0x80010880 | 0x80012E24 | 53,248 |
| N2O.EXE | 460,800 | 0x80021500 | 0x80021500 | 458,752 |
| NEW.EXE | 335,872 | 0x80021500 | 0x80023550 | 333,824 |

The disc also contains `SLES_008.09`; its presence alone does not prove support
for the European release. It is not used for the USA import.

The two larger executables overlap in PS1 RAM. Their actual load order and
lifetimes must be traced before integrating native dispatch. Their file presence
and header values do not establish which is used for each gameplay state.

Data files include `.TIM`/`.TMD`, `PSXMAP.TRM`, `PSXSND.SND`, `.SXA`/`.STR` files,
and ten `DA/*.RAW` directory entries. No assumptions about the custom map/sound
formats or audio/file aliasing have been validated. Preserve the original full
disc track layout when investigating playback.

Initial JAL scans yielded 117 boot-loader, 644 N2O.EXE and 225 NEW.EXE address
candidates. These include possible data false positives and **are not confirmed
function counts**. Whole-image emitter discovery over-expanded NEW.EXE to over
26 million C lines; that output was rejected as a starting point. The current
developer command trusts only each EXE's header entry and uses reachable discovery.
It is deliberately incomplete at indirect transfers until evidence is added.
