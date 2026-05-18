import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import random
import customtkinter as ctk

# --- 1. KÜTÜPHANE VE BAĞIMLILIK KONTROLÜ ---
# Projeyi başka bir bilgisayarda çalıştıran kullanıcının 'matplotlib' kütüphanesi eksikse 
# programın çökmesini engellemek için Try-Except bloğu kullanılmıştır. Hata fırlatmak yerine özellik pasife alınır.
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_YUKLU = True
except ImportError:
    MATPLOTLIB_YUKLU = False

print("FITTRACK PRO - Sistem Başlatılıyor...")

# --- 2. TEMA VE DİNAMİK RENK PALETİ ---
ctk.set_appearance_mode("Light")  
ctk.set_default_color_theme("blue")  

FONT_FAMILY = "Segoe UI" 

# Dinamik Renk Yapısı: (Light Mode, Dark Mode)
# Projenin ana arka plan rengi burada tanımlanır.
# İlk görseldeki göz yormayan koyu maviyi geri getirmek için Tuple'ın ilk değerini değiştiriyoruz.
BG_COLOR = ("#0033A0", "#000000") # Blue Angels Mavisi / Saf Siyah

# CustomTkinter kütüphanesinin dinamik tema özelliği kullanılmıştır. 
# Renkler (Light_Mode_Rengi, Dark_Mode_Rengi) şeklinde Tuple olarak tanımlanır.
# Sistem teması değiştiğinde arka planda hiçbir if-else bloğuna gerek kalmadan renkler otomatik adapte olur.

# GÜNCELLEME: Üst menü (navbar) rengi göz yormayan ve ana renkle uyumlu yumuşak tonlarla değiştirildi.
NAVBAR_BG = ("#E6F0FA", "#121826")         # Üst Menü: Soft Buzul Mavi-Gri / Koyu Lacivert-Gri

CARD_BG = ("#D9E2EC", "#111111")           # Kart Zeminleri (Çarpı alanları): Soft Buzul Mavisi / Çok Koyu Gri
ENTRY_BG = ("#FFFFFF", "#1A1A1A")          # Girdi Alanları (Tik alanları): Beyaz / Koyu Gri

TEXT_MAIN = ("#1E293B", "#F8FAFC")         
TEXT_SUB = ("#475569", "#818CF8")          

ACCENT_COLOR = ("#0033A0", "#6366F1")      
ACCENT_HOVER = ("#002277", "#4F46E5")      

SUCCESS_COLOR = ("#10B981", "#2DD4BF")     
SUCCESS_HOVER = ("#059669", "#14B8A6")

DANGER_COLOR = ("#EF4444", "#F472B6")      
DANGER_HOVER = ("#DC2626", "#DB2777")

COLOR_ZAYIF = ("#0EA5E9", "#7DD3FC")       
COLOR_NORMAL = ("#10B981", "#2DD4BF")      
COLOR_FAZLA = ("#F59E0B", "#FCD34D")       
COLOR_OBEZ = ("#EF4444", "#F472B6")        

WHITE = "#FFFFFF"
BLACK = "#000000"

# --- 3. SABİT VERİLER VE İŞ MANTIĞI (BUSINESS LOGIC) ---
POPULER_50_SPOR = [
    "1. Koşu", "2. Yüzme", "3. Bisiklet", "4. Ağırlık Antrenmanı", "5. Pilates", 
    "6. Yoga", "7. Futbol", "8. Basketbol", "9. Voleybol", "10. Tenis", 
    "11. Masa Tenisi", "12. Boks", "13. Kickboks", "14. CrossFit", "15. Halter", 
    "16. Jimnastik", "17. Kürek", "18. Atletizm", "19. Güreş", "20. Judo", 
    "21. Karate", "22. Taekwondo", "23. Eskrim", "24. Okçuluk", "25. Badminton", 
    "26. Golf", "27. Hentbol", "28. Su Topu", "29. Buz Pateni", "30. Kayak", 
    "31. Snowboard", "32. Dağcılık", "33. Tırmanış", "34. Sörf", "35. Yelken", 
    "36. Binicilik", "37. Triatlon", "38. Maraton", "39. Zumba", "40. Aerobik", 
    "41. Step", "42. Dans", "43. Squash", "44. Rugby", "45. Amerikan Futbolu", 
    "46. Beyzbol", "47. Kriket", "48. İp Atlama", "49. Kalistenik", "50. MMA"
]

# Kalori hesaplaması kullanıcıya bırakılmamış, tıp biliminde kullanılan MET 
# (Metabolic Equivalent of Task) algoritması koda entegre edilmiştir.
MET_DEGERLERI = {
    "1. Koşu": 9.8, "2. Yüzme": 7.0, "3. Bisiklet": 7.5, "4. Ağırlık Antrenmanı": 3.0, "5. Pilates": 3.0, 
    "6. Yoga": 2.5, "7. Futbol": 7.0, "8. Basketbol": 6.5, "9. Voleybol": 4.0, "10. Tenis": 7.3, 
    "11. Masa Tenisi": 4.0, "12. Boks": 9.0, "13. Kickboks": 10.0, "14. CrossFit": 8.0, "15. Halter": 5.0, 
    "16. Jimnastik": 4.0, "17. Kürek": 7.0, "18. Atletizm": 7.5, "19. Güreş": 6.0, "20. Judo": 7.0, 
    "21. Karate": 10.0, "22. Taekwondo": 10.0, "23. Eskrim": 6.0, "24. Okçuluk": 4.3, "25. Badminton": 5.5, 
    "26. Golf": 4.3, "27. Hentbol": 8.0, "28. Su Topu": 10.0, "29. Buz Pateni": 7.0, "30. Kayak": 7.0, 
    "31. Snowboard": 5.3, "32. Dağcılık": 7.5, "33. Tırmanış": 8.0, "34. Sörf": 3.0, "35. Yelken": 3.0, 
    "36. Binicilik": 5.5, "37. Triatlon": 9.0, "38. Maraton": 11.0, "39. Zumba": 6.8, "40. Aerobik": 7.3, 
    "41. Step": 8.5, "42. Dans": 5.0, "43. Squash": 7.3, "44. Rugby": 8.3, "45. Amerikan Futbolu": 8.0, 
    "46. Beyzbol": 5.0, "47. Kriket": 4.8, "48. İp Atlama": 10.0, "49. Kalistenik": 8.0, "50. MMA": 10.0
}

