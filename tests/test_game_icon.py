"""Original synthetic icon fixtures; no commercial palette or bitmap bytes."""
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import zlib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from prepare_icon import decode_icon,png_bytes,ico_bytes,prepare_icon,write_icons


class GameIconTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='Original icon with spaces ')
        self.root=Path(self.temp.name);self.install=self.root/'installation'
        self.output=self.root/'.local/private game icon'
        self.palette=struct.pack('<16H',0,31,31<<5,31<<10,*range(4,16))
        self.packed=bytes([0x21,0x03])*64
        self.data=b'original synthetic executable header'+self.palette+self.packed
        source=self.install/'executables/N2O.EXE';source.parent.mkdir(parents=True);source.write_bytes(self.data)
        config=self.root/'configs';config.mkdir()
        sha=lambda data:hashlib.sha256(data).hexdigest()
        self.recipe=dict(schema=1,source='N2O.EXE',format='ps1-clut16-icon-4bpp',width=16,height=16,
                         palette_offset=len(self.data)-160,pixels_offset=len(self.data)-128,
                         palette_sha256=sha(self.palette),pixels_sha256=sha(self.packed))
        (config/'game_icon_usa.json').write_text(json.dumps(self.recipe))
        (config/'disc_usa.json').write_text(json.dumps(dict(executables=[dict(path='N2O.EXE',size=len(self.data),sha256=sha(self.data))])))

    def tearDown(self):self.temp.cleanup()

    def test_palette_order_opacity_and_pixel_nibbles(self):
        pixels=decode_icon(self.palette,self.packed)
        self.assertEqual(pixels[:16],bytes([255,0,0,255,0,255,0,255,0,0,255,255,0,0,0,0]))
        self.assertEqual(len(pixels),1024)
        for palette,packed in [(self.palette[:-1],self.packed),(self.palette,self.packed[:-1])]:
            with self.assertRaises(ValueError):decode_icon(palette,packed)

    def test_generated_png_and_ico_follow_their_file_formats(self):
        pixels=decode_icon(self.palette,self.packed);png=png_bytes(pixels)
        self.assertEqual(png[:8],b'\x89PNG\r\n\x1a\n');pos=8;chunks={}
        while pos<len(png):
            size=struct.unpack_from('>I',png,pos)[0];kind=png[pos+4:pos+8];data=png[pos+8:pos+8+size]
            self.assertEqual(zlib.crc32(kind+data)&0xffffffff,struct.unpack_from('>I',png,pos+8+size)[0])
            chunks[kind]=data;pos+=12+size
        self.assertEqual(struct.unpack('>2I5B',chunks[b'IHDR']),(256,256,8,6,0,0,0))
        rows=zlib.decompress(chunks[b'IDAT']);self.assertEqual(len(rows),256*(1+256*4))
        self.assertEqual(rows[0],0);self.assertEqual(rows[1:65],bytes([255,0,0,255])*16)
        ico=ico_bytes(pixels);self.assertEqual(struct.unpack_from('<3H',ico),(0,1,6))
        end=102
        for index,size in enumerate((16,32,48,64,128,256)):
            width,height,_,_,planes,bpp,length,offset=struct.unpack_from('<4B2H2I',ico,6+16*index)
            self.assertEqual((width or 256,height or 256,planes,bpp),(size,size,1,32))
            self.assertEqual(offset,end);end=offset+length
            self.assertEqual(struct.unpack_from('<IiiHH',ico,offset),(40,size,size*2,1,32))
            # First stored row is the bottom row; source repeats the same pattern.
            self.assertEqual(ico[offset+40:offset+44],bytes([0,0,255,255]))
        self.assertEqual(end,len(ico))

    def test_verified_private_preparation_is_repeatable_and_preserves_source(self):
        with patch('prepare_icon.ROOT',self.root):icon=prepare_icon(self.install,self.output)
        receipt=json.loads((self.output/'icon.json').read_text())
        self.assertFalse(receipt['public_distribution_allowed'])
        before={p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in self.output.iterdir()}
        with patch('prepare_icon.ROOT',self.root):self.assertEqual(prepare_icon(self.install,self.output),icon)
        self.assertEqual(before,{p.name:(p.read_bytes(),p.stat().st_mtime_ns) for p in self.output.iterdir()})
        self.assertEqual((self.install/'executables/N2O.EXE').read_bytes(),self.data)

    def test_changed_source_or_recipe_never_publishes_an_icon(self):
        source=self.install/'executables/N2O.EXE';source.write_bytes(self.data[:-1]+b'!')
        with patch('prepare_icon.ROOT',self.root),self.assertRaisesRegex(ValueError,'verified USA'):
            prepare_icon(self.install,self.output)
        source.write_bytes(self.data)
        for key,value in [('pixels_offset',len(self.data)),('palette_offset',-1),('pixels_sha256','0'*64)]:
            recipe=dict(self.recipe);recipe[key]=value
            (self.root/'configs/game_icon_usa.json').write_text(json.dumps(recipe))
            with patch('prepare_icon.ROOT',self.root),self.assertRaises(ValueError):prepare_icon(self.install,self.output)
        self.assertFalse(self.output.exists())
        with self.assertRaisesRegex(ValueError,'private .local'):
            write_icons(decode_icon(self.palette,self.packed),self.root/'public assets')

    @unittest.skipUnless(shutil.which('cmake'),'CMake required for game icon integration')
    def test_project_passes_the_private_icon_to_the_framework(self):
        icon=write_icons(decode_icon(self.palette,self.packed),self.output)
        framework=self.root/'framework';(framework/'runtime').mkdir(parents=True)
        generated=self.root/'generated';generated.mkdir()
        (generated/'SLUS_006.37_dispatch.c').write_text('/* Original fixture. */\n')
        (framework/'dummy.c').write_text('int main(void) { return 0; }\n')
        # The pinned high-level helper does not recognize APP_ICON itself.
        # It forwards unknown arguments, but a preceding GEN_FULL_GLOB list
        # consumes them. Model both parser layers instead of bypassing it.
        (framework/'runtime/runtime.cmake').write_text('''function(psxrecomp_add_game_runtime target)
  cmake_parse_arguments(TITLE "ENABLE_NETPLAY_IF_PRESENT;ENABLE_SETUP_WIZARD;PGXP"
    "GEN_MARKER;GEN_FULL_FALLBACK;VERSION_FILE;CODEGEN_SETUP_INCLUDE_DIR;NETPLAY_LOBBY_URL;PRELOADED_MODS_DIR"
    "GEN_FULL_GLOB;CODEGEN_SETUP_SOURCES;EXCLUDE_BUILTIN_MODS" ${ARGN})
  psxrecomp_add_runtime_target(${target} ${TITLE_UNPARSED_ARGUMENTS})
endfunction()
function(psxrecomp_add_runtime_target target)
  cmake_parse_arguments(FIXTURE "" "APP_ICON" "" ${ARGN})
  if(NOT FIXTURE_APP_ICON STREQUAL NITROGEN_GAME_ICON)
    message(FATAL_ERROR "Private icon was not passed to the framework")
  endif()
  file(WRITE "${CMAKE_BINARY_DIR}/received-icon.txt" "${FIXTURE_APP_ICON}")
  add_executable(${target} "${PSXRECOMP_ROOT}/dummy.c")
endfunction()
''')
        build=self.root/'build';command=['cmake','-S',str(ROOT),'-B',str(build),
            '-DPSXRECOMP_ROOT='+str(framework),'-DNITROGEN_GENERATED_DIR='+str(generated),
            '-DNITROGEN_GAME_ICON='+str(icon)]
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(Path((build/'received-icon.txt').read_text()).resolve(),icon.resolve())
        icon.with_suffix('.png').unlink()
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0);self.assertIn('Private game icon is incomplete',result.stdout+result.stderr)


if __name__=='__main__':unittest.main()
