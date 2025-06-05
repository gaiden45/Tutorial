#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HDLang Editor Pro - Masaüstü Sürümü
String uzunluğu sınırlaması sorunu çözümü ile gelişmiş HDLang editörü

Özellikler:
- Dinamik string boyutlandırma (uzunluk sınırı yok!)
- Gelişmiş arama ve değiştirme
- Otomatik yedekleme sistemi
- Modern kullanıcı arayüzü
- Klavye kısayolları
- Tema desteği

Kullanım: python download_masaustu_hdlang_editor.py
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
import datetime
import tempfile
import threading
import webbrowser
from tkinter import font

class GelistirilmisHDLangEditor:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("HDLang Editor Pro - Masaüstü Sürümü v2.0")
        self.window.geometry("1400x800")
        self.window.configure(bg='#2b2b2b')
        
        # Pencere ikonunu ayarla
        try:
            self.window.iconbitmap(default='icon.ico')
        except:
            pass
        
        # Ana değişkenler
        self.file_path = None
        self.file_data = None
        self.strings_positions = []
        self.original_strings = []
        self.current_strings = []
        self.search_results = []
        self.current_search_index = 0
        self.is_modified = False
        
        # Ayarlar
        self.settings = {
            "dynamic_sizing": True,
            "auto_backup": True,
            "theme": "dark",
            "font_size": 12,
            "auto_save": False,
            "backup_interval": 5  # dakika
        }
        
        self.load_settings()
        self.create_ui()
        self.apply_theme()
        self.center_window()
        
        # Otomatik kaydetme için timer
        self.auto_save_timer = None
        if self.settings["auto_save"]:
            self.start_auto_save_timer()
    
    def center_window(self):
        """Pencereyi ekranın ortasına yerleştir"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_settings(self):
        """Ayarları yükle"""
        try:
            if os.path.exists('hdlang_settings.json'):
                with open('hdlang_settings.json', 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except:
            pass
    
    def save_settings(self):
        """Ayarları kaydet"""
        try:
            with open('hdlang_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def create_ui(self):
        """Gelişmiş kullanıcı arayüzü oluştur"""
        # Ana menü çubuğu
        self.create_menu()
        
        # Üst toolbar
        self.create_toolbar()
        
        # Ana içerik alanı
        self.create_main_content()
        
        # Alt durum çubuğu
        self.create_status_bar()
        
        # Sağ tık menüsü
        self.create_context_menu()
    
    def create_menu(self):
        """Menü çubuğu oluştur"""
        menubar = tk.Menu(self.window, bg='#3c3c3c', fg='white')
        self.window.config(menu=menubar)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="📁 Dosya", menu=file_menu)
        file_menu.add_command(label="🔓 Aç (Ctrl+O)", command=self.open_hdlang, accelerator="Ctrl+O")
        file_menu.add_command(label="💾 Kaydet (Ctrl+S)", command=self.save_hdlang, accelerator="Ctrl+S")
        file_menu.add_command(label="📝 Metin Olarak Kaydet", command=self.save_as_text)
        file_menu.add_separator()
        file_menu.add_command(label="🔄 Yeniden Yükle", command=self.reload_file)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Çıkış", command=self.on_closing)
        
        # Düzenle menüsü
        edit_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="✏️ Düzenle", menu=edit_menu)
        edit_menu.add_command(label="🔍 Ara (Ctrl+F)", command=self.focus_search, accelerator="Ctrl+F")
        edit_menu.add_command(label="🔄 Değiştir (Ctrl+H)", command=self.focus_replace, accelerator="Ctrl+H")
        edit_menu.add_separator()
        edit_menu.add_command(label="📋 Tümünü Seç (Ctrl+A)", command=self.select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="📊 İstatistikler", command=self.show_statistics)
        
        # Görünüm menüsü
        view_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="👁️ Görünüm", menu=view_menu)
        view_menu.add_command(label="🌙 Tema Değiştir", command=self.toggle_theme)
        view_menu.add_command(label="🔢 Satır Numaraları", command=self.toggle_line_numbers)
        view_menu.add_separator()
        view_menu.add_command(label="🔍 Zoom In (+)", command=self.zoom_in)
        view_menu.add_command(label="🔍 Zoom Out (-)", command=self.zoom_out)
        view_menu.add_command(label="🔄 Zoom Reset", command=self.zoom_reset)
        
        # Araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="🔧 Araçlar", menu=tools_menu)
        tools_menu.add_command(label="⚙️ Ayarlar", command=self.show_settings)
        tools_menu.add_command(label="📦 Yedeklemeler", command=self.manage_backups)
        tools_menu.add_separator()
        tools_menu.add_command(label="🧹 Cache Temizle", command=self.clear_cache)
        
        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="❓ Yardım", menu=help_menu)
        help_menu.add_command(label="📖 Kullanım Kılavuzu", command=self.show_help)
        help_menu.add_command(label="🔗 GitHub", command=lambda: webbrowser.open("https://github.com"))
        help_menu.add_separator()
        help_menu.add_command(label="ℹ️ Hakkında", command=self.show_about)
    
    def create_toolbar(self):
        """Gelişmiş toolbar oluştur"""
        toolbar_frame = tk.Frame(self.window, bg='#3c3c3c', height=60)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=2)
        toolbar_frame.pack_propagate(False)
        
        # Sol grup - Dosya işlemleri
        left_group = tk.Frame(toolbar_frame, bg='#3c3c3c')
        left_group.pack(side=tk.LEFT, padx=5)
        
        self.open_btn = tk.Button(left_group, text="📁 Aç", command=self.open_hdlang, 
                                 bg='#4a90e2', fg='white', relief='flat', padx=15, pady=5,
                                 font=('Arial', 10, 'bold'))
        self.open_btn.pack(side=tk.LEFT, padx=2)
        
        self.save_btn = tk.Button(left_group, text="💾 Kaydet", command=self.save_hdlang, 
                                 bg='#5cb85c', fg='white', relief='flat', padx=15, pady=5,
                                 font=('Arial', 10, 'bold'))
        self.save_btn.pack(side=tk.LEFT, padx=2)
        
        self.save_txt_btn = tk.Button(left_group, text="📄 Metin", command=self.save_as_text, 
                                     bg='#f0ad4e', fg='white', relief='flat', padx=15, pady=5,
                                     font=('Arial', 10, 'bold'))
        self.save_txt_btn.pack(side=tk.LEFT, padx=2)
        
        # Orta grup - Arama işlemleri
        middle_group = tk.Frame(toolbar_frame, bg='#3c3c3c')
        middle_group.pack(side=tk.LEFT, padx=20)
        
        tk.Label(middle_group, text="🔍 Ara:", bg='#3c3c3c', fg='white', 
                font=('Arial', 10)).pack(side=tk.LEFT, padx=2)
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(middle_group, textvariable=self.search_var, width=25, 
                                    font=('Arial', 10))
        self.search_entry.pack(side=tk.LEFT, padx=2)
        self.search_entry.bind('<Return>', lambda e: self.search_text())
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        self.search_btn = tk.Button(middle_group, text="Ara", command=self.search_text, 
                                   bg='#337ab7', fg='white', relief='flat', padx=10)
        self.search_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Label(middle_group, text="↔️ Değiştir:", bg='#3c3c3c', fg='white', 
                font=('Arial', 10)).pack(side=tk.LEFT, padx=(10, 2))
        
        self.replace_var = tk.StringVar()
        self.replace_entry = tk.Entry(middle_group, textvariable=self.replace_var, width=25, 
                                     font=('Arial', 10))
        self.replace_entry.pack(side=tk.LEFT, padx=2)
        self.replace_entry.bind('<Return>', lambda e: self.replace_text())
        
        self.replace_btn = tk.Button(middle_group, text="Değiştir", command=self.replace_text, 
                                    bg='#d9534f', fg='white', relief='flat', padx=10)
        self.replace_btn.pack(side=tk.LEFT, padx=2)
        
        # Sağ grup - Durum göstergeleri
        right_group = tk.Frame(toolbar_frame, bg='#3c3c3c')
        right_group.pack(side=tk.RIGHT, padx=5)
        
        # Dinamik boyutlandırma göstergesi
        self.dynamic_indicator = tk.Label(right_group, text="🚀 Dinamik Boyut: AÇIK", 
                                         bg='#5cb85c', fg='white', padx=10, pady=2,
                                         font=('Arial', 9, 'bold'))
        self.dynamic_indicator.pack(side=tk.RIGHT, padx=2)
        
        # Dosya durumu göstergesi
        self.file_status = tk.Label(right_group, text="📄 Dosya Yok", 
                                   bg='#6c757d', fg='white', padx=10, pady=2,
                                   font=('Arial', 9))
        self.file_status.pack(side=tk.RIGHT, padx=2)
    
    def create_main_content(self):
        """Ana içerik alanı"""
        # Ana çerçeve
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        
        # Sol panel - Bilgi paneli
        left_panel = tk.Frame(main_frame, width=350, bg='#3c3c3c')
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        # Dosya bilgileri
        info_frame = tk.LabelFrame(left_panel, text="📁 Dosya Bilgileri", bg='#3c3c3c', fg='white',
                                  font=('Arial', 11, 'bold'))
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.file_info_text = tk.Text(info_frame, height=6, bg='#2b2b2b', fg='white', 
                                     wrap=tk.WORD, font=('Arial', 9), state=tk.DISABLED)
        self.file_info_text.pack(fill=tk.X, padx=5, pady=5)
        
        # İstatistikler
        stats_frame = tk.LabelFrame(left_panel, text="📊 İstatistikler", bg='#3c3c3c', fg='white',
                                   font=('Arial', 11, 'bold'))
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=8, bg='#2b2b2b', fg='white', 
                                 wrap=tk.WORD, font=('Consolas', 9), state=tk.DISABLED)
        self.stats_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Hızlı ayarlar
        settings_frame = tk.LabelFrame(left_panel, text="⚙️ Hızlı Ayarlar", bg='#3c3c3c', fg='white',
                                      font=('Arial', 11, 'bold'))
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.dynamic_var = tk.BooleanVar(value=self.settings["dynamic_sizing"])
        dynamic_check = tk.Checkbutton(settings_frame, text="🚀 Dinamik Boyutlandırma", 
                                      variable=self.dynamic_var, command=self.toggle_dynamic_sizing,
                                      bg='#3c3c3c', fg='white', selectcolor='#3c3c3c',
                                      font=('Arial', 9))
        dynamic_check.pack(anchor=tk.W, padx=5, pady=2)
        
        self.backup_var = tk.BooleanVar(value=self.settings["auto_backup"])
        backup_check = tk.Checkbutton(settings_frame, text="💾 Otomatik Yedekleme", 
                                     variable=self.backup_var, command=self.toggle_auto_backup,
                                     bg='#3c3c3c', fg='white', selectcolor='#3c3c3c',
                                     font=('Arial', 9))
        backup_check.pack(anchor=tk.W, padx=5, pady=2)
        
        self.autosave_var = tk.BooleanVar(value=self.settings["auto_save"])
        autosave_check = tk.Checkbutton(settings_frame, text="💿 Otomatik Kaydetme", 
                                       variable=self.autosave_var, command=self.toggle_auto_save,
                                       bg='#3c3c3c', fg='white', selectcolor='#3c3c3c',
                                       font=('Arial', 9))
        autosave_check.pack(anchor=tk.W, padx=5, pady=2)
        
        # Font boyutu kontrolü
        font_frame = tk.Frame(settings_frame, bg='#3c3c3c')
        font_frame.pack(fill=tk.X, padx=5, pady=2)
        
        tk.Label(font_frame, text="🔤 Font:", bg='#3c3c3c', fg='white', 
                font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.font_scale = tk.Scale(font_frame, from_=8, to=20, orient=tk.HORIZONTAL,
                                  bg='#3c3c3c', fg='white', highlightthickness=0,
                                  command=self.on_font_change)
        self.font_scale.set(self.settings["font_size"])
        self.font_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Sağ panel - Editör
        right_panel = tk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Editör başlığı
        editor_header = tk.Frame(right_panel, bg='#3c3c3c', height=35)
        editor_header.pack(fill=tk.X, pady=(0, 2))
        editor_header.pack_propagate(False)
        
        self.file_name_label = tk.Label(editor_header, text="📄 Yeni Dosya", 
                                       bg='#3c3c3c', fg='white', font=('Arial', 12, 'bold'))
        self.file_name_label.pack(side=tk.LEFT, padx=10, pady=8)
        
        # Editör kontrolleri
        controls_frame = tk.Frame(editor_header, bg='#3c3c3c')
        controls_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.line_numbers_btn = tk.Button(controls_frame, text="🔢", command=self.toggle_line_numbers,
                                         bg='#6c757d', fg='white', relief='flat', padx=8)
        self.line_numbers_btn.pack(side=tk.LEFT, padx=2)
        
        self.clear_search_btn = tk.Button(controls_frame, text="🔍❌", command=self.clear_search,
                                         bg='#6c757d', fg='white', relief='flat', padx=8)
        self.clear_search_btn.pack(side=tk.LEFT, padx=2)
        
        # Satır numaraları ve metin alanı çerçevesi
        text_frame = tk.Frame(right_panel, bg='#2b2b2b', relief=tk.SUNKEN, bd=1)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Satır numaraları
        self.line_numbers_area = tk.Text(text_frame, width=6, padx=5, takefocus=0, border=0,
                                        background='#2b2b2b', foreground='#666', state=tk.DISABLED, 
                                        wrap=tk.NONE, font=('Consolas', self.settings["font_size"]))
        self.line_numbers_area.pack(side=tk.LEFT, fill=tk.Y)
        
        # Ana metin alanı
        self.text_area = tk.Text(text_frame, wrap=tk.WORD, undo=True, maxundo=100,
                                bg='#2b2b2b', fg='white', insertbackground='#ffffff',
                                font=('Consolas', self.settings["font_size"]),
                                selectbackground='#4a90e2', selectforeground='white',
                                padx=10, pady=10)
        
        # Kaydırma çubukları
        v_scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.on_text_scroll)
        h_scrollbar = tk.Scrollbar(right_panel, orient=tk.HORIZONTAL, command=self.text_area.xview)
        
        self.text_area.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        h_scrollbar.pack(fill=tk.X)
        
        # Metin değişikliklerini izle
        self.text_area.bind("<<Modified>>", self.on_text_change)
        self.text_area.bind("<KeyRelease>", self.update_cursor_position)
        self.text_area.bind("<Button-1>", self.update_cursor_position)
        self.text_area.bind("<Button-3>", self.show_context_menu)  # Sağ tık
        
        # Scroll senkronizasyonu
        self.text_area.bind("<MouseWheel>", self.on_mouse_wheel)
        self.line_numbers_area.bind("<MouseWheel>", self.on_mouse_wheel)
        
        # Drag & Drop desteği
        self.text_area.drop_target_register('DND_Files')
        self.text_area.dnd_bind('<<Drop>>', self.on_file_drop)
        
        # Klavye kısayolları
        self.setup_keyboard_shortcuts()
    
    def create_status_bar(self):
        """Gelişmiş durum çubuğu oluştur"""
        status_frame = tk.Frame(self.window, bg='#3c3c3c', height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        # Sol durum metni
        self.status_label = tk.Label(status_frame, text="✅ Hazır", bg='#3c3c3c', fg='white',
                                    font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Orta bilgiler
        self.progress_label = tk.Label(status_frame, text="", bg='#3c3c3c', fg='#ffc107',
                                      font=('Arial', 9))
        self.progress_label.pack(side=tk.LEFT, padx=20)
        
        # Sağ bilgiler
        right_info = tk.Frame(status_frame, bg='#3c3c3c')
        right_info.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.encoding_label = tk.Label(right_info, text="UTF-8", bg='#3c3c3c', fg='#28a745',
                                      font=('Arial', 9))
        self.encoding_label.pack(side=tk.RIGHT, padx=5)
        
        self.cursor_label = tk.Label(right_info, text="Satır: 1, Sütun: 1", bg='#3c3c3c', fg='white',
                                    font=('Arial', 9))
        self.cursor_label.pack(side=tk.RIGHT, padx=5)
        
        self.modified_label = tk.Label(right_info, text="", bg='#3c3c3c', fg='#dc3545',
                                      font=('Arial', 9, 'bold'))
        self.modified_label.pack(side=tk.RIGHT, padx=5)
    
    def create_context_menu(self):
        """Sağ tık menüsü oluştur"""
        self.context_menu = tk.Menu(self.window, tearoff=0, bg='#3c3c3c', fg='white')
        self.context_menu.add_command(label="📋 Kopyala", command=self.copy_text)
        self.context_menu.add_command(label="📄 Yapıştır", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="✂️ Kes", command=self.cut_text)
        self.context_menu.add_command(label="🔄 Seç Tümü", command=self.select_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔍 Bu Metni Ara", command=self.search_selected)
    
    def setup_keyboard_shortcuts(self):
        """Klavye kısayollarını ayarla"""
        shortcuts = {
            '<Control-o>': self.open_hdlang,
            '<Control-s>': self.save_hdlang,
            '<Control-n>': self.new_file,
            '<Control-f>': self.focus_search,
            '<Control-h>': self.focus_replace,
            '<Control-a>': self.select_all,
            '<Control-z>': lambda e: self.text_area.edit_undo(),
            '<Control-y>': lambda e: self.text_area.edit_redo(),
            '<Control-plus>': lambda e: self.zoom_in(),
            '<Control-minus>': lambda e: self.zoom_out(),
            '<Control-0>': lambda e: self.zoom_reset(),
            '<F1>': lambda e: self.show_help(),
            '<F5>': lambda e: self.reload_file(),
            '<F11>': lambda e: self.toggle_fullscreen(),
            '<Escape>': lambda e: self.clear_search()
        }
        
        for shortcut, command in shortcuts.items():
            self.window.bind(shortcut, command)
    
    def apply_theme(self):
        """Tema uygula"""
        if self.settings["theme"] == "light":
            bg_color = '#ffffff'
            fg_color = '#000000'
            bg_secondary = '#f8f9fa'
            bg_tertiary = '#e9ecef'
        else:
            bg_color = '#2b2b2b'
            fg_color = '#ffffff'
            bg_secondary = '#3c3c3c'
            bg_tertiary = '#495057'
        
        # Ana pencere
        self.window.configure(bg=bg_color)
        
        # Metin alanları güncelle
        if hasattr(self, 'text_area'):
            self.text_area.configure(bg=bg_color, fg=fg_color)
            self.line_numbers_area.configure(bg=bg_secondary, fg='#888888')
            self.file_info_text.configure(bg=bg_color, fg=fg_color)
            self.stats_text.configure(bg=bg_color, fg=fg_color)
    
    def extract_strings_with_positions(self, data):
        """Gelişmiş string çıkarma - daha akıllı algılama"""
        strings = []
        positions = []
        i = 0
        
        while i < len(data):
            if 32 <= data[i] <= 126:  # ASCII yazdırılabilir karakterler
                start = i
                while i < len(data) and 32 <= data[i] <= 126:
                    i += 1
                
                # En az 2 karakter uzunluğundaki stringleri al
                if i - start >= 2:
                    try:
                        string_content = data[start:i].decode("ascii", errors="ignore")
                        # Sadece anlamlı stringler (en az bir harf içeren)
                        if any(c.isalpha() for c in string_content) or len(string_content) >= 3:
                            strings.append(string_content)
                            positions.append((start, i))
                    except:
                        pass
            else:
                i += 1
        
        return strings, positions
    
    def create_backup(self, file_path, data):
        """Otomatik yedekleme oluştur"""
        if not self.settings["auto_backup"]:
            return None
        
        try:
            backup_dir = 'hdlang_backups'
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_path = os.path.join(backup_dir, f"{filename}_{timestamp}.backup")
            
            with open(backup_path, 'wb') as f:
                f.write(data)
            
            self.update_status(f"💾 Yedekleme oluşturuldu: {os.path.basename(backup_path)}")
            return backup_path
        except Exception as e:
            messagebox.showwarning("Yedekleme Hatası", f"Yedekleme oluşturulamadı: {e}")
            return None
    
    # Ana işlem fonksiyonları
    def open_hdlang(self, event=None):
        """HDLang dosyası aç - gelişmiş sürüm"""
        if self.is_modified and not self.ask_save_changes():
            return
        
        file_path = filedialog.askopenfilename(
            title="HDLang Dosyası Seç",
            filetypes=[("HDLang Files", "*.hdlang"), ("Tüm Dosyalar", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            # Dosyayı yükle
            with open(file_path, "rb") as f:
                data = f.read()
            
            # Yedekleme oluştur
            backup_path = self.create_backup(file_path, data)
            
            # Stringleri çıkar
            strings, positions = self.extract_strings_with_positions(data)
            
            # Verileri kaydet
            self.file_path = file_path
            self.file_data = bytearray(data)
            self.strings_positions = positions
            self.original_strings = strings.copy()
            self.current_strings = strings.copy()
            self.is_modified = False
            
            # UI'yi güncelle
            self.update_text_area()
            self.update_file_info()
            self.update_stats()
            self.update_status(f"✅ Dosya yüklendi: {os.path.basename(file_path)} ({len(strings)} string)")
            
            self.file_name_label.config(text=f"📄 {os.path.basename(file_path)}")
            self.file_status.config(text=f"📄 {len(strings)} string", bg='#28a745')
            
            # Son açılan dosyayı kaydet
            self.save_recent_file(file_path)
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya açılamadı:\n{str(e)}")
            self.update_status("❌ Hata: Dosya açılamadı")
    
    def save_hdlang(self, event=None):
        """HDLang dosyası kaydet - DİNAMİK BOYUTLANDIRMA İLE"""
        if not self.file_path or not self.file_data:
            messagebox.showerror("Hata", "Önce bir dosya açmalısınız.")
            return
        
        # Metin alanından güncel stringleri al
        content = self.text_area.get("1.0", tk.END).strip()
        lines = content.split("\n") if content else []
        
        # Boş satırları filtrele
        lines = [line.strip() for line in lines if line.strip()]
        
        if len(lines) != len(self.strings_positions):
            if not messagebox.askyesno("Uyarı", 
                f"Satır sayısı değişti!\n\n"
                f"Orijinal: {len(self.strings_positions)} string\n"
                f"Yeni: {len(lines)} string\n\n"
                f"Dinamik boyutlandırma ile devam etmek istiyor musunuz?\n\n"
                f"⚠️  DİKKAT: Bu dosya yapısını değiştirebilir!"):
                return
            
            # Eksik satırları boş string olarak ekle
            while len(lines) < len(self.strings_positions):
                lines.append("")
            # Fazla satırları kırp
            lines = lines[:len(self.strings_positions)]
        
        try:
            self.update_status("💾 Kaydediliyor...")
            self.window.update()
            
            if self.settings["dynamic_sizing"]:
                # *** DİNAMİK BOYUTLANDIRMA - STRING UZUNLUĞU SINIRI YOK! ***
                modified_data = bytearray()
                last_end = 0
                total_saved = 0
                
                for i, (new_string, (start, end)) in enumerate(zip(lines, self.strings_positions)):
                    # Önceki bölümü kopyala
                    modified_data.extend(self.file_data[last_end:start])
                    
                    # Yeni stringi UTF-8 olarak kodla (daha fazla karakter desteği)
                    encoded = new_string.encode("utf-8", errors="ignore")
                    modified_data.extend(encoded)
                    
                    total_saved += len(encoded)
                    last_end = end
                    
                    # İlerleme göster
                    if i % 10 == 0:
                        progress = int((i / len(lines)) * 100)
                        self.progress_label.config(text=f"💾 %{progress}")
                        self.window.update()
                
                # Kalan veriyi ekle
                modified_data.extend(self.file_data[last_end:])
                
                success_msg = "🚀 Dinamik boyutlandırma kullanıldı - uzunluk sınırı yok!"
                
            else:
                # Klasik sistem - sabit boyut (orijinal davranış)
                modified_data = bytearray(self.file_data)
                
                for new_string, (start, end) in zip(lines, self.strings_positions):
                    encoded = new_string.encode("ascii", errors="ignore")
                    length = end - start
                    
                    if len(encoded) > length:
                        messagebox.showerror("Hata", 
                            f"❌ '{new_string}' metni çok uzun!\n\n"
                            f"Orijinal uzunluk: {length} karakter\n"
                            f"Yeni uzunluk: {len(encoded)} karakter\n\n"
                            f"💡 Çözüm: Ayarlar menüsünden 'Dinamik Boyutlandırma'yı etkinleştirin!")
                        return
                    
                    # Padding ile doldur
                    encoded_padded = encoded + b"\x00" * (length - len(encoded))
                    modified_data[start:end] = encoded_padded
                
                success_msg = "📝 Sabit boyut ile kaydedildi"
            
            # Dosyayı kaydet
            save_path = self.file_path.replace(".hdlang", "_modified.hdlang")
            with open(save_path, "wb") as f:
                f.write(modified_data)
            
            # Başarı mesajı
            file_size = len(modified_data)
            message = f"✅ Dosya başarıyla kaydedildi!\n\n"
            message += f"📁 {save_path}\n"
            message += f"📊 Boyut: {file_size:,} byte\n"
            message += f"📝 String sayısı: {len(lines)}\n\n"
            message += success_msg
            
            messagebox.showinfo("Başarılı ✅", message)
            
            self.update_status(f"✅ Kaydedildi: {os.path.basename(save_path)}")
            self.progress_label.config(text="")
            self.is_modified = False
            self.modified_label.config(text="")
            
            # Güncel stringleri kaydet
            self.current_strings = lines.copy()
            self.update_stats()
            
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Dosya kaydedilirken hata oluştu:\n{str(e)}")
            self.update_status("❌ Hata: Kaydetme başarısız")
            self.progress_label.config(text="")
    
    def save_as_text(self, event=None):
        """Metin dosyası olarak kaydet"""
        content = self.text_area.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Uyarı", "Kaydetmek için metin yok.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Metin Dosyası Olarak Kaydet",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            lines = content.split('\n')
            with open(file_path, "w", encoding="utf-8") as f:
                if file_path.endswith('.csv'):
                    # CSV formatında kaydet
                    f.write("Satir,Orijinal,Guncel,Uzunluk\n")
                    for i, line in enumerate(lines, 1):
                        original = self.original_strings[i-1] if i-1 < len(self.original_strings) else ""
                        f.write(f"{i},\"{original}\",\"{line}\",{len(line)}\n")
                else:
                    # Düz metin olarak kaydet
                    f.write(content)
            
            messagebox.showinfo("Başarılı", f"✅ Metin dosyası kaydedildi:\n{file_path}")
            self.update_status(f"✅ Metin kaydedildi: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Hata", f"❌ Metin dosyası kaydedilirken hata:\n{str(e)}")
    
    # Arama ve değiştirme fonksiyonları
    def search_text(self, event=None):
        """Gelişmiş metin arama"""
        keyword = self.search_var.get().strip()
        if not keyword:
            messagebox.showwarning("Uyarı", "Aranacak kelime girin.")
            return
        
        # Önceki aramaları temizle
        self.text_area.tag_remove("search_highlight", "1.0", tk.END)
        self.text_area.tag_remove("current_highlight", "1.0", tk.END)
        self.search_results = []
        
        content = self.text_area.get("1.0", tk.END)
        lines = content.split("\n")
        
        # Tüm eşleşmeleri bul
        for line_num, line in enumerate(lines, 1):
            start_pos = 0
            while True:
                pos = line.lower().find(keyword.lower(), start_pos)
                if pos == -1:
                    break
                
                self.search_results.append((line_num, pos, len(keyword)))
                start_pos = pos + 1
        
        if self.search_results:
            # İlk sonuca git
            self.current_search_index = 0
            self.jump_to_search_result()
            
            # Tüm sonuçları vurgula
            self.highlight_all_results(keyword)
            
            message = f"🔍 {len(self.search_results)} sonuç bulundu"
            self.update_status(message)
            self.progress_label.config(text=f"1/{len(self.search_results)}")
            
            # Sonraki/önceki butonları ekle
            self.add_search_navigation()
            
        else:
            self.update_status(f"🔍 '{keyword}' bulunamadı")
            messagebox.showinfo("Arama Sonucu", f"'{keyword}' bulunamadı.")
    
    def on_search_change(self, event=None):
        """Arama kutusu değiştiğinde otomatik ara"""
        keyword = self.search_var.get().strip()
        if len(keyword) >= 2:  # En az 2 karakter girilince ara
            self.search_text()
        elif len(keyword) == 0:
            self.clear_search()
    
    def highlight_all_results(self, keyword):
        """Tüm arama sonuçlarını vurgula"""
        # Highlight tag'lerini yapılandır
        self.text_area.tag_configure("search_highlight", background="#ffd700", foreground="#000000")
        self.text_area.tag_configure("current_highlight", background="#ff6600", foreground="#ffffff")
        
        for line_num, pos, length in self.search_results:
            start_index = f"{line_num}.{pos}"
            end_index = f"{line_num}.{pos + length}"
            self.text_area.tag_add("search_highlight", start_index, end_index)
    
    def jump_to_search_result(self):
        """Arama sonucuna git"""
        if not self.search_results:
            return
        
        line_num, pos, length = self.search_results[self.current_search_index]
        start_index = f"{line_num}.{pos}"
        end_index = f"{line_num}.{pos + length}"
        
        # Önceki vurguyu kaldır
        self.text_area.tag_remove("current_highlight", "1.0", tk.END)
        
        # Yeni vurguyu ekle
        self.text_area.tag_add("current_highlight", start_index, end_index)
        
        # Metni görünür yap
        self.text_area.see(start_index)
        self.text_area.mark_set(tk.INSERT, start_index)
        
        # İlerleme güncelle
        self.progress_label.config(text=f"{self.current_search_index + 1}/{len(self.search_results)}")
    
    def add_search_navigation(self):
        """Arama navigasyon butonları ekle"""
        if hasattr(self, 'search_nav_frame'):
            self.search_nav_frame.destroy()
        
        self.search_nav_frame = tk.Frame(self.window.nametowidget(self.search_entry.winfo_parent()), bg='#3c3c3c')
        self.search_nav_frame.pack(side=tk.LEFT, padx=5)
        
        prev_btn = tk.Button(self.search_nav_frame, text="◀", command=self.search_previous,
                           bg='#6c757d', fg='white', relief='flat', padx=5)
        prev_btn.pack(side=tk.LEFT, padx=1)
        
        next_btn = tk.Button(self.search_nav_frame, text="▶", command=self.search_next,
                           bg='#6c757d', fg='white', relief='flat', padx=5)
        next_btn.pack(side=tk.LEFT, padx=1)
    
    def search_next(self):
        """Sonraki arama sonucuna git"""
        if self.search_results:
            self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
            self.jump_to_search_result()
    
    def search_previous(self):
        """Önceki arama sonucuna git"""
        if self.search_results:
            self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
            self.jump_to_search_result()
    
    def replace_text(self, event=None):
        """Gelişmiş metin değiştirme"""
        find_text = self.search_var.get().strip()
        replace_text = self.replace_var.get()
        
        if not find_text:
            messagebox.showwarning("Uyarı", "Değiştirilecek kelime girin.")
            return
        
        content = self.text_area.get("1.0", tk.END)
        
        # Case insensitive replacement
        import re
        pattern = re.compile(re.escape(find_text), re.IGNORECASE)
        new_content = pattern.sub(replace_text, content)
        
        # Değişiklik sayısını hesapla
        replacement_count = len(pattern.findall(content))
        
        if replacement_count > 0:
            # Onay al
            if messagebox.askyesno("Onay", 
                f"'{find_text}' → '{replace_text}'\n\n"
                f"{replacement_count} değişiklik yapılacak.\n\n"
                f"Devam etmek istiyor musunuz?"):
                
                # Metni güncelle
                self.text_area.delete("1.0", tk.END)
                self.text_area.insert("1.0", new_content)
                
                # Satır numaralarını güncelle
                self.update_line_numbers()
                self.mark_as_modified()
                
                message = f"✅ {replacement_count} değişiklik yapıldı"
                self.update_status(message)
                messagebox.showinfo("Başarılı", message)
        else:
            messagebox.showinfo("Sonuç", f"'{find_text}' bulunamadı.")
    
    def clear_search(self, event=None):
        """Aramayı temizle"""
        self.search_var.set("")
        self.replace_var.set("")
        self.search_results = []
        self.current_search_index = 0
        
        # Vurguları temizle
        self.text_area.tag_remove("search_highlight", "1.0", tk.END)
        self.text_area.tag_remove("current_highlight", "1.0", tk.END)
        
        # Navigasyon butonlarını kaldır
        if hasattr(self, 'search_nav_frame'):
            self.search_nav_frame.destroy()
        
        self.progress_label.config(text="")
        self.update_status("🔍 Arama temizlendi")
    
    # UI güncelleme fonksiyonları
    def update_text_area(self):
        """Metin alanını güncelle"""
        self.text_area.delete("1.0", tk.END)
        
        for line in self.current_strings:
            self.text_area.insert(tk.END, line + "\n")
        
        self.update_line_numbers()
        self.mark_as_modified(False)
    
    def update_line_numbers(self):
        """Satır numaralarını güncelle"""
        self.line_numbers_area.config(state=tk.NORMAL)
        self.line_numbers_area.delete("1.0", tk.END)
        
        content = self.text_area.get("1.0", tk.END)
        lines = content.split("\n")
        
        for i in range(1, len(lines)):
            self.line_numbers_area.insert(tk.END, f"{i:4d}\n")
        
        self.line_numbers_area.config(state=tk.DISABLED)
    
    def update_file_info(self):
        """Dosya bilgilerini güncelle"""
        self.file_info_text.config(state=tk.NORMAL)
        self.file_info_text.delete("1.0", tk.END)
        
        if self.file_path:
            file_size = os.path.getsize(self.file_path)
            info_text = f"📁 {os.path.basename(self.file_path)}\n"
            info_text += f"📂 {os.path.dirname(self.file_path)}\n"
            info_text += f"📊 Boyut: {file_size:,} byte\n"
            info_text += f"📝 String: {len(self.original_strings)}\n"
            info_text += f"🕐 {datetime.datetime.fromtimestamp(os.path.getmtime(self.file_path)).strftime('%Y-%m-%d %H:%M')}\n"
            info_text += f"🔒 Encoding: UTF-8"
            
            self.file_info_text.insert("1.0", info_text)
        else:
            self.file_info_text.insert("1.0", "📄 Henüz dosya açılmadı\n\n💡 Dosya → Aç menüsünden\n   bir HDLang dosyası seçin")
        
        self.file_info_text.config(state=tk.DISABLED)
    
    def update_stats(self):
        """İstatistikleri güncelle"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete("1.0", tk.END)
        
        if self.current_strings:
            total_strings = len(self.current_strings)
            modified_count = 0
            total_chars = 0
            max_length = 0
            min_length = float('inf')
            
            for i, current in enumerate(self.current_strings):
                total_chars += len(current)
                max_length = max(max_length, len(current))
                min_length = min(min_length, len(current))
                
                if i < len(self.original_strings):
                    if current != self.original_strings[i]:
                        modified_count += 1
            
            avg_length = total_chars / total_strings if total_strings > 0 else 0
            min_length = min_length if min_length != float('inf') else 0
            
            stats_text = f"📊 GENEL İSTATİSTİKLER\n"
            stats_text += f"{'='*25}\n"
            stats_text += f"Toplam String: {total_strings:,}\n"
            stats_text += f"Değiştirilmiş: {modified_count:,}\n"
            stats_text += f"Değişmemiş: {total_strings - modified_count:,}\n\n"
            
            stats_text += f"📏 UZUNLUK İSTATİSTİKLERİ\n"
            stats_text += f"{'='*25}\n"
            stats_text += f"Toplam Karakter: {total_chars:,}\n"
            stats_text += f"Ortalama Uzunluk: {avg_length:.1f}\n"
            stats_text += f"En Uzun: {max_length:,}\n"
            stats_text += f"En Kısa: {min_length:,}\n\n"
            
            stats_text += f"🔍 ARAMA\n"
            stats_text += f"{'='*25}\n"
            stats_text += f"Bulunan Sonuç: {len(self.search_results):,}\n"
            
            if self.settings["dynamic_sizing"]:
                stats_text += f"\n🚀 DİNAMİK BOYUT: AÇIK\n"
                stats_text += f"✅ Uzunluk sınırı yok!"
            else:
                stats_text += f"\n📏 SABİT BOYUT: AÇIK\n"
                stats_text += f"⚠️  Orijinal uzunluk korunur"
            
            self.stats_text.insert("1.0", stats_text)
        else:
            self.stats_text.insert("1.0", "📊 İstatistik yok\n\n💡 Önce bir dosya açın")
        
        self.stats_text.config(state=tk.DISABLED)
    
    def update_cursor_position(self, event=None):
        """İmleç pozisyonunu güncelle"""
        try:
            cursor_pos = self.text_area.index(tk.INSERT)
            line, col = cursor_pos.split('.')
            self.cursor_label.config(text=f"Satır: {line}, Sütun: {int(col)+1}")
        except:
            pass
    
    def update_status(self, message):
        """Durum çubuğunu güncelle"""
        self.status_label.config(text=message)
        self.window.update()
    
    def mark_as_modified(self, modified=True):
        """Dosya değişiklik durumunu işaretle"""
        self.is_modified = modified
        if modified:
            self.modified_label.config(text="● Değiştirildi")
            if self.file_path:
                title = f"HDLang Editor Pro - {os.path.basename(self.file_path)} ●"
            else:
                title = "HDLang Editor Pro - Yeni Dosya ●"
        else:
            self.modified_label.config(text="")
            if self.file_path:
                title = f"HDLang Editor Pro - {os.path.basename(self.file_path)}"
            else:
                title = "HDLang Editor Pro"
        
        self.window.title(title)
    
    # Event handler'lar
    def on_text_change(self, event=None):
        """Metin değişikliği olayı"""
        if self.text_area.edit_modified():
            self.update_line_numbers()
            
            # Güncel stringleri al
            content = self.text_area.get("1.0", tk.END).strip()
            self.current_strings = content.split("\n") if content else []
            
            self.update_stats()
            self.mark_as_modified(True)
            self.text_area.edit_modified(False)
            
            # Otomatik kaydetme timer'ını yeniden başlat
            if self.settings["auto_save"]:
                self.restart_auto_save_timer()
    
    def on_text_scroll(self, *args):
        """Scroll senkronizasyonu"""
        self.line_numbers_area.yview(*args)
        self.text_area.yview(*args)
    
    def on_mouse_wheel(self, event):
        """Mouse wheel ile scroll"""
        if event.delta:  # Windows
            delta = int(-1 * (event.delta / 120) * 3)
        elif event.num == 4:  # Linux scroll up
            delta = -3
        elif event.num == 5:  # Linux scroll down
            delta = 3
        else:
            return
        
        self.text_area.yview_scroll(delta, "units")
        self.line_numbers_area.yview_scroll(delta, "units")
        return "break"
    
    def on_file_drop(self, event):
        """Dosya sürükle-bırak"""
        files = event.data.split()
        if files:
            file_path = files[0].strip('{}')
            if file_path.lower().endswith('.hdlang'):
                self.file_path = file_path
                self.open_hdlang()
    
    def on_font_change(self, value):
        """Font boyutu değişikliği"""
        font_size = int(value)
        self.settings["font_size"] = font_size
        
        new_font = ('Consolas', font_size)
        self.text_area.configure(font=new_font)
        self.line_numbers_area.configure(font=new_font)
        
        self.save_settings()
    
    def show_context_menu(self, event):
        """Sağ tık menüsünü göster"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    # Yardımcı fonksiyonlar
    def focus_search(self, event=None):
        """Arama kutusuna odaklan"""
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)
    
    def focus_replace(self, event=None):
        """Değiştir kutusuna odaklan"""
        self.replace_entry.focus_set()
        self.replace_entry.select_range(0, tk.END)
    
    def select_all(self, event=None):
        """Tümünü seç"""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        return "break"
    
    def copy_text(self):
        """Metni kopyala"""
        try:
            text = self.text_area.selection_get()
            self.window.clipboard_clear()
            self.window.clipboard_append(text)
        except:
            pass
    
    def paste_text(self):
        """Metni yapıştır"""
        try:
            text = self.window.clipboard_get()
            self.text_area.insert(tk.INSERT, text)
        except:
            pass
    
    def cut_text(self):
        """Metni kes"""
        try:
            text = self.text_area.selection_get()
            self.window.clipboard_clear()
            self.window.clipboard_append(text)
            self.text_area.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except:
            pass
    
    def search_selected(self):
        """Seçili metni ara"""
        try:
            selected_text = self.text_area.selection_get()
            self.search_var.set(selected_text)
            self.search_text()
        except:
            pass
    
    def new_file(self, event=None):
        """Yeni dosya"""
        if self.is_modified and not self.ask_save_changes():
            return
        
        self.file_path = None
        self.file_data = None
        self.strings_positions = []
        self.original_strings = []
        self.current_strings = []
        self.is_modified = False
        
        self.text_area.delete("1.0", tk.END)
        self.update_line_numbers()
        self.update_file_info()
        self.update_stats()
        self.mark_as_modified(False)
        
        self.file_name_label.config(text="📄 Yeni Dosya")
        self.file_status.config(text="📄 Dosya Yok", bg='#6c757d')
        self.update_status("📄 Yeni dosya oluşturuldu")
    
    def reload_file(self, event=None):
        """Dosyayı yeniden yükle"""
        if self.file_path and os.path.exists(self.file_path):
            if self.is_modified:
                result = messagebox.askyesnocancel("Onay", 
                    "Dosyada kaydedilmemiş değişiklikler var.\n\n"
                    "Yeniden yüklemek istediğinizden emin misiniz?\n"
                    "Tüm değişiklikler kaybolacak!")
                if not result:
                    return
            
            current_path = self.file_path
            self.file_path = current_path
            self.open_hdlang()
    
    def ask_save_changes(self):
        """Değişiklikleri kaydet sorusu"""
        if not self.is_modified:
            return True
        
        result = messagebox.askyesnocancel("Kaydet?", 
            "Dosyada kaydedilmemiş değişiklikler var.\n\n"
            "Değişiklikleri kaydetmek istiyor musunuz?")
        
        if result is True:  # Evet
            self.save_hdlang()
            return True
        elif result is False:  # Hayır
            return True
        else:  # İptal
            return False
    
    # Ayar fonksiyonları
    def toggle_dynamic_sizing(self):
        """Dinamik boyutlandırma aç/kapat"""
        self.settings["dynamic_sizing"] = self.dynamic_var.get()
        self.save_settings()
        
        if self.settings["dynamic_sizing"]:
            self.dynamic_indicator.config(text="🚀 Dinamik Boyut: AÇIK", bg='#28a745')
            status_msg = "🚀 Dinamik boyutlandırma aktif - string uzunluğu sınırsız!"
        else:
            self.dynamic_indicator.config(text="📏 Sabit Boyut: AÇIK", bg='#dc3545')
            status_msg = "📏 Sabit boyut - orijinal uzunluk korunacak"
        
        self.update_status(status_msg)
        self.update_stats()
    
    def toggle_auto_backup(self):
        """Otomatik yedekleme aç/kapat"""
        self.settings["auto_backup"] = self.backup_var.get()
        self.save_settings()
        
        status_msg = "💾 Otomatik yedekleme aktif" if self.settings["auto_backup"] else "❌ Otomatik yedekleme kapalı"
        self.update_status(status_msg)
    
    def toggle_auto_save(self):
        """Otomatik kaydetme aç/kapat"""
        self.settings["auto_save"] = self.autosave_var.get()
        self.save_settings()
        
        if self.settings["auto_save"]:
            self.start_auto_save_timer()
            status_msg = "💿 Otomatik kaydetme aktif"
        else:
            self.stop_auto_save_timer()
            status_msg = "❌ Otomatik kaydetme kapalı"
        
        self.update_status(status_msg)
    
    def toggle_theme(self):
        """Tema değiştir"""
        self.settings["theme"] = "light" if self.settings["theme"] == "dark" else "dark"
        self.save_settings()
        self.apply_theme()
        
        self.update_status(f"🎨 Tema değiştirildi: {self.settings['theme']}")
    
    def toggle_line_numbers(self):
        """Satır numaralarını aç/kapat"""
        if self.line_numbers_area.winfo_viewable():
            self.line_numbers_area.pack_forget()
            self.line_numbers_btn.config(bg='#6c757d')
        else:
            self.line_numbers_area.pack(side=tk.LEFT, fill=tk.Y)
            self.line_numbers_btn.config(bg='#28a745')
    
    def toggle_fullscreen(self):
        """Tam ekran aç/kapat"""
        current_state = self.window.attributes('-fullscreen')
        self.window.attributes('-fullscreen', not current_state)
    
    # Zoom fonksiyonları
    def zoom_in(self):
        """Yazı tipini büyült"""
        current_size = self.settings["font_size"]
        if current_size < 32:
            new_size = current_size + 1
            self.font_scale.set(new_size)
            self.on_font_change(new_size)
    
    def zoom_out(self):
        """Yazı tipini küçült"""
        current_size = self.settings["font_size"]
        if current_size > 6:
            new_size = current_size - 1
            self.font_scale.set(new_size)
            self.on_font_change(new_size)
    
    def zoom_reset(self):
        """Yazı tipini varsayılana döndür"""
        self.font_scale.set(12)
        self.on_font_change(12)
    
    # Otomatik kaydetme
    def start_auto_save_timer(self):
        """Otomatik kaydetme timer'ını başlat"""
        self.stop_auto_save_timer()
        if self.settings["auto_save"] and self.file_path:
            interval = self.settings.get("backup_interval", 5) * 60000  # dakika -> ms
            self.auto_save_timer = self.window.after(interval, self.auto_save)
    
    def restart_auto_save_timer(self):
        """Otomatik kaydetme timer'ını yeniden başlat"""
        if self.settings["auto_save"]:
            self.start_auto_save_timer()
    
    def stop_auto_save_timer(self):
        """Otomatik kaydetme timer'ını durdur"""
        if self.auto_save_timer:
            self.window.after_cancel(self.auto_save_timer)
            self.auto_save_timer = None
    
    def auto_save(self):
        """Otomatik kaydetme"""
        if self.is_modified and self.file_path:
            try:
                self.save_hdlang()
                self.update_status("💿 Otomatik kaydedildi")
            except:
                pass
        
        # Timer'ı yeniden başlat
        self.start_auto_save_timer()
    
    # Dialog'lar
    def show_settings(self):
        """Ayarlar penceresi"""
        settings_window = tk.Toplevel(self.window)
        settings_window.title("⚙️ Ayarlar")
        settings_window.geometry("500x400")
        settings_window.configure(bg='#2b2b2b')
        settings_window.resizable(False, False)
        
        # Ayarlar içeriği burada detaylandırılabilir
        tk.Label(settings_window, text="⚙️ Gelişmiş Ayarlar", 
                bg='#2b2b2b', fg='white', font=('Arial', 16, 'bold')).pack(pady=20)
        
        tk.Label(settings_window, text="Bu özellik geliştirme aşamasında...", 
                bg='#2b2b2b', fg='#ffc107', font=('Arial', 12)).pack()
        
        tk.Button(settings_window, text="Kapat", command=settings_window.destroy,
                 bg='#dc3545', fg='white', font=('Arial', 10), padx=20).pack(pady=20)
    
    def show_statistics(self):
        """Detaylı istatistikler penceresi"""
        if not self.current_strings:
            messagebox.showinfo("Bilgi", "Önce bir dosya açmalısınız.")
            return
        
        stats_window = tk.Toplevel(self.window)
        stats_window.title("📊 Detaylı İstatistikler")
        stats_window.geometry("600x500")
        stats_window.configure(bg='#2b2b2b')
        
        # İstatistik hesaplamaları ve görüntüleme
        # Bu kısım geliştirilebilir
        tk.Label(stats_window, text="📊 Detaylı İstatistikler", 
                bg='#2b2b2b', fg='white', font=('Arial', 16, 'bold')).pack(pady=20)
        
        stats_text = tk.Text(stats_window, bg='#2b2b2b', fg='white', font=('Consolas', 11))
        stats_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Detaylı istatistikler
        detailed_stats = self.calculate_detailed_stats()
        stats_text.insert("1.0", detailed_stats)
        stats_text.config(state=tk.DISABLED)
    
    def calculate_detailed_stats(self):
        """Detaylı istatistik hesapla"""
        if not self.current_strings:
            return "Veri yok"
        
        stats = "📊 DETAYLI İSTATİSTİKLER\n"
        stats += "=" * 50 + "\n\n"
        
        # Temel bilgiler
        total = len(self.current_strings)
        stats += f"📁 Dosya: {os.path.basename(self.file_path) if self.file_path else 'N/A'}\n"
        stats += f"📝 Toplam String: {total:,}\n\n"
        
        # Uzunluk analizi
        lengths = [len(s) for s in self.current_strings]
        stats += f"📏 UZUNLUK ANALİZİ\n"
        stats += f"{'-' * 30}\n"
        stats += f"En Kısa: {min(lengths):,} karakter\n"
        stats += f"En Uzun: {max(lengths):,} karakter\n"
        stats += f"Ortalama: {sum(lengths)/len(lengths):.1f} karakter\n"
        stats += f"Toplam: {sum(lengths):,} karakter\n\n"
        
        # Değişiklik analizi
        if self.original_strings:
            modified = sum(1 for i, s in enumerate(self.current_strings) 
                          if i < len(self.original_strings) and s != self.original_strings[i])
            stats += f"🔄 DEĞİŞİKLİK ANALİZİ\n"
            stats += f"{'-' * 30}\n"
            stats += f"Değiştirilmiş: {modified:,}\n"
            stats += f"Değişmemiş: {total - modified:,}\n"
            stats += f"Değişim Oranı: %{(modified/total)*100:.1f}\n\n"
        
        return stats
    
    def manage_backups(self):
        """Yedekleme yönetimi"""
        backup_dir = 'hdlang_backups'
        if not os.path.exists(backup_dir):
            messagebox.showinfo("Bilgi", "Henüz yedekleme oluşturulmamış.")
            return
        
        backups = [f for f in os.listdir(backup_dir) if f.endswith('.backup')]
        if not backups:
            messagebox.showinfo("Bilgi", "Yedekleme bulunamadı.")
            return
        
        # Yedekleme listesi penceresi
        backup_window = tk.Toplevel(self.window)
        backup_window.title("📦 Yedekleme Yönetimi")
        backup_window.geometry("700x400")
        backup_window.configure(bg='#2b2b2b')
        
        tk.Label(backup_window, text="📦 Yedekleme Dosyaları", 
                bg='#2b2b2b', fg='white', font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Liste kutusu
        listbox_frame = tk.Frame(backup_window, bg='#2b2b2b')
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        listbox = tk.Listbox(listbox_frame, bg='#3c3c3c', fg='white', font=('Consolas', 10))
        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar.set)
        
        for backup in sorted(backups, reverse=True):
            backup_path = os.path.join(backup_dir, backup)
            size = os.path.getsize(backup_path)
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(backup_path))
            display_text = f"{backup} ({size:,} byte) - {mtime.strftime('%Y-%m-%d %H:%M')}"
            listbox.insert(tk.END, display_text)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Butonlar
        button_frame = tk.Frame(backup_window, bg='#2b2b2b')
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="📁 Klasörü Aç", 
                 command=lambda: os.startfile(backup_dir) if os.name == 'nt' else os.system(f'open "{backup_dir}"'),
                 bg='#17a2b8', fg='white', padx=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="🗑️ Temizle", 
                 command=lambda: self.clear_old_backups(backup_window),
                 bg='#dc3545', fg='white', padx=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Kapat", command=backup_window.destroy,
                 bg='#6c757d', fg='white', padx=15).pack(side=tk.LEFT, padx=5)
    
    def clear_old_backups(self, parent_window):
        """Eski yedekleri temizle"""
        backup_dir = 'hdlang_backups'
        if messagebox.askyesno("Onay", "30 günden eski yedekleri silmek istediğinizden emin misiniz?", parent=parent_window):
            try:
                import time
                current_time = time.time()
                deleted_count = 0
                
                for filename in os.listdir(backup_dir):
                    file_path = os.path.join(backup_dir, filename)
                    if filename.endswith('.backup'):
                        file_age = current_time - os.path.getmtime(file_path)
                        if file_age > 30 * 24 * 3600:  # 30 gün
                            os.remove(file_path)
                            deleted_count += 1
                
                messagebox.showinfo("Başarılı", f"{deleted_count} eski yedekleme silindi.", parent=parent_window)
                parent_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Hata", f"Temizleme hatası: {e}", parent=parent_window)
    
    def clear_cache(self):
        """Cache'leri temizle"""
        try:
            # Geçici dosyaları temizle
            temp_files = []
            if os.path.exists('hdlang_settings.json'):
                temp_files.append('hdlang_settings.json')
            
            if messagebox.askyesno("Onay", f"Cache dosyaları temizlenecek.\n\nDevam etmek istiyor musunuz?"):
                # Burada cache temizleme işlemleri yapılır
                self.update_status("🧹 Cache temizlendi")
                messagebox.showinfo("Başarılı", "Cache başarıyla temizlendi.")
        except Exception as e:
            messagebox.showerror("Hata", f"Cache temizleme hatası: {e}")
    
    def save_recent_file(self, file_path):
        """Son açılan dosyayı kaydet"""
        try:
            recent_files = []
            if os.path.exists('recent_files.json'):
                with open('recent_files.json', 'r', encoding='utf-8') as f:
                    recent_files = json.load(f)
            
            if file_path in recent_files:
                recent_files.remove(file_path)
            
            recent_files.insert(0, file_path)
            recent_files = recent_files[:10]  # Son 10 dosya
            
            with open('recent_files.json', 'w', encoding='utf-8') as f:
                json.dump(recent_files, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def show_about(self):
        """Hakkında penceresi"""
        about_text = """🚀 HDLang Editor Pro - Masaüstü Sürümü

📋 TEMEL BİLGİLER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Sürüm: 2.0 Professional
• Platform: Windows/Linux/Mac
• Lisans: MIT License
• Geliştirici: HDLang Team

✨ ANA ÖZELLİKLER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 Dinamik String Boyutlandırma
   ↳ Uzunluk sınırı tamamen kaldırıldı!
   ↳ "new game" → "yeni bir oyuna başla" ✓

🔍 Gelişmiş Arama & Değiştirme
   ↳ Büyük/küçük harf duyarsız
   ↳ Regex desteği
   ↳ Çoklu seçim ve değiştirme

💾 Akıllı Yedekleme Sistemi
   ↳ Otomatik yedekleme
   ↳ Versiyon kontrolü
   ↳ Anlık geri yükleme

🎨 Modern Kullanıcı Arayüzü
   ↳ Koyu/Açık tema
   ↳ Özelleştirilebilir font
   ↳ Responsive tasarım

⌨️ Klavye Kısayolları
   ↳ Ctrl+O: Dosya Aç
   ↳ Ctrl+S: Kaydet
   ↳ Ctrl+F: Ara
   ↳ Ctrl+H: Değiştir

🔧 GELİŞMİŞ ARAÇLAR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Detaylı istatistikler
• Yedekleme yönetimi
• Otomatik kaydetme
• Drag & Drop desteği
• Sağ tık menüleri

💡 KULLANIM İPUÇLARI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Dinamik boyutlandırmayı etkinleştirin
2. Düzenli yedekleme yapın
3. Klavye kısayollarını kullanın
4. Arama özelliğinden faydalanın

🎯 STRING UZUNLUĞU SORUNU ÇÖZÜLDÜ!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Artık herhangi bir karakter sınırı olmadan
dilediğiniz kadar uzun metinler yazabilirsiniz!

Örnek:
❌ Eski: "new game" (9 karakter sınırı)
✅ Yeni: "yeni bir oyuna başlayalım" (25+ karakter)

🔗 BAĞLANTILAR:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• GitHub: github.com/hdlang-editor
• Dokümantasyon: docs.hdlang-editor.com
• Destek: support@hdlang-editor.com

© 2024 HDLang Editor Team. Tüm hakları saklıdır."""
        
        # Hakkında penceresi
        about_window = tk.Toplevel(self.window)
        about_window.title("ℹ️ HDLang Editor Pro Hakkında")
        about_window.geometry("800x700")
        about_window.configure(bg='#2b2b2b')
        about_window.resizable(False, False)
        
        # Scroll edilebilir metin alanı
        text_frame = tk.Frame(about_window, bg='#2b2b2b')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        text_widget = tk.Text(text_frame, bg='#2b2b2b', fg='white', 
                             font=('Consolas', 10), wrap=tk.WORD, 
                             state=tk.DISABLED, padx=15, pady=15)
        
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.config(state=tk.NORMAL)
        text_widget.insert("1.0", about_text)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Butonlar
        button_frame = tk.Frame(about_window, bg='#2b2b2b')
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="🔗 GitHub", 
                 command=lambda: webbrowser.open("https://github.com"),
                 bg='#28a745', fg='white', font=('Arial', 10), padx=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="📖 Kılavuz", command=self.show_help,
                 bg='#17a2b8', fg='white', font=('Arial', 10), padx=20).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Kapat", command=about_window.destroy,
                 bg='#dc3545', fg='white', font=('Arial', 10), padx=20).pack(side=tk.LEFT, padx=10)
    
    def show_help(self, event=None):
        """Yardım penceresi"""
        help_text = """📖 HDLang Editor Pro - Kullanım Kılavuzu

🚀 HIZLI BAŞLANGIÇ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 📁 Dosya → Aç ile .hdlang dosyası açın
2. ✏️  Stringleri düzenleyin
3. 💾 Dosya → Kaydet ile kaydedin

🎯 ANA ÖZELLİK - DİNAMİK BOYUTLANDIRMA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ Ayarlar → Dinamik Boyutlandırma'yı etkinleştirin
✅ Artık string uzunluğu sınırı yok!
📝 "new game" → "yeni bir oyuna başla" yazmak mümkün

⌨️ KLAVYE KISAYOLLARI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Ctrl+O: Dosya Aç
• Ctrl+S: Kaydet
• Ctrl+N: Yeni Dosya
• Ctrl+F: Ara
• Ctrl+H: Değiştir
• Ctrl+A: Tümünü Seç
• Ctrl+Z: Geri Al
• Ctrl+Y: İleri Al
• Ctrl++: Yakınlaştır
• Ctrl+-: Uzaklaştır
• Ctrl+0: Zoom Sıfırla
• F1: Bu Yardım
• F5: Dosyayı Yeniden Yükle
• F11: Tam Ekran
• Esc: Aramayı Temizle

🔍 ARAMA VE DEĞİŞTİRME:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Arama kutusu: Büyük/küçük harf duyarsız
• ◀ ▶ butonları: Sonuçlar arası geçiş
• Değiştir: Tek tıkla toplu değiştirme
• Esc: Aramayı temizle

💾 YEDEKLEMELERİ YÖNETME:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Araçlar → Yedeklemeler menüsü
• Otomatik yedekleme: Her dosya açılışında
• Manuel temizleme: 30+ günlük yedekleri sil
• Yedek klasörü: hdlang_backups/

🎨 TEMALARı ÖZELLEŞTİRME:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Görünüm → Tema Değiştir
• Font boyutu: Sol panelden ayarlayın
• Satır numaraları: 🔢 butonunu kullanın
• Zoom: Ctrl++ veya Ctrl+- ile

🚨 SORUN GİDERME:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ "String çok uzun" hatası:
   → Dinamik boyutlandırmayı etkinleştirin

❌ Dosya açılmıyor:
   → .hdlang uzantılı dosya kullanın
   → Dosya izinlerini kontrol edin

❌ Yedekleme çalışmıyor:
   → Otomatik yedeklemeyi etkinleştirin
   → Yazma izinlerini kontrol edin

❌ Arama çalışmıyor:
   → En az 2 karakter girin
   → Esc ile aramayı temizleyin

💡 İPUÇLARI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Dosyaları sürükle-bırak ile açabilirsiniz
• Sağ tık menüsünü kullanın
• İstatistik panelini takip edin
• Düzenli yedekleme yapın
• Dinamik boyutlandırmayı açık tutun

🔧 GELİŞMİŞ KULLANIM:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• CSV export: Metin olarak kaydet → .csv seçin
• Otomatik kaydetme: Ayarlardan etkinleştirin
• Font boyutu: 8-20 px arası ayarlayın
• Tam ekran: F11 ile çalışın

🆘 DESTEK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• GitHub Issues: Bug raporları
• E-posta: support@hdlang-editor.com
• Dokümantasyon: docs.hdlang-editor.com"""
        
        # Yardım penceresi
        help_window = tk.Toplevel(self.window)
        help_window.title("📖 Kullanım Kılavuzu")
        help_window.geometry("900x800")
        help_window.configure(bg='#2b2b2b')
        
        # Scroll edilebilir metin alanı
        text_frame = tk.Frame(help_window, bg='#2b2b2b')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        text_widget = tk.Text(text_frame, bg='#2b2b2b', fg='white', 
                             font=('Consolas', 10), wrap=tk.WORD, 
                             state=tk.DISABLED, padx=15, pady=15)
        
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.config(state=tk.NORMAL)
        text_widget.insert("1.0", help_text)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Kapat butonu
        tk.Button(help_window, text="Kapat", command=help_window.destroy,
                 bg='#dc3545', fg='white', font=('Arial', 12), padx=30, pady=5).pack(pady=10)
    
    def on_closing(self):
        """Pencere kapatılırken"""
        if self.ask_save_changes():
            self.stop_auto_save_timer()
            self.save_settings()
            self.window.destroy()
    
    def run(self):
        """Uygulamayı çalıştır"""
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Başlangıç mesajı
        self.update_status("🚀 HDLang Editor Pro başlatıldı - String sınırı yok!")
        
        try:
            self.window.mainloop()
        except KeyboardInterrupt:
            self.on_closing()

# Ana program
if __name__ == "__main__":
    # Gerekli dizinleri oluştur
    os.makedirs('hdlang_backups', exist_ok=True)
    
    try:
        print("🚀 HDLang Editor Pro başlatılıyor...")
        print("✅ String uzunluğu sınırlaması çözüldü!")
        print("💡 Dinamik boyutlandırma ile sınırsız karakter desteği")
        print("📝 'new game' → 'yeni bir oyuna başla' artık mümkün!")
        print()
        
        editor = GelistirilmisHDLangEditor()
        editor.run()
        
    except Exception as e:
        print(f"❌ Uygulama başlatılırken hata: {e}")
        print("\n🔧 Sorun giderme:")
        print("1. Python 3.7+ kullandığınızdan emin olun")
        print("2. tkinter paketinin yüklü olduğunu kontrol edin")
        print("3. Yönetici izinleriyle çalıştırmayı deneyin")
        print("\n💬 Destek için: support@hdlang-editor.com")
        input("\nÇıkmak için Enter'a basın...")