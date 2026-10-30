# Private asset folders and future replacement packs

Asset extraction can proceed alongside native conversion. It does not depend on
100% linked translation coverage or logic/render clock separation. The first
extractor organizes the player's verified original content into private folders
and records its identities; runtime migration is a separate compatibility step.

## Extract with the portable Windows release

Open PowerShell in the extracted Nitrogen-Squared folder and run:

```powershell
.\support\python\python.exe -I -X utf8 -B .\app\tools\extract_assets.py --installation .\.local\installation --output .\.local\game
```

Use the existing verified installation after launcher preparation. The original
CUE/BIN must still be available. In a source checkout, the equivalent command is
`python tools/extract_assets.py --output .local/game`; its default import location
is the existing developer user-data installation. Pass --installation explicitly
when using a different import.

The extractor verifies the complete disc, prepares a new folder atomically and
never overwrites an existing destination. This protects edits made for later mod
work. Use a different private .local destination to make another original copy.
Launcher updates preserve these private files. Extracted game content must remain
out of Git, public source packages and releases.

| Folder under .local/game | Content and representation |
| --- | --- |
| assets/textures | Original TIM texture containers |
| assets/models | Original TMD model containers |
| assets/maps | Original TRM map container |
| assets/soundbanks | Original SND sound-bank container |
| assets/text | Original text files, preserving their source paths |
| movies | Complete 2352-byte sector streams, retaining video headers and interleaved XA audio |
| music | Ten PCM WAVE music tracks, 44.1 kHz, stereo, signed 16-bit little endian |
| system | Original system files and executable inputs |
| disc/pregaps | Original PCM sectors preceding audio-track index 1 |

The music filenames use the CUE's track numbers: track 1 is data, so music begins
at track-02.wav. ISO DA/*.RAW entries alias audio tracks; they are recorded as
aliases of the WAVE outputs rather than misread as ordinary 2048-byte ISO data.
The private asset-manifest.json maps all original file names and extents to output
paths and representations, with sizes/SHA-256 hashes. The verified USA layout has
27 ISO file records, ten music tracks and 37 output files including pregaps.
Movie outputs keep their original filename extension, but contain raw sectors;
the manifest explicitly identifies that representation. TIM/TMD/TRM/SND remain
original containers. Exporting their internal resources into editing formats is
further work.

## Runtime migration and replacement packs

The current runtime still uses the original BIN. The catalog is an extraction
and inspection tool; changing its files does not yet change in-game resources.
Keep the original CUE/BIN. ISO metadata, padding and all data-sector framing are
not reconstructed into a replacement disc by this tool.

Next steps are to identify each loader/resource boundary, make normal loads read
verified folder files, and retain the original sector/track behavior where needed.
Qualify map/model/texture loading, XA movies, CD music, seeks, transitions and
saves against the accepted baseline before changing default access. This can be
done incrementally before full code linkage. No frame-clock change is needed.

Future packs should contain original replacement assets plus a manifest naming
resource IDs, formats and compatibility. Their identity, supported sizes/layouts,
load order and fallback need explicit rules. Packs must preserve the original
private extraction; launcher updates must preserve both. Mod loading, editing
format conversion and BIN-free runtime access are not enabled by this first step.
