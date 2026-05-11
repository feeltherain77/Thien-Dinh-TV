import requests
import re
from urllib.parse import quote, urljoin

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
# Domain VIP mới của Mạnh
BASE_URL = 'https://sv2.thiendinh2.live/'

def get_m3u():
    m3u_lines = []
    h = {'User-Agent': UA, 'Referer': BASE_URL}
    processed = set()
    
    try:
        # 1. LẤY LOGO VIP TỪ TRANG CHỦ
        r_home = requests.get(urljoin(BASE_URL, 'trang-chu'), headers=h, timeout=15).text
        logo_match = re.search(r'src="([^"]*logo[^"]*)"', r_home, re.I)
        web_logo = urljoin(BASE_URL, logo_match.group(1)) if logo_match else "https://sv2.thiendinh2.live/uploads/logo.png"

        # 2. QUÉT TRẬN ĐẤU
        matches = re.findall(r'href="([^"]*(?:truc-tiep|match|watch)/[^"]+)"', r_home)
        
        # Đảo ngược [::-1] để những trận mới nhất/đang đá nằm trên cùng
        for m_url in list(dict.fromkeys(matches))[::-1]: 
            full_u = urljoin(BASE_URL, m_url)
            if full_u in processed: continue
            try:
                d = requests.get(full_u, headers=h, timeout=10).text
                # Quét link m3u8
                streams = re.findall(r'(https?://[^\s"\'<>]+?\.m3u8[^\s"\'<>]*)', d)
                
                if streams:
                    t_match = re.search(r'<title>(.*?)</title>', d)
                    raw_title = t_match.group(1) if t_match else "Live"
                    
                    # LỌC TÊN TRẬN (Bỏ rác watermark của web)
                    clean_name = raw_title.split('|')[0].replace('Trực tiếp', '').split('-')[0].strip()
                    clean_name = re.sub(r'(THIENDINH|LIVE|VIP|WEB|COM|SV2)', '', clean_name, flags=re.I).strip()

                    # SĂN BLV (Ép tên người lên đầu)
                    blv_tag = ""
                    # Tìm trong title hoặc trong code web
                    blv_find = re.search(r'(?:BLV|Bình luận viên)\s*:?\s*([\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệđìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]+)', d, re.IGNORECASE)
                    
                    if blv_find:
                        name_blv = blv_find.group(1).strip().upper()
                        if 1 < len(name_blv) < 15:
                            blv_tag = f"[{name_blv}] "
                    elif '|' in raw_title:
                        potential = raw_title.split('|')[-1].strip().upper()
                        if len(potential) < 15 and "THIEN" not in potential:
                            blv_tag = f"[{potential}] "

                    for i, s in enumerate(streams):
                        s_link = s.replace('\\', '')
                        # Tên chuẩn: [BLV] Tên trận - L1
                        display_name = f"{blv_tag}{clean_name} - L{i+1}"
                        
                        # Cấu trúc VIP đa App (TiviMate, OTT Navigator, Smarters...)
                        line = f'#EXTINF:-1 tvg-logo="{web_logo}" group-title="Bún Chả TV", {display_name}\n'
                        line += f'#EXTVLCOPT:http-user-agent={UA}\n'
                        line += f'#EXTVLCOPT:http-referrer={full_u}\n'
                        line += f'#EXTVLCOPT:http-origin={BASE_URL}\n'
                        line += f'{s_link}'
                        m3u_lines.append(line)
            except: continue
            processed.add(full_u)
    except: pass

    with open("list.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n" + "\n".join(m3u_lines))

if __name__ == "__main__":
    get_m3u()
      
