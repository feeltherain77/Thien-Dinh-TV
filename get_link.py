import requests
import re
from urllib.parse import quote, urljoin

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
BASE_URL = 'https://sv2.thiendinh2.live/'

def get_m3u():
    m3u_lines = []
    h = {'User-Agent': UA, 'Referer': BASE_URL}
    
    try:
        # Lấy logo chính chủ Thiên Định
        r_home = requests.get(urljoin(BASE_URL, 'trang-chu'), headers=h, timeout=15).text
        web_logo = "https://sv2.thiendinh2.live/uploads/logo.png" # Link logo cứng cho chắc

        matches = re.findall(r'href="([^"]*(?:truc-tiep|match|watch)/[^"]+)"', r_home)
        
        for m_url in list(dict.fromkeys(matches))[::-1]: 
            full_u = urljoin(BASE_URL, m_url)
            try:
                d = requests.get(full_u, headers=h, timeout=10).text
                streams = re.findall(r'(https?://[^\s"\'<>]+?\.m3u8[^\s"\'<>]*)', d)
                
                if streams:
                    t_match = re.search(r'<title>(.*?)</title>', d)
                    raw_title = t_match.group(1) if t_match else "Live"
                    
                    # DIỆT RÁC CACHEP: Xóa sạch các cụm từ quảng cáo
                    clean_name = raw_title.split('|')[0].replace('Trực tiếp', '').split('-')[0].strip()
                    clean_name = re.sub(r'\[?CACHEPBONGDA\]?', '', clean_name, flags=re.I).strip()
                    clean_name = re.sub(r'(THIENDINH|LIVE|VIP|WEB|COM|SV2)', '', clean_name, flags=re.I).strip()

                    # SĂN BLV XỊN
                    blv_tag = ""
                    blv_find = re.search(r'BLV\s+([\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệđìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]+)', d, re.I)
                    if blv_find:
                        name = blv_find.group(1).strip().upper()
                        if "CACHEP" not in name and len(name) < 15:
                            blv_tag = f"[{name}] "

                    for i, s in enumerate(streams):
                        s_link = s.replace('\\', '')
                        display_name = f"{blv_tag}{clean_name} - Link {i+1}"
                        
                        line = f'#EXTINF:-1 tvg-logo="{web_logo}" group-title="Thiên Định TV", {display_name}\n'
                        line += f'#EXTVLCOPT:http-user-agent={UA}\n'
                        line += f'#EXTVLCOPT:http-referrer={full_u}\n'
                        line += f'#EXTVLCOPT:http-origin={BASE_URL}\n'
                        line += f'{s_link}'
                        m3u_lines.append(line)
            except: continue

        with open("list.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n" + "\n".join(m3u_lines))
    except: pass

if __name__ == "__main__":
    get_m3u()
    
