import requests
import re
import time
import urllib3
import warnings
import os

# Uyarıları kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

class UltimateM3UGenerator:
    def __init__(self):
        self.m3u_content = "#EXTM3U\n"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0 Safari/537.36'
        })
        self.total_channels = 0

    def get_html(self, url):
        try:
            response = self.session.get(url, timeout=20, verify=False)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"URL hatası: {str(e)[:100]}...")
            return None

    def selcuksports_streams(self):
        """VERDİĞİNİZ PROXY'LER İLE SELCUKSPORTS"""
        print("🔄 Selcuksports kanalları alınıyor...")
        
        # VERDİĞİNİZ PROXY LİSTESİ
        proxies = [
            "https://rapid-wave-c8e3.redfor14314.workers.dev/",
            "https://proxy.ponelat.workers.dev/",
            "https://proxy.freecdn.workers.dev/?url=",
            "https://withered-shape-3305.vadimkantorov.workers.dev/?",
            "https://wandering-sky-a896.cbracketdash.workers.dev/?",
            "https://hello-world-aged-resonance-fc8f.bokaflix.workers.dev/?apiUrl=",
            "https://cors.gerhut.workers.dev/?"
        ]
        
        original_url = "https://www.selcuksportshd.is/"
        
        channel_ids = [
            "selcukbeinsports1", "selcukbeinsports2", "selcukbeinsports3",
            "selcukbeinsports4", "selcukbeinsports5", "selcukbeinsportsmax1",
            "selcukbeinsportsmax2", "selcukssport", "selcukssport2",
            "selcuksmartspor", "selcuksmartspor2", "selcuktivibuspor1",
            "selcuktivibuspor2", "selcuktivibuspor3", "selcuktivibuspor4",
            "sssplus1", "sssplus2", "selcukobs1", 
            "selcuktabiispor1", "selcuktabiispor2", 
            "selcuktabiispor3", "selcuktabiispor4", 
            "selcuktabiispor5"
        ]
        
        html = None
        used_proxy = ""
        
        # TÜM PROXY'LERİ DENEYELİM
        for proxy in proxies:
            if "?url=" in proxy or "?apiUrl=" in proxy or proxy.endswith("?"):
                # Query parametreli proxy'ler
                test_url = proxy + original_url
            else:
                # Normal proxy'ler
                test_url = proxy + original_url
                
            print(f"🔗 Proxy deneniyor: {proxy[:50]}...")
            html = self.get_html(test_url)
            if html:
                used_proxy = proxy
                print(f"✅ Proxy başarılı: {proxy[:50]}...")
                break
            time.sleep(1)
        
        if not html:
            print("❌ Selcuksports: Tüm proxy'lere erişilemiyor")
            return 0
        
        active_domain = ""
        
        # ORJİNAL REGEX PATTERN'LER
        section_match = re.search(r'data-device-mobile[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
        if section_match:
            link_match = re.search(r'href=["\'](https?://[^"\']*selcuksportshd[^"\']+)["\']', section_match.group(1))
            if link_match:
                active_domain = link_match.group(1)
        
        if not active_domain:
            # ALTERNATİF ARAMA
            link_match = re.search(r'href=["\'](https?://[^"\']*selcuksportshd[^"\']+)["\']', html)
            if link_match:
                active_domain = link_match.group(1)
        
        if not active_domain:
            active_domain = original_url
        
        print(f"🌐 Aktif domain: {active_domain}")
        
        # AKTİV DOMAİN'E PROXY UYGULA
        if used_proxy:
            if "?url=" in used_proxy or "?apiUrl=" in used_proxy or used_proxy.endswith("?"):
                domain_to_fetch = used_proxy + active_domain
            else:
                domain_to_fetch = used_proxy + active_domain
        else:
            domain_to_fetch = active_domain
            
        print(f"🔗 Fetch edilecek: {domain_to_fetch[:80]}...")
        
        domain_html = self.get_html(domain_to_fetch)
        if not domain_html:
            print("❌ Selcuksports: Domain sayfası erişilemiyor")
            return 0
        
        player_links = re.findall(r'data-url="(https?://[^"]+id=[^"]+)"', domain_html)
        
        if not player_links:
            # ALTERNATİF PATTERN
            player_links = re.findall(r'data-url=["\'](https?://[^"\'?]+?id=[^"\'&]+)["\']', domain_html)
        
        if not player_links:
            print("❌ Selcuksports: Player linkleri bulunamadı")
            return 0
        
        print(f"🔗 Bulunan player linkleri: {len(player_links)}")
        
        found_channels = 0
        base_stream_url = None
        
        for player_url in player_links:
            print(f"🔍 Player URL deneniyor: {player_url[:50]}...")
            
            # PLAYER URL'YE PROXY UYGULA
            if used_proxy:
                if "?url=" in used_proxy or "?apiUrl=" in used_proxy or used_proxy.endswith("?"):
                    player_url_to_fetch = used_proxy + player_url
                else:
                    player_url_to_fetch = used_proxy + player_url
            else:
                player_url_to_fetch = player_url
                
            html_player = self.get_html(player_url_to_fetch)
            if html_player:
                stream_match = re.search(r'this\.baseStreamUrl\s*=\s*[\'"](https://[^\'"]+)[\'"]', html_player)
                if stream_match:
                    base_stream_url = stream_match.group(1)
                    print(f"✅ Base stream URL bulundu: {base_stream_url[:50]}...")
                    break
        
        if not base_stream_url:
            print("❌ Selcuksports: Base stream URL bulunamadı")
            return 0
        
        # KANALLARI EKLE
        for cid in channel_ids:
            stream_url = base_stream_url + cid + "/playlist.m3u8"
            
            clean_name = re.sub(r'^selcuk', '', cid, flags=re.IGNORECASE)
            clean_name = clean_name.upper() + " HD"
            channel_name = "TR:" + clean_name
            
            self.m3u_content += f'#EXTINF:-1 tvg-id="" tvg-name="{channel_name}" tvg-logo="https://i.hizliresim.com/b6xqz10.jpg" group-title="SELCUKSPORTS",{channel_name}\n'
            self.m3u_content += f'#EXTVLCOPT:http-referrer={active_domain}\n'
            self.m3u_content += f'{stream_url}\n'
            
            found_channels += 1
            print(f"✅ {channel_name}")
        
        print(f"📊 Selcuksports: {found_channels} kanal eklendi")
        return found_channels

    def deathless_streams(self):
        print("🔄 DeaTHLesS kanalları alınıyor...")
        
        active_domain = None
        for i in range(42, 200):
            url = f"https://birazcikspor{i}.xyz/"
            try:
                response = requests.head(url, timeout=5)
                if response.status_code == 200:
                    active_domain = url
                    break
            except:
                continue
        
        if not active_domain:
            print("❌ DeaTHLesS: Aktif domain bulunamadı")
            return 0
        
        try:
            response = requests.get(active_domain, timeout=10)
            html = response.text
        except:
            print("❌ DeaTHLesS: Ana sayfa erişilemiyor")
            return 0
        
        first_id_match = re.search(r'<iframe[^>]+id="matchPlayer"[^>]+src="event\.html\?id=([^"]+)"', html)
        first_id = first_id_match.group(1) if first_id_match else None
        
        base_url = ""
        if first_id:
            try:
                event_response = requests.get(f"{active_domain}event.html?id={first_id}", timeout=10)
                event_source = event_response.text
                base_url_match = re.search(r'var\s+baseurls\s*=\s*\[\s*"([^"]+)"', event_source)
                base_url = base_url_match.group(1) if base_url_match else ""
            except:
                pass
        
        if not base_url:
            print("❌ DeaTHLesS: Base URL bulunamadı")
            return 0
        
        channels = [
            ["beIN Sport 1 HD", "androstreamlivebs1", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["beIN Sport 2 HD", "androstreamlivebs2", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["beIN Sport 3 HD", "androstreamlivebs3", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["beIN Sport 4 HD", "androstreamlivebs4", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["beIN Sport 5 HD", "androstreamlivebs5", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["beIN Sport Max 1 HD", "androstreamlivebsm1", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["beIN Sport Max 2 HD", "androstreamlivebsm2", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["S Sport 1 HD", "androstreamlivess1", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["S Sport 2 HD", "androstreamlivess2", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tivibu Sport HD", "androstreamlivets", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tivibu Sport 1 HD", "androstreamlivets1", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tivibu Sport 2 HD", "androstreamlivets2", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tivibu Sport 3 HD", "androstreamlivets3", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tivibu Sport 4 HD", "androstreamlivets4", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Smart Sport 1 HD", "androstreamlivesm1", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Smart Sport 2 HD", "androstreamlivesm2", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Euro Sport 1 HD", "androstreamlivees1", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Euro Sport 2 HD", "androstreamlivees2", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tabii HD", "androstreamlivetb", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tabii 1 HD", "androstreamlivetb1", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tabii 2 HD", "androstreamlivetb2", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tabii 3 HD", "androstreamlivetb3", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tabii 4 HD", "androstreamlivetb4", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tabii 5 HD", "androstreamlivetb5", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tabii 6 HD", "androstreamlivetb6", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tabii 7 HD", "androstreamlivetb7", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Tabii 8 HD", "androstreamlivetb8", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Exxen HD", "androstreamliveexn", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Exxen 1 HD", "androstreamliveexn1", "https://i.hizliresim.com/8xzjgqv.jpg"],
        ]
        
        successful_channels = 0
        
        for channel in channels:
            stream_url = f"{base_url}{channel[1]}.m3u8"
            try:
                response = requests.head(stream_url, timeout=5)
                if response.status_code == 200:
                    self.m3u_content += f'#EXTINF:-1 tvg-id="sport.tr" tvg-name="TR:{channel[0]}" tvg-logo="{channel[2]}" group-title="DEATHLESS",TR:{channel[0]}\n'
                    self.m3u_content += f"{stream_url}\n"
                    successful_channels += 1
                    print(f"✅ {channel[0]}")
                else:
                    print(f"❌ {channel[0]}")
            except:
                print(f"❌ {channel[0]}")
        
        print(f"📊 DeaTHLesS: {successful_channels} kanal eklendi")
        return successful_channels

    def bilyoner_streams(self):
        print("🔄 Bilyoner kanalları alınıyor...")
        
        aktif_domain = None
        for i in range(1, 200):
            domain = f'https://bilyonersport{i}.com/'
            try:
                r = requests.get(domain, timeout=3)
                if r.status_code == 200 and "channel-list" in r.text:
                    print(f'🌐 Aktif domain bulundu: {domain}')
                    aktif_domain = domain
                    break
            except:
                pass
        
        if not aktif_domain:
            print("❌ Bilyoner: Aktif domain bulunamadı")
            return 0
        
        try:
            r = requests.get(aktif_domain, timeout=5)
            html = r.text
            hrefs = re.findall(r'href="(.*?index\.m3u8.*?)"', html)
            names = re.findall(r'<div class="channel-name">(.*?)</div>', html)
            
            if not hrefs or not names:
                print("❌ Bilyoner: Kanal bulunamadı")
                return 0
            
            kanallar = []
            for name, link in zip(names, hrefs):
                kanallar.append((name.strip(), link.strip()))
            
            successful_channels = 0
            for name, url in kanallar:
                self.m3u_content += f'#EXTINF:-1 tvg-name="{name}" group-title="BILYONER",{name}\n'
                self.m3u_content += f'#EXTVLCOPT:http-referrer={aktif_domain}\n'
                self.m3u_content += f"{url}\n\n"
                successful_channels += 1
                print(f"✅ {name}")
            
            print(f"📊 Bilyoner: {successful_channels} kanal eklendi")
            return successful_channels
            
        except Exception as e:
            print(f"❌ Bilyoner hatası: {e}")
            return 0

    def save_m3u(self, filename="ultimate_streams.m3u"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.m3u_content)
            print(f"💾 M3U dosyası kaydedildi: {filename}")
            print(f"📈 Toplam kanal sayısı: {self.total_channels}")
            return True
        except Exception as e:
            print(f"❌ Kaydetme hatası: {str(e)}")
            return False

def main():
    print("🎯 ULTIMATE M3U GENERATOR BAŞLATILIYOR...")
    print("=" * 60)
    
    generator = UltimateM3UGenerator()
    total_channels = 0
    
    # 1. Selcuksports - VERDİĞİNİZ PROXY'LER İLE
    print("\n1. SELCUKSPORTS")
    print("-" * 30)
    selcuk_count = generator.selcuksports_streams()
    total_channels += selcuk_count
    
    # 2. DeaTHLesS
    print("\n2. DEATHLESS")
    print("-" * 30)
    deathless_count = generator.deathless_streams()
    total_channels += deathless_count
    
    # 3. Bilyoner
    print("\n3. BILYONER")
    print("-" * 30)
    bilyoner_count = generator.bilyoner_streams()
    total_channels += bilyoner_count
    
    generator.total_channels = total_channels
    
    # Sonuç
    print("\n" + "=" * 60)
    print("📊 SONUÇLAR")
    print("-" * 30)
    print(f"Selcuksports: {selcuk_count} kanal")
    print(f"DeaTHLesS: {deathless_count} kanal")
    print(f"Bilyoner: {bilyoner_count} kanal")
    print(f"TOPLAM: {total_channels} kanal")
    
    # Kaydet
    print("\n💾 KAYDEDİLİYOR...")
    if generator.save_m3u("ultimate_streams.m3u"):
        print(f"\n🎉 TAMAMLANDI!")
        print(f"📁 Çıktı: ultimate_streams.m3u")
        print(f"📺 Toplam {total_channels} kanal eklendi")
    else:
        print("❌ Kayıt başarısız!")

if __name__ == "__main__":
    main()
