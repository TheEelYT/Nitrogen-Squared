"""Original Tk launcher shell: N2 artwork, persistent pages and shared progress."""
from __future__ import annotations
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
from launcher_presentation import KEYBOARD, read_options, read_launcher_preferences, save_option

BG="#060f20"; SIDE="#0c192d"; CARD="#101e34"; BORDER="#263a54"
TEXT="#edf3ff"; MUTED="#a4b4ce"; DIM="#7186a5"
FONT = 'Segoe UI' if os.name == 'nt' else 'Helvetica'
ACCENTS={"Cyan":"#7de8df","Violet":"#baa7ff","Amber":"#ffc276"}


def rounded(canvas,x,y,w,h,r=16,**kw):
    return canvas.create_polygon(x+r,y,x+w-r,y,x+w,y,x+w,y+r,x+w,y+h-r,x+w,y+h,
                                 x+w-r,y+h,x+r,y+h,x,y+h,x,y+h-r,x,y+r,x,y,
                                 smooth=True,splinesteps=24,**kw)


def icon(canvas,kind,x,y,color=TEXT,size=18):
    s=size/20
    def line(*p):canvas.create_line(*(v*s+(x if i%2==0 else y) for i,v in enumerate(p)),fill=color,width=1.5)
    if kind=="home":line(2,9,10,2,18,9,18,18,12,18,12,12,8,12,8,18,2,18,2,9)
    elif kind=="news":
        canvas.create_rectangle(x+3*s,y+2*s,x+17*s,y+18*s,outline=color,width=1.4)
        for yy in (7,11,15):line(6,yy,14,yy)
    elif kind=="settings":
        canvas.create_oval(x+5*s,y+5*s,x+15*s,y+15*s,outline=color,width=1.5)
        for dx,dy in ((10,0),(10,20),(0,10),(20,10)):
            line(dx,dy,10+(dx-10)*.7,10+(dy-10)*.7)
    elif kind=="play":canvas.create_polygon(x+4*s,y+2*s,x+17*s,y+10*s,x+4*s,y+18*s,fill=color,outline="")
    elif kind=="download":line(10,1,10,13,5,8);line(10,13,15,8);line(3,14,3,18,17,18,17,14)
    elif kind=="folder":line(1,6,1,17,19,17,19,5,10,5,7,2,1,2,1,6)
    elif kind=="stop":canvas.create_rectangle(x+4*s,y+4*s,x+16*s,y+16*s,outline=color,width=1.5)
    elif kind=="arrow":line(4,16,16,4,7,4);line(16,4,16,13)


