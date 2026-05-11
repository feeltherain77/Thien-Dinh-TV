import requests
import re
import json
from urllib.parse import urljoin

# Dùng User-Agent của Mobile để web nó nhả link m3u8 trực tiếp
UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
BASE_URL = 'https://sv2.thiendinh2.live/'

def get_m3u():
    m3u_lines = []
    headers = {'User-Agent': UA, 'Referer': BASE_URL}
    
    try:
        session = requests.Session()
        # 1. Vào trang chủ lấy danh sách trận
        r_home = session.get(urljoin(BASE_URL, 'trang-chu'), headers=headers, timeout=15).text
        
        # Tìm link các trận đấu
        matches = re.findall(r'href="([^"]*(?:truc-tiep|match|watch)/[^"]+)"', r_home)
        matches = list(dict.fromkeys(matches))[::-1]

        for m_url in matches:
            full_u = urljoin(BASE_URL, m_url)
            try:
                # 2. Vào trang trận đấu
                d = session.get(full_u, headers=headers, timeout=10).text
                
                # SĂN LINK M3U8 (Tìm cả trong script và iframe)
                # Thiên định thường để link trong biến 'file' hoặc 'src'
                streams = re.findall(r'["\']?(https?://[^\s"\'<>]+?\.m3u8[^\s"\'<>]*)["\']?', d)
                
                if not streams:
                    # Nếu không thấy, tìm link iframe chứa player
                    iframe = re.search(r'iframe.*?src="([^"]+)"', d)
                    if iframe:
                        d_if = session.get(urljoin(BASE_URL, iframe.group(1)), headers=headers).text
                        streams = re.findall(r'["\']?(https?://[^\s"\'<>]+?\.m3u8[^\s"\'<>]*)["\']?', d_if)

                if streams:
                    t_match = re.search(r'<title>(.*?)</title>', d)
                    raw_title = t_match.group(1) if t_match else "Live"
                    
                    # LỌC RÁC
                    clean_name = re.sub(r'\[?CACHEPBONGDA\]?', '', raw_title, flags=re.I)
                    clean_name = clean_name.split('|')[0].replace('Trực tiếp', '').strip()
                    for trash in ["THIENDINH", "LIVE", "SV2", "VIP"]:
                        clean_name = clean_name.replace(trash, "").strip()

                    # BẮT BLV
                    blv_tag = ""
                    blv_find = re.search(r'BLV[:\s]+([\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệđìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]+)', d, re.I)
                    if blv_find:
                        name = blv_find.group(1).strip().upper()
                        if "CACHEP" not in name and len(name) < 15:
                            blv_tag = f"[{name}] "

                    for i, s_url in enumerate(list(dict.fromkeys(streams))):
                        final_link = s_url.replace('\\', '')
                        display_name = f"{blv_tag}{clean_name} - Link {i+1}"
                        
                        line = f'#EXTINF:-1 tvg-logo="https://sv2.thiendinh2.live/uploads/logo.png" group-title="Thiên Định TV", {display_name}\n'
                        # Thêm KODIPROP để OTT Navigator hay TiviMate đều chạy được
                        line += f'#KODIPROP:inputstream.adaptive.license_type=clearkey\n'
                        line += f'#EXTHTTP:{{"User-Agent":"{UA}","Referer":"{full_u}"}}\n'
                        line += f'{final_link}'
                        m3u_lines.append(line)
            except: continue

        # Ghi file
        with open("list.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n" + "\n".join(m3u_lines))
            
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    get_m3u()
    
