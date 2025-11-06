import requests
import re
import time
import urllib3
import warnings
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

class DeaTHLesS_M3U_Generator:
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
        except Exception:
            return None
    
    def selcuksports_streams(self):
        print("🔍 Scanning Selcuksports...")
        
        url = "https://seep.eu.org/https://www.selcuksportshd.is/"
        
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
        
        html = self.get_html(url)
        if not html:
            print("❌ Selcuksports: Main page not available")
            return 0
        
        active_domain = ""
        
        section_match = re.search(r'data-device-mobile[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
        if section_match:
            link_match = re.search(r'href=["\'](https?://[^"\']*selcuksportshd[^"\']+)["\']', section_match.group(1))
            if link_match:
                active_domain = link_match.group(1)
        
        if not active_domain:
            print("❌ Selcuksports: Active domain not found")
            return 0
        
        print(f"✅ Selcuksports domain: {active_domain}")
        
        domain_html = self.get_html(active_domain)
        if not domain_html:
            print("❌ Selcuksports: Domain page not available")
            return 0
        
        player_links = re.findall(r'data-url="(https?://[^"]+id=[^"]+)"', domain_html)
        
        if not player_links:
            print("❌ Selcuksports: Player links not found")
            return 0
        
        found_channels = 0
        
        for player_url in player_links:
            html_player = self.get_html(player_url)
            if html_player:
                stream_match = re.search(r'this\.baseStreamUrl\s*=\s*[\'"](https://[^\'"]+)[\'"]', html_player)
                if stream_match:
                    base_stream_url = stream_match.group(1)
                    
                    for cid in channel_ids:
                        stream_url = base_stream_url + cid + "/playlist.m3u8"
                        
                        clean_name = re.sub(r'^selcuk', '', cid, flags=re.IGNORECASE)
                        clean_name = clean_name.upper() + " HD"
                        channel_name = "TR:" + clean_name
                        
                        self.m3u_content += f'#EXTINF:-1 tvg-id="" tvg-name="{channel_name}" tvg-logo="https://i.hizliresim.com/b6xqz10.jpg" group-title="TURKIYE",{channel_name}\n'
                        self.m3u_content += f'#EXTVLCOPT:http-referrer={active_domain}\n'
                        self.m3u_content += f'{stream_url}\n'
                        
                        found_channels += 1
                        print(f"✅ Selcuksports: {channel_name}")
                    
                    break
        
        print(f"📊 Selcuksports: {found_channels} channels added")
        return found_channels

    def birazcikspor_streams(self):
        print("\n🔍 Scanning Birazcikspor...")
        
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
            print("❌ Birazcikspor: No active domain found")
            return 0
        
        try:
            response = requests.get(active_domain, timeout=10)
            html = response.text
        except:
            print("❌ Birazcikspor: Main page not accessible")
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
            print("❌ Birazcikspor: Base URL not found")
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
            ["Exxen 2 HD", "androstreamliveexn2", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Exxen 3 HD", "androstreamliveexn3", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Exxen 4 HD", "androstreamliveexn4", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Exxen 5 HD", "androstreamliveexn5", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Exxen 6 HD", "androstreamliveexn6", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Exxen 7 HD", "androstreamliveexn7", "https://i.hizliresim.com/8xzjgqv.jpg"],
            ["Exxen 8 HD", "androstreamliveexn8", "https://i.hizliresim.com/8xzjgqv.jpg"],
        ]
        
        successful_channels = 0
        
        for channel in channels:
            stream_url = f"{base_url}{channel[1]}.m3u8"
            try:
                response = requests.head(stream_url, timeout=5)
                if response.status_code == 200:
                    self.m3u_content += f'#EXTINF:-1 tvg-id="sport.tr" tvg-name="TR:{channel[0]}" tvg-logo="{channel[2]}" group-title="TURKIYE DEATHLESS",TR:{channel[0]}\n'
                    self.m3u_content += f"{stream_url}\n"
                    successful_channels += 1
                    print(f"✅ Birazcikspor: {channel[0]}")
                else:
                    print(f"❌ Birazcikspor: {channel[0]}")
            except:
                print(f"❌ Birazcikspor: {channel[0]}")
        
        print(f"📊 Birazcikspor: {successful_channels} channels added")
        return successful_channels

    def bilyonersport_streams(self):
        print("\n🔍 Scanning Bilyonersport...")
        
        active_domain = None
        for i in range(1, 200):
            domain = f"https://bilyonersport{i}.com/"
            try:
                r = requests.get(domain, timeout=3)
                if r.status_code == 200 and "channel-list" in r.text:
                    active_domain = domain
                    break
            except:
                pass
        
        if not active_domain:
            print("❌ Bilyonersport: No active domain found")
            return 0
        
        print(f"✅ Bilyonersport domain: {active_domain}")
        
        try:
            r = requests.get(active_domain, timeout=5)
            html = r.text
        except:
            print("❌ Bilyonersport: Main page not accessible")
            return 0
        
        hrefs = re.findall(r'href="([^"]+index\.m3u8[^"]*)"', html)
        names = re.findall(r'<div class="channel-name">(.*?)</div>', html)

        if not hrefs or not names:
            print("❌ Bilyonersport: No channels found")
            return 0

        successful_channels = 0
        for name, link in zip(names, hrefs):
            clean_name = name.strip()
            clean_link = link.strip()
            
            self.m3u_content += f'#EXTINF:-1 tvg-name="{clean_name}" group-title="BilyonerSport",{clean_name}\n'
            self.m3u_content += f'#EXTVLCOPT:http-referrer={active_domain}\n'
            self.m3u_content += f"{clean_link}\n\n"
            
            successful_channels += 1
            print(f"✅ Bilyonersport: {clean_name}")

        print(f"📊 Bilyonersport: {successful_channels} channels added")
        return successful_channels

    def save_m3u(self):
        # DÜZELTİLMİŞ SATIR: Android path yerine GitHub path
        file_path = "DeaTHLesS-Tek-Paket.m3u"
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.m3u_content)
            print(f"\n💾 M3U file saved: {file_path}")
            return True
        except Exception as e:
            print(f"❌ Save error: {str(e)}")
            return False

def main():
    print("🚀 Starting DeaTHLesS Multi-Source Bot...")
    generator = DeaTHLesS_M3U_Generator()
    
    total_channels = 0
    total_channels += generator.selcuksports_streams()
    total_channels += generator.birazcikspor_streams()
    total_channels += generator.bilyonersport_streams()
    
    if total_channels > 0:
        generator.save_m3u()
        print(f"\n🎯 Process completed! Total channels: {total_channels}")
    else:
        print("💥 No channels found from any source!")

if __name__ == "__main__":
    main()