class Button(tk.Canvas):
    def __init__(self,parent,text,command,*,accent="#7de8df",primary=False,kind=None,width=150,height=46,bg=BG):
        super().__init__(parent,width=width,height=height,bg=bg,highlightthickness=0,takefocus=1,cursor="hand2")
        self.text=text;self.command=command;self.accent=accent;self.primary=primary;self.kind=kind
        self.enabled=True;self.hover=False;self.selected=False
        self.bind('<Configure>',lambda e:self.draw())
        self.bind('<Enter>',lambda e:self.hovered(True));self.bind('<Leave>',lambda e:self.hovered(False))
        self.bind('<Button-1>',self.invoke);self.bind('<Return>',self.invoke);self.bind('<space>',self.invoke)
        self.bind('<FocusIn>',lambda e:self.draw());self.bind('<FocusOut>',lambda e:self.draw())
        self.draw()

    def hovered(self,value):self.hover=value;self.draw()

    def configure(self,cnf=None,**kw):
        if isinstance(cnf,dict):kw={**cnf,**kw}
        if 'text' in kw:self.text=kw.pop('text')
        if 'state' in kw:
            self.enabled=kw.pop('state')!='disabled'
            super().configure(takefocus=int(self.enabled),cursor='hand2' if self.enabled else '')
        if kw:super().configure(**kw)
        self.draw()

    config=configure

    def cget(self,key):
        if key=='state':return 'normal' if self.enabled else 'disabled'
        if key=='text':return self.text
        return super().cget(key)

    def invoke(self,event=None):
        if self.enabled:self.focus_set();self.command()
        return 'break'

    def draw(self):
        if not self.winfo_exists():return
        self.delete('all');w=max(self.winfo_width(),int(super().cget('width')));h=int(super().cget('height'))
        fill=self.accent if self.primary and self.enabled else '#1a3048' if self.hover or self.selected else CARD
        edge=self.accent if self.focus_get()==self or self.selected else BORDER
        rounded(self,1,1,w-2,h-2,r=h//2 if self.primary else 11,fill=fill,outline=edge,width=1)
        fg='#072526' if self.primary and self.enabled else TEXT if self.enabled else DIM
        center=w/2
        if self.kind:icon(self,self.kind,17,h/2-9,fg);center+=8
        self.create_text(center,h/2,text=self.text,fill=fg,font=(FONT,11,'bold'))


class Progress(tk.Canvas):
    def __init__(self,parent,accent,*,small=False,bg=BG):
        super().__init__(parent,height=62 if not small else 75,bg=bg,highlightthickness=0)
        self.accent=accent;self.small=small;self.title='Ready to play';self.detail='';self.percent=None;self.busy=False;self.phase=0
        self.reserved=0
        self.bind('<Configure>',lambda e:self.draw());self.timer=self.after(100,self.tick)

    def tick(self):
        if not self.winfo_exists():return
        if self.busy and self.percent is None:self.phase=(self.phase+7)%140;self.draw()
        self.timer=self.after(70,self.tick)

    def destroy(self):
        self.after_cancel(self.timer);super().destroy()

    def set(self,title,detail='',percent=None,busy=False):
        self.title=title;self.detail=detail;self.percent=percent;self.busy=busy;self.draw()

    def draw(self):
        self.delete('all');w=max(100,self.winfo_width());h=75 if self.small else 62
        rounded(self,1,1,w-2,h-2,r=14,fill=CARD,outline=BORDER)
        title=self.title
        if self.small:
            font=tkfont.Font(family=FONT,size=9,weight='bold')
            limit=w-32-(42 if self.percent is not None else 0)
            while title and font.measure(title)>limit:title=title[:-2]+'…' if not title.endswith('…') else title[:-2]+'…'
        self.create_text(15,20,anchor='w',text=title,fill=TEXT,font=(FONT,9 if self.small else 10,'bold'),width=0 if self.small else w-65-self.reserved)
        if self.percent is not None:self.create_text(w-15-self.reserved,20,anchor='e',text=f'{self.percent}%',fill=MUTED,font=(FONT,10,'bold'))
        if self.small:
            self.create_text(15,40,anchor='w',text='Current stage' if self.busy else 'All files stay local',fill=DIM,font=(FONT,8))
        elif self.detail:self.create_text(15,43,anchor='w',text=self.detail,fill=MUTED,font=(FONT,9),width=w-32-self.reserved)
        y=h-11 if self.small else h-7
        self.create_line(16,y,w-16,y,fill=BORDER,width=3,capstyle='round')
        if self.percent is not None:
            if self.percent:self.create_line(16,y,16+(w-32)*self.percent/100,y,fill=self.accent,width=3,capstyle='round')
        elif self.busy:
            left=max(0,(self.phase-35)/100);right=min(1,self.phase/100)
            if left<right:self.create_line(16+(w-32)*left,y,16+(w-32)*right,y,fill=self.accent,width=3,capstyle='round')


class NewsCard(tk.Canvas):
    def __init__(self,parent,item,command,accent):
        super().__init__(parent,height=90,bg=BG,highlightthickness=0,cursor='hand2',takefocus=1)
        self.item=item;self.command=command;self.accent=accent;self.hover=False
        self.bind('<Configure>',lambda e:self.draw());self.bind('<Enter>',lambda e:self.hovered(True));self.bind('<Leave>',lambda e:self.hovered(False))
        self.bind('<Button-1>',lambda e:self.command());self.bind('<Return>',lambda e:self.command())
        self.bind('<FocusIn>',lambda e:self.draw());self.bind('<FocusOut>',lambda e:self.draw())

    def hovered(self,v):self.hover=v;self.draw()

    def draw(self):
        self.delete('all');w=max(100,self.winfo_width())
        rounded(self,1,1,w-2,88,r=16,fill='#192b43' if self.hover else CARD,outline=self.accent if self.focus_get()==self else BORDER)
        label=self.item.get('version') or self.item.get('title','')
        self.create_text(16,22,anchor='w',text=label,fill=TEXT,font=(FONT,11,'bold'))
        date='This build' if self.item.get('current') else self.item.get('date','')
        self.create_text(w-14,22,anchor='e',text=date,fill=DIM,font=(FONT,8))
        self.create_text(16,52,anchor='w',text=self.item.get('summary',''),fill=MUTED,font=(FONT,9),width=w-32)


class LauncherView:
    def __init__(self,app):
        self.app=app;self.root=app.window
        self.accent=ACCENTS[read_launcher_preferences(app.layout.local)['accent']]
        self.page='Home';self.tab='Display';self.controls=[];self.option_widgets=[];self.nav={};self.release_buttons=[]
        self.root.configure(bg=BG)
        self.root.option_add('*Font',(FONT,10))
        self.style=ttk.Style(self.root);self.style.theme_use('clam')
        self.style.configure('N.TCombobox',font=(FONT,10),fieldbackground=CARD,background='#24364f',foreground=TEXT,arrowcolor=MUTED,bordercolor=BORDER,padding=8)
        self.style.map('N.TCombobox',fieldbackground=[('readonly',CARD),('disabled',SIDE)],foreground=[('readonly',TEXT),('disabled',DIM)])
        self.style.configure('N.Vertical.TScrollbar',background='#29405b',troughcolor=BG,bordercolor=BG,arrowcolor=MUTED,width=9)
        self.style.configure('N.Horizontal.TScale',background=CARD,troughcolor='#2b3a56',sliderlength=17)
        self.root.option_add('*TCombobox*Listbox.background',CARD);self.root.option_add('*TCombobox*Listbox.foreground',TEXT)
        self.root.option_add('*TCombobox*Listbox.selectBackground','#28495b')
        self.shell=tk.Frame(self.root,bg=BG);self.shell.pack(fill='both',expand=True,padx=14,pady=14)
        self.shell.grid_columnconfigure(1,weight=1);self.shell.grid_rowconfigure(0,weight=1)
        self.side=tk.Canvas(self.shell,width=210,bg=BG,highlightthickness=0);self.side.grid(row=0,column=0,sticky='ns',padx=(0,12))
        self.side.bind('<Configure>',self.draw_sidebar)
        assets=app.layout.app/'launcher/assets'
        self.art=tk.PhotoImage(file=str(assets/'tunnel.png'),format='png');self.art_half=self.art.subsample(2)
        self.logo=tk.PhotoImage(file=str(assets/'logo.png'),format='png');self.hero_logo=self.logo.subsample(4);self.mark=self.logo.subsample(24)
        if self.art.width()!=1536 or self.art.height()!=1024:raise RuntimeError('Launcher artwork did not decode correctly')
        self.root.iconphoto(True,self.mark)
        for i,(name,kind) in enumerate((('Home','home'),("What's New",'news'),('Settings','settings'))):
            b=Button(self.side,name,lambda n=name:self.show_page(n),accent=self.accent,kind=kind,width=182,height=44,bg=SIDE)
            b.place(x=14,y=104+i*52);self.nav[name]=b
        self.sidebar_progress=Progress(self.side,self.accent,small=True,bg=SIDE)
        self.content=tk.Frame(self.shell,bg=BG);self.content.grid(row=0,column=1,sticky='nsew')
        self.content.grid_columnconfigure(0,weight=1);self.content.grid_rowconfigure(0,weight=1)
        self.pages={name:tk.Frame(self.content,bg=BG) for name in self.nav}
        for frame in self.pages.values():frame.grid(row=0,column=0,sticky='nsew');frame.grid_propagate(False)
        self.build_home();self.build_news();self.build_settings()
        self.status_trace=app.status.trace_add('write',lambda *args:self.refresh_status())
        self.detail_trace=app.detail.trace_add('write',lambda *args:self.refresh_status())
        self.show_page('Home');self.refresh_status();self.set_busy(app.busy)

    def destroy(self):
        self.app.status.trace_remove('write',self.status_trace);self.app.detail.trace_remove('write',self.detail_trace)
        for event,func in self.mouse_bindings:self.root.unbind(event,func)
        self.shell.destroy()

    def draw_sidebar(self,event=None):
        c=self.side;c.delete('all');w=c.winfo_width();h=c.winfo_height()
        rounded(c,1,1,w-2,h-2,r=22,fill=SIDE,outline=BORDER)
        if hasattr(self,'mark'):c.create_image(21,32,anchor='w',image=self.mark)
        c.create_text(83,37,anchor='w',text='Nitrogen\nSquared',fill=TEXT,font=(FONT,11,'bold'))
        c.create_text(18,h-152,anchor='w',text='N₂  /  NEON',fill=self.accent,font=(FONT,9,'bold'))
        c.create_text(18,h-27,anchor='w',text='v'+self.app.layout.version,fill=MUTED,font=(FONT,9))
        c.create_text(w-18,h-27,anchor='e',text=self.app.layout.display_name,fill=DIM,font=(FONT,8))
        if hasattr(self,'sidebar_progress'):self.sidebar_progress.place(x=13,y=h-132,width=w-26,height=75)

    def show_page(self,name):
        self.page=name;self.pages[name].tkraise()
        for n,b in self.nav.items():b.selected=n==name;b.draw()
        if name=='Settings':self.reload_options()

    def build_home(self):
        self.home=tk.Canvas(self.pages['Home'],bg=BG,highlightthickness=0);self.home.pack(fill='both',expand=True)
        self.home.bind('<Configure>',self.draw_home)
        a=self.app
        a.play_button=Button(self.home,'Play' if a.layout.state().get('disc') else 'Set up game',a.play,primary=True,accent=self.accent,kind='play',width=165,height=50)
        a.update_button=Button(self.home,'Restore version' if a.recovery else 'Check updates',a.restore if a.recovery else a.check_update,accent=self.accent,kind='download',width=158,height=50)
        a.disc_button=Button(self.home,'Choose disc',lambda:a.choose(play=False),accent=self.accent,kind='folder',width=145,height=50)
        a.stop_button=Button(self.home,'Stop setup',a.stop,accent=self.accent,kind='stop',width=120,height=38)
        self.home_progress=Progress(self.home,self.accent)
        self.cards=[];self.rebuild_cards()

    def rebuild_cards(self):
        for c in self.cards:c.destroy()
        self.cards=[]
        items=self.app.releases[:3]
        for item in items:
            c=NewsCard(self.home,item,lambda i=item:self.show_release(i),self.accent);self.cards.append(c)
        if len(items)<3:
            for item,tab in [(dict(title='Your game. Your saves.',summary='Everything stays in your installation folder.'),'Storage'),
                             (dict(title='Make it yours',summary='Display, audio and your familiar controls.'),'Display')][:3-len(items)]:
                self.cards.append(NewsCard(self.home,item,lambda t=tab:self.open_settings(t),self.accent))
        self.draw_home()

    def draw_home(self,event=None):
        c=self.home;c.delete('all');w=max(600,c.winfo_width());h=max(560,c.winfo_height())
        art=self.art if w>1200 or h>850 else self.art_half
        c.create_image(w,0,image=art,anchor='ne')
        c.create_text(28,31,anchor='w',text='N₂O  /  NATIVE RECOMPILATION',fill=self.accent,font=(FONT,9,'bold'))
        c.create_image(28,h-478,anchor='nw',image=self.hero_logo)
        c.create_text(30,h-289,anchor='w',text='Return to the tunnel.',fill=TEXT,font=(FONT,16,'bold'))
        for b,x,width in [(self.app.play_button,28,165),(self.app.update_button,205,158),(self.app.disc_button,375,145)]:
            c.create_window(x,h-261,window=b,width=width,height=50,anchor='nw')
        stoppable=self.app.busy and self.app.status.get()!='Game running'
        c.create_window(28,h-194,window=self.home_progress,width=w-56-(132 if stoppable else 0),height=62,anchor='nw')
        if stoppable:
            c.create_window(w-148,h-182,window=self.app.stop_button,width=120,height=38,anchor='nw')
        c.create_text(30,h-111,anchor='w',text="WHAT'S NEW",fill=DIM,font=(FONT,8,'bold'))
        n=max(1,len(self.cards));width=(w-56-(n-1)*12)/n
        for i,card in enumerate(self.cards):c.create_window(28+i*(width+12),h-95,window=card,width=width,height=90,anchor='nw')

    def build_news(self):
        page=self.pages["What's New"]
        tk.Label(page,text="What's New",bg=BG,fg=TEXT,font=(FONT,25,'bold')).pack(anchor='w',padx=28,pady=(22,18))
        body=tk.Frame(page,bg=BG);body.pack(fill='both',expand=True,padx=22,pady=(0,10))
        rail=tk.Frame(body,bg=SIDE,width=190);rail.pack(side='left',fill='y',padx=(0,18));rail.pack_propagate(False)
        self.news_scroller=tk.Canvas(rail,bg=SIDE,highlightthickness=0,width=175)
        self.news_scroller.pack(side='left',fill='both',expand=True)
        rail_scroll=ttk.Scrollbar(rail,command=self.news_scroller.yview,style='N.Vertical.TScrollbar');rail_scroll.pack(side='right',fill='y')
        self.news_scroller.configure(yscrollcommand=rail_scroll.set)
        self.news_list=tk.Frame(self.news_scroller,bg=SIDE)
        item=self.news_scroller.create_window(0,0,window=self.news_list,anchor='nw')
        self.news_scroller.bind('<Configure>',lambda e:self.news_scroller.itemconfigure(item,width=e.width))
        self.news_list.bind('<Configure>',lambda e:self.news_scroller.configure(scrollregion=self.news_scroller.bbox('all')))
        right=tk.Frame(body,bg=BG);right.pack(side='left',fill='both',expand=True)
        self.news_title=tk.Label(right,text='',bg=BG,fg=TEXT,font=(FONT,21,'bold'),anchor='w',justify='left',wraplength=550)
        self.news_title.pack(fill='x',pady=(10,4))
        self.news_title.bind('<Configure>',lambda e:self.news_title.configure(wraplength=max(200,e.width-8)))
        self.news_date=tk.Label(right,text='',bg=BG,fg=MUTED,font=(FONT,10),anchor='w');self.news_date.pack(fill='x',pady=(0,12))
        self.news_body=tk.Text(right,bg=BG,fg=TEXT,font=(FONT,11),wrap='word',relief='flat',bd=0,highlightthickness=0,padx=0,pady=8,spacing1=4,spacing3=7,insertbackground=TEXT)
        scrollbar=ttk.Scrollbar(right,command=self.news_body.yview,style='N.Vertical.TScrollbar');scrollbar.pack(side='right',fill='y')
        self.news_body.configure(yscrollcommand=scrollbar.set);self.news_body.pack(fill='both',expand=True)
        self.rebuild_news()

    def rebuild_news(self):
        for b in self.release_buttons:b.destroy()
        self.release_buttons=[]
        for item in self.app.releases:
            text='v'+item['version']+('  ·  current' if item.get('current') else '')
            b=Button(self.news_list,text,lambda r=item:self.show_release(r),accent=self.accent,width=165,height=48,bg=SIDE)
            b.version=item['version'];b.pack(fill='x',padx=5,pady=4);self.release_buttons.append(b)
        if self.app.releases:self.select_release(self.app.releases[0])

    def select_release(self,item):
        for b in self.release_buttons:b.selected=b.version==item['version'];b.draw()
        self.news_title.configure(text=item['title'])
        self.news_date.configure(text=('Included in this build  ·  ' if item.get('current') else '')+item['date'])
        self.news_body.configure(state='normal');self.news_body.delete('1.0','end')
        # Display remote notes as plain text, never executable HTML or markup.
        self.news_body.insert('1.0',item['body']);self.news_body.configure(state='disabled');self.news_body.yview_moveto(0)

    def show_release(self,item):self.select_release(item);self.show_page("What's New")

    def build_settings(self):
        page=self.pages['Settings']
        tk.Label(page,text='Settings',bg=BG,fg=TEXT,font=(FONT,25,'bold')).pack(anchor='w',padx=28,pady=(22,18))
        tabs=tk.Frame(page,bg=BG);tabs.pack(fill='x',padx=28)
        self.tab_buttons={}
        for name in ('Display','Audio','Controls','Storage','About'):
            b=Button(tabs,name,lambda t=name:self.open_settings(t),accent=self.accent,width=98,height=38)
            b.pack(side='left',padx=(0,6));self.tab_buttons[name]=b
        self.scroller=tk.Canvas(page,bg=BG,highlightthickness=0)
        self.scroller.pack(side='left',fill='both',expand=True,padx=(28,8),pady=(20,12))
        scroll=ttk.Scrollbar(page,command=self.scroller.yview,style='N.Vertical.TScrollbar');scroll.pack(side='right',fill='y',pady=20)
        self.scroller.configure(yscrollcommand=scroll.set)
        self.settings_body=tk.Frame(self.scroller,bg=BG)
        self.settings_window=self.scroller.create_window(0,0,window=self.settings_body,anchor='nw')
        self.scroller.bind('<Configure>',lambda e:self.scroller.itemconfigure(self.settings_window,width=e.width))
        self.settings_body.bind('<Configure>',lambda e:self.scroller.configure(scrollregion=self.scroller.bbox('all')))
        self.mouse_bindings=[(event,self.root.bind(event,self.scroll_settings)) for event in ('<MouseWheel>','<Button-4>','<Button-5>')]
        self.settings_tabs={}
        for name in self.tab_buttons:
            frame=tk.Frame(self.settings_body,bg=BG);self.settings_tabs[name]=frame
        self.vars={k:tk.StringVar() for k in ('video_mode','hud_scale','render_percent','master_volume')}
        self.build_display();self.build_audio();self.build_controls();self.build_storage();self.build_about()
        self.open_settings('Display',show=False)

    def scroll_settings(self,event):
        if self.page=="What's New" and self.root.winfo_pointerx()<self.news_scroller.winfo_rootx()+self.news_scroller.winfo_width():
            amount=(-1 if event.num==4 else 1) if getattr(event,'num',None) in (4,5) else (-1 if event.delta>0 else 1)
            self.news_scroller.yview_scroll(amount*3,'units');return
        if self.page=='Settings':
            amount=(-1 if event.num==4 else 1) if getattr(event,'num',None) in (4,5) else (-int(event.delta/120) if abs(event.delta)>=120 else (-1 if event.delta>0 else 1))
            self.scroller.yview_scroll(amount*3,'units')

    def section(self,parent,title):
        tk.Label(parent,text=title.upper(),bg=BG,fg=DIM,font=(FONT,9,'bold')).pack(anchor='w',pady=(5,10))
        box=tk.Frame(parent,bg=CARD,highlightthickness=1,highlightbackground=BORDER)
        box.pack(fill='x',pady=(0,20));return box

    def row(self,parent,title,description=None):
        frame=tk.Frame(parent,bg=CARD);frame.pack(fill='x',padx=18,pady=13)
        left=tk.Frame(frame,bg=CARD);left.pack(side='left',fill='x',expand=True)
        tk.Label(left,text=title,bg=CARD,fg=TEXT,font=(FONT,11,'bold'),anchor='w').pack(fill='x')
        if description:tk.Label(left,text=description,bg=CARD,fg=MUTED,font=(FONT,9),anchor='w',wraplength=330,justify='left').pack(fill='x',pady=(5,0))
        return frame

    def combo(self,row,key,labels):
        combo=ttk.Combobox(row,textvariable=self.vars[key],values=list(labels),state='readonly',style='N.TCombobox',width=16)
        combo.pack(side='right',padx=(12,0));combo.bind('<<ComboboxSelected>>',lambda e:self.commit_option(key,labels[self.vars[key].get()]))
        self.option_widgets.append((combo,'readonly'));return combo

    def slider(self,row,key,minimum,maximum,step):
        right=tk.Frame(row,bg=CARD);right.pack(side='right',padx=(12,0))
        tk.Label(right,textvariable=self.vars[key],bg=CARD,fg=self.accent,font=(FONT,11,'bold'),width=6,anchor='e').pack(side='right')
        variable=tk.DoubleVar(value=100);self.vars[key+'_slider']=variable
        slider=ttk.Scale(right,variable=variable,from_=minimum,to=maximum,length=180,style='N.Horizontal.TScale')
        slider.pack(side='right')
        def show(*args):self.vars[key].set(str(int(round(variable.get()/step)*step))+'%')
        variable.trace_add('write',show)
        def commit(e):self.commit_option(key,int(round(variable.get()/step)*step))
        slider.bind('<ButtonRelease-1>',commit);slider.bind('<KeyRelease>',commit)
        self.option_widgets.append((slider,'normal'))

    def build_display(self):
        parent=self.settings_tabs['Display'];box=self.section(parent,'Picture')
        self.combo(self.row(box,'Window mode'),'video_mode',{'Windowed':0,'Borderless':1,'Fullscreen':2})
        self.combo(self.row(box,'HUD scale','Auto follows the window, with a 2× minimum.'),'hud_scale',{'Auto':0,'2×':2,'3×':3,'4×':4,'6×':6})
        box=self.section(parent,'Rendering')
        self.slider(self.row(box,'Scene resolution','Scale the 3D scene; keep menus and text sharp.'),'render_percent',25,200,5)
        self.note(parent,'Changes apply when you next start the game. While playing, use the in-game Video menu.')

    def build_audio(self):
        parent=self.settings_tabs['Audio'];box=self.section(parent,'Volume')
        self.slider(self.row(box,'Master volume','Set the overall game volume.'),'master_volume',0,100,1)
        self.note(parent,'Music, ambient sound and effects have separate controls in the game’s Audio menu. Changes here apply on the next launch.')

    def build_controls(self):
        parent=self.settings_tabs['Controls'];box=self.section(parent,'Keyboard')
        for action,key in KEYBOARD:
            row=self.row(box,action);tk.Label(row,text=key,bg=CARD,fg=self.accent,font=(FONT,10,'bold'),anchor='e').pack(side='right')
        b=Button(parent,'Open keyboard bindings',lambda:self.app.open_runtime_file('keybinds.ini'),accent=self.accent,width=215)
        b.pack(anchor='w',pady=(0,16));self.controls.append(b)
        self.note(parent,'Custom bindings are preserved. Launch the game once to create its bindings file. Gamepads are detected automatically; the in-game Controls menu selects the controller configuration.')

    def build_storage(self):
        parent=self.settings_tabs['Storage'];box=self.section(parent,'Your game')
        self.disc_path=tk.StringVar(value=self.app.layout.state().get('disc') or 'No disc selected')
        row=self.row(box,'Source disc');tk.Label(row.winfo_children()[0],textvariable=self.disc_path,bg=CARD,fg=MUTED,font=(FONT,9),wraplength=480,justify='left',anchor='w').pack(fill='x',pady=(8,0))
        for label,command in [('Choose disc…',lambda:self.app.choose(play=False)),('Open saves',lambda:self.app.open_folder('saves')),('Open setup log',lambda:self.app.open_local_file('setup.log'))]:
            b=Button(box,label,command,accent=self.accent,width=205,bg=CARD);b.pack(anchor='w',padx=18,pady=(0,12));self.controls.append(b)
        box=self.section(parent,'Asset folders')
        self.note(box,'Extract original assets and music for your own use. The game continues to read your original disc.')
        self.app.assets_button=Button(box,'Open asset folders' if (self.app.layout.local/'game').is_dir() else 'Extract asset folders',self.app.assets,accent=self.accent,kind='folder',width=225,bg=CARD)
        self.app.assets_button.pack(anchor='w',padx=18,pady=(0,16))

    def build_about(self):
        parent=self.settings_tabs['About'];box=self.section(parent,'Nitrogen Squared')
        self.row(box,'Version '+self.app.layout.version,self.app.layout.display_name+' · N2O: Nitrous Oxide recompilation')
        row=self.row(box,'Accent colour')
        accent=tk.StringVar(value=read_launcher_preferences(self.app.layout.local)['accent'])
        combo=ttk.Combobox(row,textvariable=accent,values=list(ACCENTS),state='readonly',style='N.TCombobox',width=14)
        combo.pack(side='right');combo.bind('<<ComboboxSelected>>',lambda e:self.app.change_accent(accent.get()));self.option_widgets.append((combo,'readonly'))
        for text,url in [('Project on GitHub','https://github.com/TheEelYT/Nitrogen-Squared'),('Published releases','https://github.com/TheEelYT/Nitrogen-Squared/releases')]:
            b=Button(box,text,lambda u=url:self.app.open_url(u),accent=self.accent,width=220,bg=CARD);b.pack(anchor='w',padx=18,pady=(0,12));self.controls.append(b)
        self.note(parent,'Bring your own supported USA CUE/BIN. Game files, saves and compiled code stay in your installation folder. No commercial game data is included with this launcher.')

    def note(self,parent,text):
        tk.Label(parent,text=text,bg=parent.cget('bg'),fg=MUTED,font=(FONT,10),justify='left',wraplength=650,anchor='w').pack(fill='x',padx=16,pady=(12,18))

    def open_settings(self,name,show=True):
        self.tab=name
        for n,frame in self.settings_tabs.items():
            if n==name:frame.pack(fill='x',expand=True)
            else:frame.pack_forget()
        for n,b in self.tab_buttons.items():b.selected=n==name;b.draw()
        self.scroller.yview_moveto(0)
        if show:self.show_page('Settings')

    def reload_options(self):
        options=read_options(self.app.layout.local)
        self.vars['video_mode'].set(('Windowed','Borderless','Fullscreen')[options['video_mode']])
        self.vars['hud_scale'].set('Auto' if not options['hud_scale'] else str(options['hud_scale'])+'×')
        for name in ('render_percent','master_volume'):self.vars[name+'_slider'].set(options[name])
        self.disc_path.set(self.app.layout.state().get('disc') or 'No disc selected')

    def commit_option(self,key,value):
        if self.app.busy or self.app.recovery:return
        try:
            save_option(self.app.layout.local,key,value)
            self.app.status.set('Settings saved');self.app.detail.set('Your changes will apply on the next game launch.')
        except (OSError,ValueError) as e:self.app.show_error(str(e))

    def set_busy(self,busy):
        blocked=busy or self.app.recovery
        for b in [self.app.play_button,self.app.disc_button,self.app.update_button,*self.controls]:b.configure(state='disabled' if blocked else 'normal')
        if self.app.recovery and not busy:self.app.update_button.configure(state='normal')
        self.app.assets_button.configure(state='normal' if not blocked and (self.app.layout.installation/'installation.json').is_file() else 'disabled')
        self.app.stop_button.configure(state='normal' if busy and self.app.status.get()!='Game running' else 'disabled')
        for widget,normal in self.option_widgets:widget.configure(state='disabled' if blocked else normal)
        self.draw_home();self.refresh_status()

    def refresh_status(self):
        if not hasattr(self,'home_progress'):return
        self.draw_home()
        title=self.app.status.get();detail=self.app.detail.get();percent=getattr(self.app,'stage_percent',None)
        self.home_progress.reserved=0
        self.home_progress.set(title,detail,percent,self.app.busy)
        self.sidebar_progress.set(title,detail,percent,self.app.busy)
        self.app.play_button.configure(text='Setting up...' if self.app.busy and title!='Game running' else 'Playing' if title=='Game running' else 'Play' if self.app.layout.state().get('disc') else 'Set up game')

    def update_releases(self):self.rebuild_cards();self.rebuild_news()

    def smoke(self):
        original=self.root.geometry()
        previous=self.app.status.get(),self.app.detail.get(),self.app.stage_percent
        for size in ('960x620','1180x720'):
            self.root.geometry(size);self.root.update()
            for name in self.pages:
                self.show_page(name);self.root.update()
                if not self.pages[name].winfo_ismapped():raise RuntimeError('Launcher navigation did not map '+name)
            for name in self.settings_tabs:self.open_settings(name);self.root.update()
            if self.scroller.winfo_width()<400:raise RuntimeError('Launcher settings clipped')
        self.app.busy=True;self.set_busy(True)
        if self.app.play_button.cget('state')!='disabled':raise RuntimeError('Busy launcher actions are not disabled')
        self.app.stage_percent=42;self.app.status.set('Compiling');self.app.detail.set('Current compilation stage · 42%')
        self.root.update();self.app.busy=False;self.app.stage_percent=None;self.set_busy(False)
        self.app.status.set(previous[0]);self.app.detail.set(previous[1]);self.app.stage_percent=previous[2]
        self.root.geometry(original);self.show_page('Home');self.root.update()
        return dict(navigation=list(self.pages),settings=list(self.settings_tabs),progress=True,layout=True,artwork=True)