# Sanal Antrenör Tavsiye Veri Tabanı
TAVSIYELER = {
    "Zayıf": {
        "yap": [
            "1. Günlük kalori alımını harcadığından 300-500 kcal fazla tut (Kalori Fazlası oluştur).",
            "2. Ağırlık ve direnç antrenmanlarına odaklanarak kas kütleni artırmayı hedefle.",
            "3. Kuruyemiş, zeytinyağı, fıstık ezmesi gibi hacmi küçük ama kalorisi yüksek sağlıklı yağlar tüket.",
            "4. Kas gelişimi için günlük protein alımını (kilo başına 1.5 - 2 gram) artır.",
            "5. Öğün sayısını artır. Ara öğünlerle beslenmeni destekleyerek sürekli anabolik kal."
        ],
        "yapma": [
            "1. Uzun süreli ve yüksek tempolu kardiyo (maraton koşusu, uzun yüzme vb.) yapmaktan kaçın.",
            "2. Sadece fast-food ve şekerli gıdalarla sağlıksız 'kirli' kilo almaya çalışma.",
            "3. Antrenman sürelerini çok uzun tutma (Maksimum 45-60 dakika idealdir).",
            "4. Geceleri düzensiz uyuyarak kas gelişimini ve onarımını baltalama.",
            "5. Öğün atlama! Öğünleri geçiştirerek vücudunu katabolik (kas yıkımı) duruma sokma."
        ]
    },
    "Normal": {
        "yap": [
            "1. Mevcut kas kütlesini ve formunu korumak için düzenli direnç egzersizleri yap.",
            "2. Kardiyo ve ağırlık antrenmanlarını dengeli dağıt (Örn: 3 gün ağırlık, 2 gün kardiyo).",
            "3. Eklemlerini ve kaslarını korumak için esneklik (Yoga/Pilates) hareketleri ekle.",
            "4. Makro besin (Protein, Karbonhidrat, Yağ) dengeni günlük ihtiyacına göre koru.",
            "5. Günlük su tüketimini kilona uygun olarak (ortalama 2.5 - 3 Litre) sabit tut."
        ],
        "yapma": [
            "1. 'Zaten formdayım' diyerek şok diyetler veya gereksiz kalori kısıtlamaları deneme.",
            "2. Antrenman rutinine saplanıp kalma, vücudu şaşırtmak için hareketleri çeşitlendir.",
            "3. Aşırı işlenmiş paketli gıdaları ve basit şekerleri günlük rutinine dahil etme.",
            "4. Antrenman programında dinlenme (Rest Day) günlerini atlayıp kendini sürantrene (Overtraining) etme.",
            "5. Sadece kardiyoya veya sadece ağırlığa odaklanıp kondisyon dengeni bozma."
        ]
    },
    "Fazla Kilolu": {
        "yap": [
            "1. Kontrollü ve sağlıklı bir kalori açığı (Deficit) oluştur (Günlük harcadığından 300-500 kcal az al).",
            "2. Yağ yakımını hızlandırmak için Yüksek Yoğunluklu Aralıklı Antrenman (HIIT) rutinine ekle.",
            "3. Tokluk hissini artırmak için lifli gıdalar (yulaf, sebzeler) ve protein tüketimini artır.",
            "4. Güç antrenmanları yaparak dinlenik metabolizma hızını (RMR) yükselt.",
            "5. Günlük hareketliliğini (NEAT) artır, 10.000 adım kuralını alışkanlık haline getir."
        ],
        "yapma": [
            "1. Kendini günlerce aç bırakarak su ve kas kaybettiren şok diyetler (Örn: Sadece sıvı diyeti) yapma.",
            "2. Hazır meyve suları, asitli içecekler ve gizli şeker barındıran gıdalardan kesinlikle uzak dur.",
            "3. Eklem kaslarına zarar verebilecek aşırı zorlayıcı zıplama (plyometric) hareketlerine hemen girme.",
            "4. Geç saatlerde ağır ve yüksek karbonhidratlı öğünler tüketmekten kaçın.",
            "5. Kısa sürede mucize sonuçlar bekleme, tartıdaki günlük oynamalara takılıp motivasyonunu düşürme."
        ]
    },
    "Obez": {
        "yap": [
            "1. Eklemleri yormayan, düşük etkili (Low-Impact) egzersizlerle (Yüzme, Bisiklet, Tempolu Yürüyüş) başla.",
            "2. Tabak boyutlarını küçülterek ve yavaş yiyerek porsiyon kontrolü sağlamaya odaklan.",
            "3. Basit şekerleri ve beyaz unlu gıdaları hayatından tamamen çıkarmayı hedefle.",
            "4. Süreci profesyonelce yönetmek için bir diyetisyen veya uzman hekim kontrolünde ilerle.",
            "5. Uyku kalitene dikkat et; yetersiz uyku, iştah açıcı hormonları (Ghrelin) tetikler."
        ],
        "yapma": [
            "1. Diz ve ayak bileklerine yüksek basınç bindiren koşu veya ip atlama gibi sporlardan başlangıçta kaçın.",
            "2. 'Light' veya 'Diyet' etiketiyle satılan yüksek sodyum ve tatlandırıcılı işlenmiş ürünlere aldanma.",
            "3. Çabuk pes etme; bu uzun bir maraton, ilk haftalardaki su atımından sonra yavaşlayan kiloya takılma.",
            "4. Ağır ağırlıklar veya zorlayıcı CrossFit gibi vücudunu riske atacak programlara aniden girme.",
            "5. Öğün atlayarak metabolizmanı 'kıtlık moduna' sokup yağ yakımını durdurma."
        ]
    }
}

ZAYIF_MESAJLAR = ["Biraz daha kalori alarak o güzel kasları besleyebiliriz! 💪", "Sağlıklı atıştırmalıklarla enerjini artırmaya ne dersin? 🥜"]
NORMAL_MESAJLAR = ["Harika görünüyorsun! Formunu korumaya aynen devam! 🌟", "Mükemmel denge! Disiplinin her halinden belli oluyor. 👏"]
KILOLU_MESAJLAR = ["Hedeflerine ulaşmak için harika bir yoldasın, pes etmek yok! 🔥", "Küçük adımlar büyük değişimler getirir. ✨"]
OBEZ_MESAJLAR = ["Bu yola çıkma cesaretin bile en büyük başarı! 🧗‍♂️", "Sağlığın için attığın her adım çok değerli. Birlikte başaracağız! 🚀"]

# --- 4. VERİTABANI VE ORM (Object-Relational Mapping) İŞLEMLERİ ---
def db_baglan():
    return sqlite3.connect("fittrack_pro.db")

