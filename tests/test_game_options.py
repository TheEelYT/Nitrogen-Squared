"""Original persistence tests: settings survive runtime rebuild locations."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('c++'), 'C++ compiler required')
class GameOptionsTests(unittest.TestCase):
    def test_load_migration_validation_and_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)
            (p/'fixture.cpp').write_text(r'''
#include "game_options.h"
#include <cassert>
#include <cstdlib>
int main(int argc,char**argv){
 nitrogen_options_init(argv[1]);
 assert(nitrogen_options_desktop());
 assert(nitrogen_option_get(NITROGEN_MASTER_VOLUME)==std::atoi(argv[2]));
 if(argc==4){
  assert(nitrogen_option_get(NITROGEN_HUD_SCALE)==0);
  assert(nitrogen_option_get(NITROGEN_RENDER_PERCENT)==100);
  assert(!nitrogen_option_set(NITROGEN_HUD_SCALE,1));
  assert(!nitrogen_option_set(NITROGEN_RENDER_PERCENT,73));
  assert(!nitrogen_option_set(NITROGEN_MASTER_VOLUME,101));
  assert(nitrogen_option_set(NITROGEN_HUD_SCALE,4));
  assert(nitrogen_option_set(NITROGEN_VIDEO_MODE,NITROGEN_FULLSCREEN));
  assert(nitrogen_option_set(NITROGEN_RENDER_PERCENT,75));
  assert(nitrogen_option_set(NITROGEN_MASTER_VOLUME,37));
 }else{
  assert(nitrogen_option_get(NITROGEN_HUD_SCALE)==4);
  assert(nitrogen_option_get(NITROGEN_VIDEO_MODE)==NITROGEN_FULLSCREEN);
  assert(nitrogen_option_get(NITROGEN_RENDER_PERCENT)==75);
 }
}
''')
            subprocess.run(['c++','-std=c++17','-I',str(ROOT/'compat'),str(p/'fixture.cpp'),
                            str(ROOT/'compat/game_options.cpp'),'-o',str(p/'fixture')],check=True)
            config = p/'nitrogen-options.ini'
            base = p/'build-a'
            base.mkdir()
            (base/'nitrogen-menu.ini').write_text('visible 1\nvolume 61\n')
            env = dict(os.environ, NITROGEN_OPTIONS_FILE=str(config))
            subprocess.run([str(p/'fixture'),str(base)+'/', '61','write'],env=env,check=True)
            # A rebuilt runtime has another executable directory. The portable
            # settings path, unlike its old F1 settings, still owns the values.
            other = p/'build-b'; other.mkdir()
            with config.open('a') as f:
                f.write('hud_scale 1\nrender_percent 999\nmaster_volume text\nvideo_mode 0 junk\n')
            subprocess.run([str(p/'fixture'),str(other)+'/', '37'],env=env,check=True)
