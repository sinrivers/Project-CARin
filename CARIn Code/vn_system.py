"""
Filename:vn_system.py
Author(s): Ricardo Ochoa, Taliesin Reese
Version: 2.0
Date: 11/12/2025
Purpose: User cutscenes for Project CARIn
"""
# vn_system.py
import pygame
import storage
import sharedlib

# Simple word-wrap helper
def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if font.size(test)[0] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

class vnoverlay(sharedlib.gameobject):
    def __init__(self, script):
        super().__init__()
        # VN panel geometry (bottom 35% of screen)
        W, H = storage.screensize
        self.pad = 16
        self.chars = []
        self.box = pygame.Rect(self.pad, int(H*0.65), W - self.pad*2, int(H*0.30))
        self.name_height = 28

        # Script & state
        self.script = script                  # list of {"speaker": str, "text": str}
        self.idx = 0                          # which line we are on
        self.done = False

        # Typewriter
        self.speed = 1                        # chars per frame (tweak)
        self.char_index = 0                   # how many chars revealed
        self.full_line = ""                   # full text of current line (unwrapped)
        self.wrapped = []                     # wrapped lines for drawing

        # Surfaces/colors
        self.bg_color = (10, 10, 10)
        self.bg_alpha = 210
        self.border_color = (220, 220, 220)
        self.text_color = (240, 240, 240)
        self.name_color = (200, 200, 255)

        # name “plate”
        self.name_rect = pygame.Rect(self.box.x + 12, self.box.y - self.name_height//2, 180, self.name_height)

        # font from storage
        self.font = storage.userwriter
        self.line_gap = 6

        # prepare first line
        self._load_line()

        # make this draw on UI layer, above game
        self.z = 10_000
        self.vertsort = 10_000

        # identify as UI so your saver can skip it
        self.persist = False
        self.is_ui = True

    # Called when this overlay should be removed
    def close(self):
        self.done = True
        if self in storage.objlist:
            storage.objlist.remove(self)
        sharedlib.cutscene_active = False

    def _load_line(self):
        if self.idx >= len(self.script):
            self.close()
            return
        entry = self.script[self.idx]
        if isinstance(entry,dict):
                self.speaker = entry.get("speaker", "")
                self.full_line = entry.get("text", "")
                self.char_index = 0
                # Pre-wrap target width inside box, leaving padding
                max_text_width = self.box.w - self.pad*2
                self.wrapped_full = wrap_text(self.full_line, self.font, max_text_width)
                self.wrapped = [""]  # will reveal progressively
        elif isinstance(entry,list):
                for index in range(len(self.chars)):
                    item = self.chars[index]
                    if item[0] == entry[0]:
                        self.chars[index] = [entry[0],entry[1],entry[2],item[3],entry[3]]
                        self.idx += 1
                        self._load_line()
                        return
                self.chars.append([entry[0],entry[1],entry[2],[0,0],entry[3]])
                self.idx += 1
                self._load_line()
        elif isinstance(entry,str):
            sharedlib.loadgame(entry)

    def _advance_or_finish(self):
        # If not fully typed, finish instantly
        total_len = len(self.full_line)
        if self.char_index < total_len:
            self.char_index = total_len
            self._rebuild_visible_lines()
            return
        # else go to next line
        self.idx += 1
        self._load_line()

    def _rebuild_visible_lines(self):
        # Reveal substring and re-wrap
        snippet = self.full_line[:self.char_index]
        max_text_width = self.box.w - self.pad*2
        self.wrapped = wrap_text(snippet, self.font, max_text_width)

    def update(self):
        # Consume input: left click (1) or ENTER/SPACE
        if 1 in storage.newclicks or pygame.K_RETURN in storage.newkeys or pygame.K_SPACE in storage.newkeys:
            self._advance_or_finish()
        #NOTE: character movement display
        for char in self.chars:
                if char[3] != char[4]:
                    char[3][0] += int((char[4][0] - char[3][0])/8)
                    char[3][1] += int((char[4][1] - char[3][1])/8)
        # Typewriter tick
        if self.char_index < len(self.full_line):
            self.char_index += self.speed
            if self.char_index > len(self.full_line):
                self.char_index = len(self.full_line)
            self._rebuild_visible_lines()

    def render(self):
        surf = storage.uicanvas
	#NOTE: Rendering Character portraits.
        for char in self.chars:
                name = char[0]+char[1]
                scale = storage.animinfo["Portraits"][name]
                if char[2] == 1:
                    surf.blit(pygame.transform.flip(storage.spritesheet,char[2],0),char[3],[storage.spritesheet.get_width()-scale[0]-scale[2]]+scale[1:])
                else:
                    surf.blit(storage.spritesheet,char[3],scale)
                    
        # Panel (semi-transparent)
        panel = pygame.Surface((self.box.w, self.box.h), pygame.SRCALPHA)
        panel.fill((*self.bg_color, self.bg_alpha))
        surf.blit(panel, self.box.topleft)
        pygame.draw.rect(surf, self.border_color, self.box, 2)

        # Name plate
        if self.speaker:
            # simple plate background
            name_bg = pygame.Surface((self.name_rect.w, self.name_rect.h), pygame.SRCALPHA)
            name_bg.fill((0, 0, 0, 200))
            surf.blit(name_bg, self.name_rect.topleft)
            pygame.draw.rect(surf, self.border_color, self.name_rect, 2)

            name_surf = self.font.render(self.speaker, True, self.name_color)
            surf.blit(name_surf, (self.name_rect.x + 10, self.name_rect.y + (self.name_rect.h - name_surf.get_height())//2))

        # Text lines
        x = self.box.x + self.pad
        y = self.box.y + self.pad
        for line in self.wrapped:
            if not line:
                continue
            ts = self.font.render(line, True, self.text_color)
            surf.blit(ts, (x, y))
            y += ts.get_height() + self.line_gap

# ---- Public API: attach to sharedlib (like you did with loadmenu) ----

def start_cutscene(script):
    """script can be a list of dicts or a string key into storage.cutscenes."""
    storage.objlist = []
    if isinstance(script, str):
        data = storage.cutscenes.get(script, [])
    else:
        data = script
    if not data:
        print(f"[WARN] VN script '{script}' not found or empty")
        return
    sharedlib.cutscene_active = True
    overlay = vnoverlay(data)

# one-liner for other code to call
sharedlib.start_cutscene = start_cutscene