def veritabanini_kur():
    """
    Sistem ilk kez başlatıldığında veritabanını kurar.
    Veritabanı zaten varsa eksik sütunları güncelleyerek Migration işlemi yapar.
    """
    conn = db_baglan()
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sporcular'")
    if not cursor.fetchone():
        cursor.execute('''CREATE TABLE sporcular (
                id INTEGER PRIMARY KEY AUTOINCREMENT, ad TEXT, kilo REAL, boy REAL, cinsiyet TEXT DEFAULT 'Belirtmek İstemiyorum')''')
    else:
        # Basit Migration Mantığı. Tablo varsa ama 'cinsiyet' sütunu yoksa ALTER komutu ile ekler. 
        # Bu sayede eski kullanıcı verileri kaybolmadan veri tabanı güncellenir.
        cursor.execute("PRAGMA table_info(sporcular)")
        if 'cinsiyet' not in [col[1] for col in cursor.fetchall()]:
            cursor.execute("ALTER TABLE sporcular ADD COLUMN cinsiyet TEXT DEFAULT 'Belirtmek İstemiyorum'")
            
    cursor.execute('''CREATE TABLE IF NOT EXISTS antrenmanlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT, sporcu_id INTEGER, tur TEXT, sure REAL, kalori REAL, tarih TEXT,
            FOREIGN KEY (sporcu_id) REFERENCES sporcular (id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS kilo_gecmisi (
            id INTEGER PRIMARY KEY AUTOINCREMENT, sporcu_id INTEGER, kilo REAL, tarih TEXT,
            FOREIGN KEY (sporcu_id) REFERENCES sporcular (id))''')
            
    cursor.execute("SELECT COUNT(*) FROM kilo_gecmisi")
    if cursor.fetchone()[0] == 0:
        cursor.execute("SELECT id, kilo FROM sporcular")
        for k_id, k_kilo in cursor.fetchall():
            cursor.execute("INSERT INTO kilo_gecmisi (sporcu_id, kilo, tarih) VALUES (?, ?, ?)", (k_id, k_kilo, datetime.now().strftime("%Y-%m-%d")))
            
    cursor.execute("SELECT COUNT(*) FROM sporcular")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO sporcular (ad, kilo, boy, cinsiyet) VALUES ('Ahmet Yılmaz', 85.0, 1.82, 'Erkek')")
        ahmet_id = cursor.lastrowid
        cursor.execute("INSERT INTO kilo_gecmisi (sporcu_id, kilo, tarih) VALUES (?, ?, ?)", (ahmet_id, 85.0, datetime.now().strftime("%Y-%m-%d")))
        cursor.execute("INSERT INTO antrenmanlar (sporcu_id, tur, sure, kalori, tarih) VALUES (?, ?, ?, ?, ?)",
                       (ahmet_id, "14. CrossFit", 45, 600, datetime.now().strftime("%Y-%m-%d %H:%M")))
                       
    conn.commit()
    conn.close()

# --- 5. OOP (Nesne Yönelimli Programlama) SINIFLARI ---
class Sporcu:
    """Veritabanındaki her bir kullanıcıyı RAM üzerinde bir obje olarak temsil eder."""
    def __init__(self, s_id, ad, kilo, boy, cinsiyet):
        self.id = s_id
        self.ad = ad
        self.kilo = kilo
        self.boy = boy
        self.cinsiyet = cinsiyet

    def vki_hesapla(self):
        """Kilo ve boy verisini kullanarak Vücut Kitle İndeksini hesaplar."""
        return round(self.kilo / (self.boy ** 2), 2)

