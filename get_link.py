import requests
import re
from urllib.parse import urljoin

# Header giả lập trình duyệt xịn để qua mặt Anti-bot
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://sv2.thiendinh2.live/',
}

BASE_URL = 'https://sv2.thiendinh2.live/'

def get_m3u():
    m3u_lines = []
    try:
        # 1. Truy cập trang chủ hốt link trận
        s = requests.Session()
        r_home = s.get(urljoin(BASE_URL, 'trang-chu'), headers=HEADERS, timeout=15).text
        
        # Tìm tất cả link trực tiếp
        matches = re.findall(r'href="([^"]*(?:truc-tiep|match|watch)/[^"]+)"', r_home)
        matches = list(dict.fromkeys(matches))[::-1] # Lọc trùng và đảo ngược

        for m_url in matches:
            full_u = urljoin(BASE_URL, m_url)
            try:
                d = s.get(full_u, headers=HEADERS, timeout=10).text
                # Quét link stream m3u8
                streams = re.findall(r'(https?://[^\s"\'<>]+?\.m3u8[^\s"\'<>]*)', d)
                
                if streams:
                    t_match = re.search(r'<title>(.*?)</title>', d)
                    raw_title = t_match.group(1) if t_match else "Live"
                    
                    # DIỆT RÁC CACHEPBONGDA
                    clean_name = re.sub(r'\[?CACHEPBONGDA\]?', '', raw_title, flags=re.I)
                    clean_name = clean_name.split('|')[0].replace('Trực tiếp', '').split('-')[0].strip()
                    # Xóa nốt mấy từ quảng cáo lặt vặt
                    for trash in ["THIENDINH", "LIVE", "SV2", "VIP", "WEB"]:
                        clean_name = clean_name.replace(trash, "").strip()

                    # SĂN TÊN BLV XỊN
                    blv_tag = ""
                    # Tìm BLV trong nội dung trang (thường nằm sau chữ BLV:)
                    blv_find = re.search(r'BLV[:\s]+([\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệđìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]+)', d, re.I)
                    if blv_find:
                        name = blv_find.group(1).strip().upper()
                        if "CACHEP" not in name and 2 < len(name) < 15:
                            blv_tag = f"[{name}] "
                    elif '|' in raw_title:
                        # Nếu ko thấy trong body, lấy phần sau dấu | của title
                        poten = raw_title.split('|')[-1].strip().upper()
                        if "CACHEP" not in poten and len(poten) < 15:
                            blv_tag = f"[{poten}] "

                    for i, s_url in enumerate(streams):
                        # Link sạch không có dấu \
                        final_link = s_url.replace('\\', '')
                        display_name = f"{blv_tag}{clean_name} - Link {i+1}"
                        
                        # Build nội dung m3u
                        line = f'#EXTINF:-1 tvg-logo="https://sv2.thiendinh2.live/uploads/logo.png" group-title="Thiên Định TV", {display_name}\n'
                        line += f'#EXTVLCOPT:http-user-agent={HEADERS["User-Agent"]}\n'
                        line += f'#EXTVLCOPT:http-referrer={full_u}\n'
                        line += f'{final_link}'
                        m3u_lines.append(line)
            except: continue

        # Ghi file
        with open("list.m3u", "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n" + "\n".join(m3u_lines))
            
    except Exception as e:
        print(f"Lỗi rồi Mạnh ơi: {e}")

if __name__ == "__main__":
    get_m3u()
    
