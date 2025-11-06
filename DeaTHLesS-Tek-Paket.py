import requests
import re
import time
import urllib3
import warnings
import os
from datetime import datetime

# Uyarıları kapat
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

class UltimateM3UGenerator:
    def __init__(self):
        self.m3u_content = "#EXTM3U\n"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.total_channels = 0
        self.failed_channels = []

    def debug_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")

    def get_html(self, url, timeout=20):
        try:
            self.debug_log(f"GET: {url[:80]}...")
            response = self.session.get(url, timeout=timeout, verify=False)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.debug_log(f"❌ URL hatası: {str(e)[:100]}")
            return None

    def check_stream(self, url, channel_name=""):
        """Stream URL kontrolü - daha toleranslı"""
        try:
            # Sadece bağlantıyı kontrol et, içeriği indirme
            response = self.session.head(url, timeout=8, verify=False, allow_redirects=True)
            if response.status_code in [200, 302, 301]:
                return True
            return False
        except:
            try:
                # HEAD başarısız olursa GET dene
                response = self.session.get(url, timeout=5, verify=False, stream=True)
                return response.status_code == 200
            except:
                self.failed_channels.append(channel_name)
                return False

    def selcuksports_streams(self):
        """Selcuksports kanalları - geliştirilmiş versiyon"""
        print("🔄 Selcuksports kanalları alınıyor...")
        
        proxies = [
            "https://proxy.ponelat.workers.dev/",
            "https://withered-shape-3305.vadimkantorov.workers.dev/?",
            "https://cors.gerhut.workers.dev/?",
            "https://corsproxy.io/?",
            ""  # Doğrudan erişim
        ]
        
        original_url = "https://www.selcuksportshd.is/"
        html = None
        
        for proxy in proxies:
            if proxy:
                test_url = proxy + original_url
            else:
                test_url = original_url
                
            self.debug_log(f"🔗 Proxy deneniyor: {proxy[:30]}...")
            html = self.get_html(test_url, timeout=15)
            if html:
                self.debug_log("✅ Proxy başarılı")
                break
            time.sleep(1)
        
        if not html:
            self.debug_log("❌ Tüm proxy'ler başarısız")
            return 0

        # Domain bulma
        domain_patterns = [
            r'href=["\'](https?://[^"\']*selcuksportshd[^"\']+)["\']',
            r'data-url=["\'](https?://[^"\']+)["\']',
            r'src=["\'](https?://[^"\']*selcuksportshd[^"\']+)["\']'
        ]
        
        active_domain = original_url
        for pattern in domain_patterns:
            match = re.search(pattern, html)
            if match:
                active_domain = match.group(1)
                self.debug_log(f"🌐 Domain bulundu: {active_domain}")
                break

        # Player linklerini bul
        player_patterns = [
            r'data-url="(https?://[^"]+id=[^"]+)"',
            r'player-url=["\'](https?://[^"\']+id=[^"\']+)["\']',
            r'stream-url=["\'](https?://[^"\']+id=[^"\']+)["\']'
        ]
        
        player_links = []
        for pattern in player_patterns:
            player_links = re.findall(pattern, html)
            if player_links:
                break
        
        self.debug_log(f"🔗 {len(player_links)} player link bulundu")
        
        base_stream_url = None
        for player_url in player_links[:3]:  # İlk 3'ü dene
            if not player_url.startswith('http'):
                player_url = active_domain + player_url
                
            self.debug_log(f"🔍 Player test: {player_url[:60]}...")
            player_html = self.get_html(player_url, timeout=10)
            if player_html:
                stream_match = re.search(r'this\.baseStreamUrl\s*=\s*[\'"](https://[^\'"]+)[\'"]', player_html)
                if stream_match:
                    base_stream_url = stream_match.group(1)
                    self.debug_log(f"✅ Base stream: {base_stream_url[:50]}...")
                    break
        
        if not base_stream_url:
            self.debug_log("❌ Base stream bulunamadı")
            return 0

        # Kanal listesi - tüm olası kanallar
        channel_ids = [
            "selcukbeinsports1", "selcukbeinsports2", "selcukbeinsports3",
            "selcukbeinsports4", "selcukbeinsports5", "selcukbeinsportsmax1", 
            "selcukbeinsportsmax2", "selcukssport", "selcukssport2",
            "selcuksmartspor", "selcuksmartspor2", "selcuktivibuspor1",
            "selcuktivibuspor2", "selcuktivibuspor3", "selcuktivibuspor4",
            "sssplus1", "sssplus2", "selcukobs1", 
            "selcuktabiispor1", "selcuktabiispor2", "selcuktabiispor3", 
            "selcuktabiispor4", "selcuktabiispor5", "selcukexxen1"
        ]
        
        found_channels = 0
        for cid in channel_ids:
            stream_url = f"{base_stream_url}{cid}/playlist.m3u8"
            clean_name = re.sub(r'^selcuk', '', cid).upper() + " HD"
            channel_name = f"TR:{clean_name}"
            
            # Stream kontrolü - daha hızlı ve toleranslı
            if self.check_stream(stream_url, channel_name):
                self.m3u_content += f'#EXTINF:-1 tvg-id="" tvg-name="{channel_name}" tvg-logo="https://i.hizliresim.com/b6xqz10.jpg" group-title="SELCUKSPORTS",{channel_name}\n'
                self.m3u_content += f'#EXTVLCOPT:http-referrer={active_domain}\n'
                self.m3u_content += f'{stream_url}\n'
                found_channels += 1
                self.debug_log(f"✅ {channel_name}")
            else:
                self.debug_log(f"❌ {channel_name} - Stream çalışmıyor")
        
        print(f"📊 Selcuksports: {found_channels}/{len(channel_ids)} kanal eklendi")
        return found_channels

    def deathless_streams(self):
        """DeaTHLesS kanalları - geliştirilmiş versiyon"""
        print("🔄 DeaTHLesS kanalları alınıyor...")
        
        # Domain bulma - daha hızlı
        domains = [f"https://birazcikspor{i}.xyz/" for i in range(42, 60)]
        domains.extend([f"https://deathless{i}.com/" for i in range(1, 10)])
        
        active_domain = None
        for domain in domains:
            try:
                response = requests.head(domain, timeout=3)
                if response.status_code == 200:
                    active_domain = domain
                    self.debug_log(f"✅ Aktif domain: {domain}")
                    break
            except:
                continue
        
        if not active_domain:
            self.debug_log("❌ Aktif domain bulunamadı")
            return 0
        
        try:
            html = self.get_html(active_domain, timeout=10)
            if not html:
                return 0
        except Exception as e:
            self.debug_log(f"❌ Ana sayfa hatası: {e}")
            return 0

        # Base URL bulma - birden fazla yöntem
        base_url = ""
        
        # Yöntem 1: iframe içinden
        iframe_match = re.search(r'src="event\.html\?id=([^"]+)"', html)
        if iframe_match:
            event_id = iframe_match.group(1)
            try:
                event_url = f"{active_domain}event.html?id={event_id}"
                event_html = self.get_html(event_url, timeout=8)
                if event_html:
                    url_match = re.search(r'baseurls\s*=\s*\[\s*"([^"]+)"', event_html)
                    if url_match:
                        base_url = url_match.group(1)
            except:
                pass
        
        # Yöntem 2: Script tag'lerinden
        if not base_url:
            script_matches = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
            for script in script_matches:
                url_match = re.search(r'baseurls?[\s=:]+["\']([^"\']+)["\']', script)
                if url_match:
                    base_url = url_match.group(1)
                    break
        
        if not base_url:
            self.debug_log("❌ Base URL bulunamadı")
            return 0
        
        self.debug_log(f"✅ Base URL: {base_url[:60]}...")
        
        # Kanal listesi - tüm kanallar
        channels = [
            ["beIN Sport 1 HD", "androstreamlivebs1"],
            ["beIN Sport 2 HD", "androstreamlivebs2"],
            ["beIN Sport 3 HD", "androstreamlivebs3"],
            ["beIN Sport 4 HD", "androstreamlivebs4"],
            ["beIN Sport 5 HD", "androstreamlivebs5"],
            ["beIN Sport Max 1 HD", "androstreamlivebsm1"],
            ["beIN Sport Max 2 HD", "androstreamlivebsm2"],
            ["S Sport 1 HD", "androstreamlivess1"],
            ["S Sport 2 HD", "androstreamlivess2"],
            ["Tivibu Sport HD", "androstreamlivets"],
            ["Tivibu Sport 1 HD", "androstreamlivets1"],
            ["Tivibu Sport 2 HD", "androstreamlivets2"],
            ["Tivibu Sport 3 HD", "androstreamlivets3"],
            ["Tivibu Sport 4 HD", "androstreamlivets4"],
            ["Smart Sport 1 HD", "androstreamlivesm1"],
            ["Smart Sport 2 HD", "androstreamlivesm2"],
            ["Euro Sport 1 HD", "androstreamlivees1"],
            ["Euro Sport 2 HD", "androstreamlivees2"],
            ["Tabii HD", "androstreamlivetb"],
            ["Tabii 1 HD", "androstreamlivetb1"],
            ["Tabii 2 HD", "androstreamlivetb2"],
            ["Tabii 3 HD", "androstreamlivetb3"],
            ["Tabii 4 HD", "androstreamlivetb4"],
            ["Tabii 5 HD", "androstreamlivetb5"],
            ["Tabii 6 HD", "androstreamlivetb6"],
            ["Tabii 7 HD", "androstreamlivetb7"],
            ["Tabii 8 HD", "androstreamlivetb8"],
            ["Exxen HD", "androstreamliveexn"],
            ["Exxen 1 HD", "androstreamliveexn1"],
        ]
        
        successful = 0
        for name, code in channels:
            stream_url = f"{base_url}{code}.m3u8"
            channel_name = f"TR:{name}"
            
            if self.check_stream(stream_url, channel_name):
                self.m3u_content += f'#EXTINF:-1 tvg-id="sport.tr" tvg-name="{channel_name}" tvg-logo="https://i.hizliresim.com/8xzjgqv.jpg" group-title="DEATHLESS",{channel_name}\n'
                self.m3u_content += f"{stream_url}\n"
                successful += 1
                self.debug_log(f"✅ {name}")
            else:
                self.debug_log(f"❌ {name}")
        
        print(f"📊 DeaTHLesS: {successful}/{len(channels)} kanal eklendi")
        return successful

    def bilyoner_streams(self):
        """Bilyoner kanalları - basitleştirilmiş"""
        print("🔄 Bilyoner kanalları alınıyor...")
        
        # Basitleştirilmiş domain bulma
        domains = [f'https://bilyonersport{i}.com/' for i in range(1, 20)]
        
        for domain in domains:
            try:
                response = requests.get(domain, timeout=5)
                if response.status_code == 200 and "channel-list" in response.text:
                    self.debug_log(f"✅ Bilyoner domain: {domain}")
                    return self._parse_bilyoner(domain)
            except:
                continue
        
        self.debug_log("❌ Bilyoner domain bulunamadı")
        return 0

    def _parse_bilyoner(self, domain):
        """Bilyoner parsing"""
        try:
            html = self.get_html(domain)
            if not html:
                return 0
            
            # Kanal isimleri ve linkleri
            names = re.findall(r'channel-name[^>]*>([^<]+)', html)
            links = re.findall(r'href="([^"]*index\.m3u8[^"]*)"', html)
            
            if not names or not links:
                self.debug_log("❌ Bilyoner: Kanal bulunamadı")
                return 0
            
            successful = 0
            for name, link in zip(names, links):
                if not link.startswith('http'):
                    link = domain + link
                
                channel_name = name.strip()
                if self.check_stream(link, channel_name):
                    self.m3u_content += f'#EXTINF:-1 tvg-name="{channel_name}" group-title="BILYONER",{channel_name}\n'
                    self.m3u_content += f'#EXTVLCOPT:http-referrer={domain}\n'
                    self.m3u_content += f"{link}\n"
                    successful += 1
                    self.debug_log(f"✅ {channel_name}")
                else:
                    self.debug_log(f"❌ {channel_name}")
            
            print(f"📊 Bilyoner: {successful} kanal eklendi")
            return successful
            
        except Exception as e:
            self.debug_log(f"❌ Bilyoner hatası: {e}")
            return 0

    def save_m3u(self, filename="DeaTHLesS-Tek-Paket.m3u"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.m3u_content)
            
            # Dosya istatistikleri
            line_count = len(self.m3u_content.split('\n'))
            extinf_count = self.m3u_content.count('#EXTINF')
            
            print(f"💾 M3U kaydedildi: {filename}")
            print(f"📊 Dosya istatistikleri:")
            print(f"   - Toplam satır: {line_count}")
            print(f"   - EXTINF entrileri: {extinf_count}")
            print(f"   - Başarısız kanallar: {len(self.failed_channels)}")
            
            if self.failed_channels:
                print(f"   - Başarısız kanal listesi: {', '.join(self.failed_channels)}")
            
            return True
        except Exception as e:
            print(f"❌ Kaydetme hatası: {e}")
            return False