# --- 6. ANA ARAYÜZ (GUI) SINIFI ---
class FitTrackApp:
    def __init__(self, root):
        self.root = root
        
        self.root.title("FITTRACK - Fitness Takip Sistemi")
        self.root.geometry("1200x800")
        # Projenin ana arka plan rengi burada tanımlanır.
        
        self.root.configure(fg_color=BG_COLOR)
        
        self.root.grid_columnconfigure(1, weight=1) 
        self.root.grid_rowconfigure(1, weight=1)    
        
        self.aktif_sporcu = None
        self.arayuzu_hazirla()
        self.stilleri_ayarla_treeview() 
        self.combo_listesini_guncelle()

    def stilleri_ayarla_treeview(self):
        """Tkinter varsayılan tablolarını CustomTkinter tarzında modernleştirir."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", font=(FONT_FAMILY, 10), rowheight=40, borderwidth=0)
        style.configure("Treeview.Heading", font=(FONT_FAMILY, 10, "bold"), padding=10, borderwidth=0)
        self.guncelle_treeview_renkleri() 

    def guncelle_treeview_renkleri(self):
        style = ttk.Style()
        if ctk.get_appearance_mode() == "Dark":
            style.configure("Treeview", background=ENTRY_BG[1], foreground=TEXT_MAIN[1], fieldbackground=ENTRY_BG[1])
            style.configure("Treeview.Heading", background=CARD_BG[1], foreground=TEXT_SUB[1])
            style.map('Treeview', background=[('selected', ACCENT_COLOR[1])], foreground=[('selected', 'white')])
        else:
            style.configure("Treeview", background=ENTRY_BG[0], foreground=TEXT_MAIN[0], fieldbackground=ENTRY_BG[0])
            style.configure("Treeview.Heading", background=CARD_BG[0], foreground=TEXT_SUB[0])
            style.map('Treeview', background=[('selected', ACCENT_COLOR[0])], foreground=[('selected', 'white')])

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        self.guncelle_treeview_renkleri() 
        self.ekrani_yenile() 

    def arayuzu_hazirla(self):
        """Sistemin tüm arayüz bileşenlerini Grid ve Pack yapılarıyla oluşturur."""
        self.navbar = ctk.CTkFrame(self.root, height=90, corner_radius=0, fg_color=NAVBAR_BG)
        self.navbar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.navbar.pack_propagate(False) # Frame yüksekliğini içindeki elemanlara göre daraltmasını engeller
        
        logo_frame = ctk.CTkFrame(self.navbar, fg_color="transparent")
        logo_frame.pack(side="left", padx=30, pady=25)
        ctk.CTkLabel(logo_frame, text="FIT", font=(FONT_FAMILY, 30, "bold"), text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkLabel(logo_frame, text="TRACK", font=(FONT_FAMILY, 30, "bold"), text_color=ACCENT_COLOR).pack(side="left")

        sag_menu = ctk.CTkFrame(self.navbar, fg_color="transparent")
        sag_menu.pack(side="right", padx=30, pady=25)
        
        self.cb_profil = ctk.CTkComboBox(sag_menu, width=240, height=40, font=(FONT_FAMILY, 13), state="readonly", 
                                         fg_color=ENTRY_BG, text_color=TEXT_MAIN, button_color=ACCENT_COLOR, 
                                         button_hover_color=ACCENT_HOVER, border_color=ACCENT_COLOR, command=self.profil_degistir_event)
        self.cb_profil.pack(side="left", padx=10)

        self.btn_yeni_profil = ctk.CTkButton(sag_menu, text="+ Yeni Üye", width=120, height=40, font=(FONT_FAMILY, 13, "bold"), 
                                             fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, text_color=WHITE, 
                                             corner_radius=20, command=self.yeni_profil_penceresi)
        self.btn_yeni_profil.pack(side="left", padx=10)
        
        self.theme_switch = ctk.CTkSegmentedButton(sag_menu, values=["Light", "Dark"], height=40, font=(FONT_FAMILY, 12), command=self.change_appearance_mode_event, 
                                                   corner_radius=20, selected_color=ACCENT_COLOR, selected_hover_color=ACCENT_HOVER)
        self.theme_switch.pack(side="left", padx=10)
        self.theme_switch.set("Light")

        self.ana_govde = ctk.CTkFrame(self.root, fg_color="transparent")
        self.ana_govde.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=30, pady=25)
        self.ana_govde.grid_columnconfigure(1, weight=1)
        self.ana_govde.grid_rowconfigure(0, weight=1)

        # SOL KART (SPORCU ÖZETİ)
        self.profil_kart = ctk.CTkFrame(self.ana_govde, width=320, corner_radius=15, fg_color=CARD_BG)
        self.profil_kart.grid(row=0, column=0, sticky="ns", padx=(0, 25))
        self.profil_kart.grid_propagate(False) 
        
      
        ctk.CTkLabel(self.profil_kart, text="Sporcu Kimliği", font=(FONT_FAMILY, 18, "bold"), text_color=TEXT_MAIN).pack(anchor="w", padx=20, pady=(20, 10))

        self.lbl_ad = ctk.CTkLabel(self.profil_kart, text="Ad Soyad: -", font=(FONT_FAMILY, 16, "bold"), text_color=TEXT_MAIN)
        self.lbl_ad.pack(anchor="w", padx=20, pady=(0, 10))
        
        self.lbl_cinsiyet = ctk.CTkLabel(self.profil_kart, text="Cinsiyet: -", font=(FONT_FAMILY, 12), text_color=TEXT_SUB)
        self.lbl_cinsiyet.pack(anchor="w", padx=20, pady=2)
        self.lbl_kilo = ctk.CTkLabel(self.profil_kart, text="Kilo: -", font=(FONT_FAMILY, 12), text_color=TEXT_SUB)
        self.lbl_kilo.pack(anchor="w", padx=20, pady=2)
        self.lbl_boy = ctk.CTkLabel(self.profil_kart, text="Boy: -", font=(FONT_FAMILY, 12), text_color=TEXT_SUB)
        self.lbl_boy.pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkFrame(self.profil_kart, height=1, fg_color=ACCENT_COLOR).pack(fill="x", padx=20, pady=15) 
        
        ctk.CTkLabel(self.profil_kart, text="Vücut Kitle İndeksi", font=(FONT_FAMILY, 12), text_color=TEXT_SUB).pack()
        self.lbl_vki = ctk.CTkLabel(self.profil_kart, text="-", font=(FONT_FAMILY, 54, "bold"))
        self.lbl_vki.pack(pady=2)
        
        self.lbl_vki_durum = ctk.CTkLabel(self.profil_kart, text="Durum: -", font=(FONT_FAMILY, 14, "bold"))
        self.lbl_vki_durum.pack(pady=2)
        
        self.lbl_vki_mesaj = ctk.CTkLabel(self.profil_kart, text="", font=(FONT_FAMILY, 11), text_color=TEXT_SUB, wraplength=270)
        self.lbl_vki_mesaj.pack(pady=(5, 10), padx=20)

        self.btn_tavsiye = ctk.CTkButton(self.profil_kart, text="💡 Kişisel Tavsiyeler", font=(FONT_FAMILY, 12, "bold"), height=35,
                                           fg_color=SUCCESS_COLOR, hover_color=SUCCESS_HOVER, text_color=WHITE, 
                                           corner_radius=10, command=self.tavsiyeleri_goster)
        self.btn_tavsiye.pack(fill="x", padx=20, pady=(0, 8))

        self.btn_grafikler = ctk.CTkButton(self.profil_kart, text="📈 Gelişim Grafikleri", font=(FONT_FAMILY, 12, "bold"), height=35,
                                           fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, text_color=WHITE, 
                                           corner_radius=10, command=self.grafikleri_goster)
        self.btn_grafikler.pack(fill="x", padx=20, pady=(0, 10))

        self.sol_buton_frame = ctk.CTkFrame(self.profil_kart, fg_color="transparent")
        self.sol_buton_frame.pack(fill="x", side="bottom", pady=20, padx=20)
        
        self.btn_guncelle = ctk.CTkButton(self.sol_buton_frame, text="Profili Güncelle", width=120, height=35, corner_radius=10, font=(FONT_FAMILY, 12, "bold"),
                                          fg_color="transparent", text_color=ACCENT_COLOR, border_width=1, 
                                          border_color=ACCENT_COLOR, command=self.profil_guncelle_penceresi)
        self.btn_guncelle.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.btn_sil = ctk.CTkButton(self.sol_buton_frame, text="Sil", width=60, height=35, corner_radius=10, font=(FONT_FAMILY, 12, "bold"),
                                     fg_color="transparent", text_color=DANGER_COLOR, border_width=1, border_color=DANGER_COLOR, 
                                     hover_color=DANGER_HOVER, command=self.profili_sil)
        self.btn_sil.pack(side="right", padx=(5, 0))

        # SAĞ GÖVDE (FORM VE GEÇMİŞ)
        self.sag_govde = ctk.CTkFrame(self.ana_govde, fg_color="transparent")
        self.sag_govde.grid(row=0, column=1, sticky="nsew")
        self.sag_govde.grid_rowconfigure(1, weight=1) 
        
        self.form_kart = ctk.CTkFrame(self.sag_govde, corner_radius=15, fg_color=CARD_BG)
        self.form_kart.pack(fill="x", pady=(0, 25))
        
        ctk.CTkLabel(self.form_kart, text="Yeni Antrenman Kaydı", font=(FONT_FAMILY, 16, "bold"), text_color=TEXT_MAIN).pack(anchor="w", padx=25, pady=(20, 15))
        
        form_icerik = ctk.CTkFrame(self.form_kart, fg_color="transparent")
        form_icerik.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkLabel(form_icerik, text="Spor Branşı", font=(FONT_FAMILY, 11), text_color=TEXT_SUB).grid(row=0, column=0, sticky="w", padx=(0, 15))
        
        self.cb_spor = ttk.Combobox(form_icerik, values=POPULER_50_SPOR, state="readonly", width=17, font=(FONT_FAMILY, 12))
        self.cb_spor.configure(height=7) 
        self.cb_spor.grid(row=1, column=0, padx=(0, 15), pady=(5, 0), ipady=3)
        self.cb_spor.set(POPULER_50_SPOR[0])

        ctk.CTkLabel(form_icerik, text="Süre (Dakika)", font=(FONT_FAMILY, 11), text_color=TEXT_SUB).grid(row=0, column=1, sticky="w", padx=(0, 15))
        self.ent_sure = ctk.CTkEntry(form_icerik, width=120, font=(FONT_FAMILY, 12), fg_color=ENTRY_BG, text_color=TEXT_MAIN, border_color=ACCENT_COLOR, border_width=1, corner_radius=10, placeholder_text="Örn: 45")
        self.ent_sure.grid(row=1, column=1, padx=(0, 15), pady=(5, 0))

        ctk.CTkLabel(form_icerik, text="Yakılan Kalori", font=(FONT_FAMILY, 11), text_color=TEXT_SUB).grid(row=0, column=2, sticky="w", padx=(0, 15))
        self.lbl_otomatik_kalori = ctk.CTkLabel(form_icerik, text="⚡ Sistem Hesaplar", font=(FONT_FAMILY, 12, "italic"), text_color=SUCCESS_COLOR[0] if ctk.get_appearance_mode() == "Light" else SUCCESS_COLOR[1])
        self.lbl_otomatik_kalori.grid(row=1, column=2, padx=(0, 15), pady=(5, 0), sticky="w")

        self.btn_kaydet = ctk.CTkButton(form_icerik, text="➕ Kaydet", width=150, height=35, font=(FONT_FAMILY, 12, "bold"), 
                                        fg_color=SUCCESS_COLOR, hover_color=SUCCESS_HOVER, text_color=WHITE, 
                                        corner_radius=20, command=self.antrenman_kaydet)
        self.btn_kaydet.grid(row=1, column=3, pady=(5, 0), sticky="s")

        self.tablo_kart = ctk.CTkFrame(self.sag_govde, corner_radius=15, fg_color=CARD_BG)
        self.tablo_kart.pack(fill="both", expand=True)
        
        ust_tablo_frame = ctk.CTkFrame(self.tablo_kart, fg_color="transparent")
        ust_tablo_frame.pack(fill="x", padx=20, pady=(20, 15))
        
        ctk.CTkLabel(ust_tablo_frame, text="Aktivite Geçmişi", font=(FONT_FAMILY, 16, "bold"), text_color=TEXT_MAIN).pack(side="left")
        
        self.btn_db = ctk.CTkButton(ust_tablo_frame, text="🗄️ Sistem DB", width=120, height=35, font=(FONT_FAMILY, 11, "bold"), 
                                    fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, text_color=WHITE, 
                                    corner_radius=10, command=self.veritabani_penceresi)
        self.btn_db.pack(side="right")

        self.tablo_frame = ctk.CTkFrame(self.tablo_kart, fg_color="transparent")
        self.tablo_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tablo = ttk.Treeview(self.tablo_frame, columns=("Tur", "Sure", "Kalori", "Tarih"), show="headings")
        self.tablo.heading("Tur", text="BRANŞ", anchor="w")
        self.tablo.heading("Sure", text="SÜRE")
        self.tablo.heading("Kalori", text="KALORİ")
        self.tablo.heading("Tarih", text="TARİH")
        
        self.tablo.column("Tur", width=300, anchor="w") 
        self.tablo.column("Sure", width=120, anchor="center")
        self.tablo.column("Kalori", width=120, anchor="center")
        self.tablo.column("Tarih", width=180, anchor="center")
        self.tablo.pack(fill="both", expand=True, side="left")
        
        self.scrollbar = ctk.CTkScrollbar(self.tablo_frame, command=self.tablo.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.tablo.configure(yscrollcommand=self.scrollbar.set)

    # --- PENCERE İŞLEMLERİ (MODAL YÖNETİMİ) ---
    def tavsiyeleri_goster(self):
        if not self.aktif_sporcu:
            messagebox.showwarning("Uyarı", "Tavsiyeleri görebilmek için lütfen profil seçiniz.")
            return

        vki = self.aktif_sporcu.vki_hesapla()
        if vki < 18.5:
            kategori = "Zayıf"
        elif 18.5 <= vki < 25.0:
            kategori = "Normal"
        elif 25.0 <= vki < 30.0:
            kategori = "Fazla Kilolu"
        else:
            kategori = "Obez"

        veriler = TAVSIYELER[kategori]

        win = ctk.CTkToplevel(self.root)
        win.title(f"{self.aktif_sporcu.ad} - Sanal Antrenör ({kategori})")
        win.geometry("900x500")
        win.configure(fg_color=BG_COLOR)
        
        # Pop-up pencerelerinin ana pencerenin arkasına düşmesini engellemek
        # ve odak kaybını önlemek için Z-Order kilitlemesi yapılmıştır.
        win.transient(self.root)
        win.lift()
        win.grab_set()

        
        ctk.CTkLabel(win, text=f"💡 Kişisel Hedef ve Tavsiyeleriniz", font=(FONT_FAMILY, 20, "bold"), text_color=WHITE).pack(pady=25)

        main_frame = ctk.CTkFrame(win, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        yap_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color=CARD_BG)
        yap_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        baslik_yap = ctk.CTkLabel(yap_frame, text="✅ Yapılması Gerekenler", font=(FONT_FAMILY, 16, "bold"), text_color=SUCCESS_COLOR)
        baslik_yap.pack(pady=15, padx=20, anchor="w")
        
        for madde in veriler["yap"]:
            ctk.CTkLabel(yap_frame, text=madde, font=(FONT_FAMILY, 13), text_color=TEXT_MAIN, wraplength=350, justify="left").pack(anchor="w", padx=20, pady=8)

        yapma_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color=CARD_BG)
        yapma_frame.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        
        baslik_yapma = ctk.CTkLabel(yapma_frame, text="❌ Uzak Durulması Gerekenler", font=(FONT_FAMILY, 16, "bold"), text_color=DANGER_COLOR)
        baslik_yapma.pack(pady=15, padx=20, anchor="w")
        
        for madde in veriler["yapma"]:
            ctk.CTkLabel(yapma_frame, text=madde, font=(FONT_FAMILY, 13), text_color=TEXT_MAIN, wraplength=350, justify="left").pack(anchor="w", padx=20, pady=8)

    def grafikleri_goster(self):
        if not self.aktif_sporcu:
            messagebox.showwarning("Uyarı", "Grafikleri görebilmek için profil seçiniz.")
            return

        if not MATPLOTLIB_YUKLU:
            messagebox.showerror("Eksik Modül", "Grafikler için 'matplotlib' kütüphanesi gereklidir.")
            return

        conn = db_baglan()
        cursor = conn.cursor()
        cursor.execute("SELECT tarih, kilo FROM kilo_gecmisi WHERE sporcu_id = ? ORDER BY tarih ASC, id ASC", (self.aktif_sporcu.id,))
        kilo_verileri = cursor.fetchall()
        
        cursor.execute('''SELECT substr(tarih, 1, 10) as gun, SUM(sure) 
            FROM antrenmanlar WHERE sporcu_id = ? GROUP BY gun ORDER BY gun ASC''', (self.aktif_sporcu.id,))
        sure_verileri = cursor.fetchall()
        conn.close()

        if not kilo_verileri and not sure_verileri:
            messagebox.showinfo("Bilgi", "Yeterli veri bulunmamaktadır.")
            return

        graph_win = ctk.CTkToplevel(self.root)
        graph_win.title("Gelişim Analizi")
        graph_win.geometry("850x650")
        
        graph_win.transient(self.root) 
        graph_win.lift()               
        graph_win.grab_set()           

        is_light = ctk.get_appearance_mode() == "Light"
        bg_renk = CARD_BG[0] if is_light else BG_COLOR[1]
        text_renk = TEXT_MAIN[0] if is_light else TEXT_MAIN[1]
        plot_color = ACCENT_COLOR[0] if is_light else ACCENT_COLOR[1]
        bar_color = SUCCESS_COLOR[0] if is_light else SUCCESS_COLOR[1]
        
        fig = Figure(figsize=(8, 6), dpi=100, facecolor=bg_renk)
        
        if kilo_verileri:
            ax1 = fig.add_subplot(211)
            tarihler_k = [v[0][-5:] for v in kilo_verileri] 
            kilolar = [v[1] for v in kilo_verileri]
            ax1.plot(tarihler_k, kilolar, color=plot_color, marker='o', linestyle='-', linewidth=2.5, markersize=6)
            ax1.set_title("Kilo Değişim Trendi", color=text_renk, fontsize=12, fontweight='bold')
            ax1.set_facecolor(bg_renk)
            ax1.tick_params(colors=text_renk)
            ax1.spines['bottom'].set_color(text_renk)
            ax1.spines['left'].set_color(text_renk)
            ax1.spines['top'].set_visible(False)
            ax1.spines['right'].set_visible(False)
            ax1.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.2)

        if sure_verileri:
            ax2 = fig.add_subplot(212)
            tarihler_s = [v[0][-5:] for v in sure_verileri]
            sureler = [v[1] for v in sure_verileri]
            x_pos = range(len(tarihler_s))
            ax2.bar(x_pos, sureler, color=bar_color, alpha=0.85, width=0.5)
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels(tarihler_s, rotation=0 if len(tarihler_s) < 5 else 45)
            ax2.set_title("Günlük Antrenman Süresi", color=text_renk, fontsize=12, fontweight='bold')
            ax2.set_facecolor(bg_renk)
            ax2.tick_params(colors=text_renk)
            ax2.spines['bottom'].set_color(text_renk)
            ax2.spines['left'].set_color(text_renk)
            ax2.spines['top'].set_visible(False)
            ax2.spines['right'].set_visible(False)
            ax2.grid(axis='y', color='gray', linestyle='--', linewidth=0.5, alpha=0.2)

        fig.tight_layout(pad=3.0)
        canvas = FigureCanvasTkAgg(fig, master=graph_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)

    def veritabani_penceresi(self):
        self.db_win = ctk.CTkToplevel(self.root)
        self.db_win.title("Veritabanı Yönetimi")
        self.db_win.geometry("1000x650")
        self.db_win.configure(fg_color=BG_COLOR)
        
        self.db_win.transient(self.root)
        self.db_win.lift()
        self.db_win.grab_set()

        ctk.CTkLabel(self.db_win, text="Veritabanı", font=(FONT_FAMILY, 18, "bold"), text_color=WHITE).pack(pady=20, padx=30, anchor="w")

        self.tabview = ctk.CTkTabview(self.db_win, width=940, height=540, corner_radius=15, 
                                      fg_color=CARD_BG, segmented_button_fg_color=BG_COLOR, 
                                      segmented_button_selected_color=ACCENT_COLOR, segmented_button_selected_hover_color=ACCENT_HOVER)
        self.tabview.pack(padx=30, pady=(0, 30))
        self.tabview.add("Kullanıcılar")
        self.tabview.add("Antrenmanlar")

        tree1_frame = ctk.CTkFrame(self.tabview.tab("Kullanıcılar"), fg_color="transparent")
        tree1_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.tree_sporcular = ttk.Treeview(tree1_frame, columns=("ID", "Ad", "Cinsiyet", "Kilo", "Boy", "VKI"), show="headings")
        self.tree_sporcular.heading("ID", text="ID")
        self.tree_sporcular.heading("Ad", text="AD SOYAD")
        self.tree_sporcular.heading("Cinsiyet", text="CİNSİYET")
        self.tree_sporcular.heading("Kilo", text="KİLO")
        self.tree_sporcular.heading("Boy", text="BOY")
        self.tree_sporcular.heading("VKI", text="VKI")
        
        self.tree_sporcular.column("ID", width=60, anchor="center")
        self.tree_sporcular.column("Ad", width=250)
        self.tree_sporcular.column("Cinsiyet", width=120, anchor="center")
        self.tree_sporcular.column("Kilo", width=80, anchor="center")
        self.tree_sporcular.column("Boy", width=80, anchor="center")
        self.tree_sporcular.column("VKI", width=100, anchor="center")
        self.tree_sporcular.pack(fill="both", expand=True, side="left")
        
        sb1 = ctk.CTkScrollbar(tree1_frame, command=self.tree_sporcular.yview)
        sb1.pack(side="right", fill="y")
        self.tree_sporcular.configure(yscrollcommand=sb1.set)

        tree2_frame = ctk.CTkFrame(self.tabview.tab("Antrenmanlar"), fg_color="transparent")
        tree2_frame.pack(fill="both", expand=True, padx=15, pady=15)

        self.tree_antrenman = ttk.Treeview(tree2_frame, columns=("ID", "Ad", "Tur", "Sure", "Kalori", "Tarih"), show="headings")
        self.tree_antrenman.heading("ID", text="ID")
        self.tree_antrenman.heading("Ad", text="AD SOYAD")
        self.tree_antrenman.heading("Tur", text="BRANŞ")
        self.tree_antrenman.heading("Sure", text="SÜRE")
        self.tree_antrenman.heading("Kalori", text="KALORİ")
        self.tree_antrenman.heading("Tarih", text="TARİH")
        
        self.tree_antrenman.column("ID", width=100, anchor="center")
        self.tree_antrenman.column("Ad", width=200)
        self.tree_antrenman.column("Tur", width=180)
        self.tree_antrenman.column("Sure", width=100, anchor="center")
        self.tree_antrenman.column("Kalori", width=100, anchor="center")
        self.tree_antrenman.column("Tarih", width=150, anchor="center")
        self.tree_antrenman.pack(fill="both", expand=True, side="left")

        sb2 = ctk.CTkScrollbar(tree2_frame, command=self.tree_antrenman.yview)
        sb2.pack(side="right", fill="y")
        self.tree_antrenman.configure(yscrollcommand=sb2.set)

        self.veritabani_verilerini_doldur()

    def veritabani_verilerini_doldur(self):
        conn = db_baglan()
        cursor = conn.cursor()
        for item in self.tree_sporcular.get_children(): self.tree_sporcular.delete(item)
        cursor.execute("SELECT id, ad, kilo, boy, cinsiyet FROM sporcular ORDER BY id ASC")
        for row in cursor.fetchall():
            s_id, s_ad, s_kilo, s_boy, s_cins = row
            vki = round(s_kilo / (s_boy ** 2), 2)
            self.tree_sporcular.insert("", "end", values=(s_id, s_ad, s_cins, f"{s_kilo:.1f} kg", f"{s_boy:.2f} m", vki))

        for item in self.tree_antrenman.get_children(): self.tree_antrenman.delete(item)
        cursor.execute('''SELECT s.id, s.ad, a.tur, a.sure, a.kalori, a.tarih 
            FROM antrenmanlar a JOIN sporcular s ON a.sporcu_id = s.id ORDER BY a.id DESC''')
        for row in cursor.fetchall():
            self.tree_antrenman.insert("", "end", values=(row[0], row[1], row[2], f"{row[3]:.1f}", f"{row[4]:.1f}", row[5]))
        conn.close()

    def yeni_profil_penceresi(self):
        self.modal = ctk.CTkToplevel(self.root)
        self.modal.title("Yeni Kayıt")
        self.modal.geometry("380x580")
        self.modal.configure(fg_color=BG_COLOR)
        
        self.modal.transient(self.root)
        self.modal.lift()
        self.modal.grab_set()

       
        ctk.CTkLabel(self.modal, text="Yeni Kayıt", font=(FONT_FAMILY, 16, "bold"), text_color=WHITE).pack(pady=(25, 20), padx=30, anchor="w")

        f = ctk.CTkFrame(self.modal, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=30)

        self.e_ad = ctk.CTkEntry(f, font=(FONT_FAMILY, 12), fg_color=ENTRY_BG, text_color=TEXT_MAIN, border_color=CARD_BG, border_width=1, corner_radius=10, placeholder_text="Ad")
        self.e_ad.pack(fill="x", ipady=6, pady=(0, 15))

        self.e_soyad = ctk.CTkEntry(f, font=(FONT_FAMILY, 12), fg_color=ENTRY_BG, text_color=TEXT_MAIN, border_color=CARD_BG, border_width=1, corner_radius=10, placeholder_text="Soyad")
        self.e_soyad.pack(fill="x", ipady=6, pady=(0, 15))
        
       
        self.cb_cinsiyet = ctk.CTkComboBox(f, values=["Erkek", "Kadın", "Belirtmek İstemiyorum"], state="readonly", font=(FONT_FAMILY, 12), 
                                           fg_color=ENTRY_BG, text_color=TEXT_MAIN, border_color=CARD_BG, button_color=CARD_BG, 
                                           button_hover_color=TEXT_SUB, corner_radius=10)
        self.cb_cinsiyet.pack(fill="x", pady=(0, 15))
        self.cb_cinsiyet.set("Cinsiyet Seçin") 

        col_frame = ctk.CTkFrame(f, fg_color="transparent")
        col_frame.pack(fill="x", pady=(0, 25))
        
        self.e_kilo = ctk.CTkEntry(col_frame, width=150, font=(FONT_FAMILY, 12), fg_color=ENTRY_BG, text_color=TEXT_MAIN, border_color=CARD_BG, border_width=1, corner_radius=10, placeholder_text="Kilo (kg)")
        self.e_kilo.pack(side="left", padx=(0, 5))

        self.e_boy = ctk.CTkEntry(col_frame, width=150, font=(FONT_FAMILY, 12), fg_color=ENTRY_BG, text_color=TEXT_MAIN, border_color=CARD_BG, border_width=1, corner_radius=10, placeholder_text="Boy (Örn: 1.80)")
        self.e_boy.pack(side="right", padx=(5, 0))

        self.btn_profil_kaydet = ctk.CTkButton(f, text="Oluştur", font=(FONT_FAMILY, 13, "bold"), fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, text_color=WHITE, corner_radius=20, command=self.yeni_profil_kaydet)
        self.btn_profil_kaydet.pack(fill="x", pady=20)

    def yeni_profil_kaydet(self):
        ad = self.e_ad.get().strip().title()
        soyad = self.e_soyad.get().strip().title()
        cinsiyet = self.cb_cinsiyet.get()
        if len(ad) < 2 or len(soyad) < 2 or cinsiyet == "Cinsiyet Seçin":
            messagebox.showwarning("Eksik Veri", "Lütfen tüm bilgileri giriniz.")
            return
        if not self.e_kilo.get() or not self.e_boy.get():
            messagebox.showwarning("Eksik Veri", "Lütfen fiziksel değerleri giriniz.")
            return

        tam_ad = f"{ad} {soyad}"
        try:
            kilo = float(self.e_kilo.get())
            boy = float(self.e_boy.get())
            if any(c.isdigit() for c in tam_ad): raise ValueError("İsim Hatası")
            if not (30 <= kilo <= 250) or not (0.5 <= boy <= 2.5): raise ValueError("Limit Hatası")
            
            conn = db_baglan()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sporcular (ad, kilo, boy, cinsiyet) VALUES (?, ?, ?, ?)", (tam_ad, kilo, boy, cinsiyet))
            yeni_id = cursor.lastrowid
            
            cursor.execute("INSERT INTO kilo_gecmisi (sporcu_id, kilo, tarih) VALUES (?, ?, ?)", (yeni_id, kilo, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            
            self.combo_listesini_guncelle()
            self.cb_profil.set(f"{yeni_id} - {tam_ad}")
            self.aktif_sporcu = Sporcu(yeni_id, tam_ad, kilo, boy, cinsiyet)
            self.ekrani_yenile()
            self.modal.destroy()
        except ValueError as e:
            if str(e) == "İsim Hatası": messagebox.showwarning("Geçersiz Format", "İsim veya soyisim alanlarında sayı bulunamaz.")
            else: messagebox.showwarning("Geçersiz Format", "Boy ve kilo alanları hatalı formatta girildi. Lütfen sayısal değerler kullanın (Örn. Boy: 1.80).")

    def profil_guncelle_penceresi(self):
        if not self.aktif_sporcu: return
        self.modal_g = ctk.CTkToplevel(self.root)
        self.modal_g.title("Güncelle")
        self.modal_g.geometry("380x420")
        self.modal_g.configure(fg_color=BG_COLOR)
        
        self.modal_g.transient(self.root)
        self.modal_g.lift()
        self.modal_g.grab_set()

        
        ctk.CTkLabel(self.modal_g, text="Profili Güncelle", font=(FONT_FAMILY, 16, "bold"), text_color=WHITE).pack(pady=(25, 20), padx=30, anchor="w")

        f = ctk.CTkFrame(self.modal_g, fg_color="transparent")
        f.pack(fill="both", expand=True, padx=30)

        ctk.CTkLabel(f, text="Kilo (kg)", font=(FONT_FAMILY, 11), text_color=WHITE).pack(anchor="w")
        self.e_guncel_kilo = ctk.CTkEntry(f, font=(FONT_FAMILY, 12), fg_color=ENTRY_BG, text_color=TEXT_MAIN, border_color=CARD_BG, border_width=1, corner_radius=10)
        self.e_guncel_kilo.pack(fill="x", ipady=6, pady=(5, 15))
        self.e_guncel_kilo.insert(0, str(self.aktif_sporcu.kilo)) 

        ctk.CTkLabel(f, text="Boy (m)", font=(FONT_FAMILY, 11), text_color=WHITE).pack(anchor="w")
        self.e_guncel_boy = ctk.CTkEntry(f, font=(FONT_FAMILY, 12), fg_color=ENTRY_BG, text_color=TEXT_MAIN, border_color=CARD_BG, border_width=1, corner_radius=10)
        self.e_guncel_boy.pack(fill="x", ipady=6, pady=(5, 15))
        self.e_guncel_boy.insert(0, str(self.aktif_sporcu.boy)) 
        
        
        self.cb_guncel_cinsiyet = ctk.CTkComboBox(f, values=["Erkek", "Kadın", "Belirtmek İstemiyorum"], state="readonly", font=(FONT_FAMILY, 12), 
                                                  fg_color=ENTRY_BG, text_color=TEXT_MAIN, border_color=CARD_BG, button_color=CARD_BG, 
                                                  button_hover_color=TEXT_SUB, corner_radius=10)
        self.cb_guncel_cinsiyet.pack(fill="x", pady=(5, 25))
        self.cb_guncel_cinsiyet.set(self.aktif_sporcu.cinsiyet)

        self.btn_kaydet = ctk.CTkButton(f, text="Güncelle", font=(FONT_FAMILY, 12, "bold"), fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER, text_color=WHITE, corner_radius=20, command=self.profil_guncelle_kaydet)
        self.btn_kaydet.pack(fill="x", pady=20)

    def profil_guncelle_kaydet(self):
        try:
            yeni_kilo = float(self.e_guncel_kilo.get())
            yeni_boy = float(self.e_guncel_boy.get())
            yeni_cinsiyet = self.cb_guncel_cinsiyet.get()
            if not (30 <= yeni_kilo <= 250) or not (0.5 <= yeni_boy <= 2.5): raise ValueError("Geçersiz")
            
            conn = db_baglan()
            cursor = conn.cursor()
            cursor.execute("UPDATE sporcular SET kilo = ?, boy = ?, cinsiyet = ? WHERE id = ?", (yeni_kilo, yeni_boy, yeni_cinsiyet, self.aktif_sporcu.id))
            cursor.execute("INSERT INTO kilo_gecmisi (sporcu_id, kilo, tarih) VALUES (?, ?, ?)", (self.aktif_sporcu.id, yeni_kilo, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            conn.close()
            
            self.aktif_sporcu.kilo, self.aktif_sporcu.boy, self.aktif_sporcu.cinsiyet = yeni_kilo, yeni_boy, yeni_cinsiyet
            self.ekrani_yenile()
            self.modal_g.destroy()
        except ValueError: messagebox.showwarning("Geçersiz Format", "Lütfen sayısal boy ve kilo formatı kullanınız.")

    def profili_sil(self):
        if not self.aktif_sporcu: return
        if messagebox.askyesno("Kalıcı İşlem Onayı", f"{self.aktif_sporcu.ad} profilini ve ilişkili tüm aktivite geçmişini kalıcı olarak silmek istediğinize emin misiniz?"):
            conn = db_baglan()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM antrenmanlar WHERE sporcu_id = ?", (self.aktif_sporcu.id,))
            cursor.execute("DELETE FROM kilo_gecmisi WHERE sporcu_id = ?", (self.aktif_sporcu.id,))
            cursor.execute("DELETE FROM sporcular WHERE id = ?", (self.aktif_sporcu.id,))
            conn.commit()
            conn.close()
            self.aktif_sporcu = None
            self.combo_listesini_guncelle()

    def combo_listesini_guncelle(self):
        # Veritabanından çekilen tüm listeler yeniden Treeview ekranına yüklenmeden önce
        # temizlenir (.delete(item)) ki aynı veriler tekrar tekrar üst üste binmesin.
        conn = db_baglan()
        cursor = conn.cursor()
        cursor.execute("SELECT id, ad, kilo, boy, cinsiyet FROM sporcular")
        kayitlar = cursor.fetchall()
        conn.close()
        
        liste = [f"{k[0]} - {k[1]}" for k in kayitlar]
        self.cb_profil.configure(values=liste)
        
        if kayitlar:
            if not self.aktif_sporcu or not any(str(self.aktif_sporcu.id) in s for s in liste):
                self.cb_profil.set(liste[0])
                ilk = kayitlar[0]
                self.aktif_sporcu = Sporcu(ilk[0], ilk[1], ilk[2], ilk[3], ilk[4])
        else:
            self.cb_profil.set("Sporcu Bulunamadı")
            self.aktif_sporcu = None
        self.ekrani_yenile()

    def profil_degistir_event(self, event):
        secim = self.cb_profil.get()
        if secim == "Sporcu Bulunamadı": return
        secili_id = int(secim.split(" - ")[0])
        conn = db_baglan()
        cursor = conn.cursor()
        cursor.execute("SELECT id, ad, kilo, boy, cinsiyet FROM sporcular WHERE id = ?", (secili_id,))
        kayit = cursor.fetchone()
        conn.close()
        if kayit:
            self.aktif_sporcu = Sporcu(kayit[0], kayit[1], kayit[2], kayit[3], kayit[4])
            self.ekrani_yenile()

    def ekrani_yenile(self):
        for item in self.tablo.get_children(): self.tablo.delete(item)
        
        if not self.aktif_sporcu: 
            self.lbl_ad.configure(text="Ad Soyad: -")
            self.lbl_cinsiyet.configure(text="Cinsiyet: -")
            self.lbl_kilo.configure(text="Kilo: -")
            self.lbl_boy.configure(text="Boy: -")
            self.lbl_vki.configure(text="-", text_color=TEXT_MAIN)
            self.lbl_vki_durum.configure(text="Durum: -", text_color=TEXT_MAIN)
            self.lbl_vki_mesaj.configure(text="")
            return
        
        self.lbl_ad.configure(text=self.aktif_sporcu.ad)
        self.lbl_cinsiyet.configure(text=f"Cinsiyet: {self.aktif_sporcu.cinsiyet}")
        self.lbl_kilo.configure(text=f"Kilo: {self.aktif_sporcu.kilo:.1f} kg")
        self.lbl_boy.configure(text=f"Boy: {self.aktif_sporcu.boy:.2f} m")
        
        vki = self.aktif_sporcu.vki_hesapla()
        
        if vki < 18.5:
            dur, rnk, msj = "Zayıf", COLOR_ZAYIF, random.choice(ZAYIF_MESAJLAR) 
        elif 18.5 <= vki < 25.0:
            dur, rnk, msj = "Normal", COLOR_NORMAL, random.choice(NORMAL_MESAJLAR) 
        elif 25.0 <= vki < 30.0:
            dur, rnk, msj = "Fazla Kilolu", COLOR_FAZLA, random.choice(KILOLU_MESAJLAR) 
        else:
            dur, rnk, msj = "Obez", COLOR_OBEZ, random.choice(OBEZ_MESAJLAR) 
            
        aktif_renk = rnk[0] if ctk.get_appearance_mode() == "Light" else rnk[1]
            
        self.lbl_vki.configure(text=f"{vki}", text_color=aktif_renk) 
        self.lbl_vki_durum.configure(text=dur, text_color=aktif_renk)
        self.lbl_vki_mesaj.configure(text=msj)

        conn = db_baglan()
        cursor = conn.cursor()
        cursor.execute("SELECT tur, sure, kalori, tarih FROM antrenmanlar WHERE sporcu_id = ? ORDER BY id DESC", (self.aktif_sporcu.id,))
        for kayit in cursor.fetchall():
            self.tablo.insert("", "end", values=(kayit[0], f"{int(kayit[1])} dk", f"{int(kayit[2])} kcal", kayit[3]))
        conn.close()

    def antrenman_kaydet(self):
        # MET algoritması sayesinde kullanıcının sadece antrenman süresini girmesi yeterlidir.
        # Yakılan kalori arka planda otomatik olarak hesaplanır. (Formül: MET * Kilo * Saat)
        if not self.aktif_sporcu: return messagebox.showwarning("Uyarı", "Lütfen geçerli bir profil seçin.")
        try:
            if not self.ent_sure.get(): raise ValueError("Eksik")
            sure = float(self.ent_sure.get())
            tur = self.cb_spor.get()
            
            if sure <= 0 or sure > 1440: raise ValueError("Limit")
            
            met = MET_DEGERLERI.get(tur, 5.0) 
            hesaplanan_kalori = round(met * self.aktif_sporcu.kilo * (sure / 60.0), 1)
            
            conn = db_baglan()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO antrenmanlar (sporcu_id, tur, sure, kalori, tarih) VALUES (?, ?, ?, ?, ?)", 
                           (self.aktif_sporcu.id, tur, sure, hesaplanan_kalori, datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            conn.close()
            
            self.ent_sure.delete(0, tk.END); self.ent_sure.configure(placeholder_text="Örn: 45")
            self.ekrani_yenile()
        except ValueError as e:
            if str(e) == "Limit": messagebox.showerror("İşlem Başarısız", "Girilen değerler mantıksal sınırların dışındadır. (Maks süre: 24 saat)")
            else: messagebox.showerror("Giriş Hatası", "Lütfen süre alanını yalnızca sayısal değerlerle doldurunuz.")

if __name__ == "__main__":
    veritabanini_kur()
    root = ctk.CTk() 
    app = FitTrackApp(root)
    root.mainloop()