def main():
    print("🎯 GELİŞTİRİLMİŞ M3U GENERATOR")
    print("=" * 50)
    
    start_time = time.time()
    generator = UltimateM3UGenerator()
    
    # Tüm kaynakları dene
    sources = [
        ("Selcuksports", generator.selcuksports_streams),
        ("DeaTHLesS", generator.deathless_streams),
        ("Bilyoner", generator.bilyoner_streams)
    ]
    
    results = {}
    for name, func in sources:
        print(f"\n{'='*20} {name} {'='*20}")
        try:
            results[name] = func()
            time.sleep(2)  # Kaynaklar arası bekleme
        except Exception as e:
            print(f"❌ {name} hatası: {e}")
            results[name] = 0
    
    # Sonuçlar
    total_time = time.time() - start_time
    print(f"\n{'='*50}")
    print("📊 FİNAL SONUÇLAR")
    print(f"{'='*50}")
    
    total_channels = 0
    for name, count in results.items():
        print(f"   {name}: {count} kanal")
        total_channels += count
    
    generator.total_channels = total_channels
    print(f"{'='*50}")
    print(f"   TOPLAM: {total_channels} kanal")
    print(f"   SÜRE: {total_time:.1f} saniye")
    print(f"{'='*50}")
    
    # Kaydet
    if generator.save_m3u():
        print("🎉 M3U başarıyla oluşturuldu!")
    else:
        print("❌ M3U oluşturulamadı!")

if __name__ == "__main__":
    main()
