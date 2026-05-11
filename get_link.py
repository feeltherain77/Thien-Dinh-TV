import requests
import re
from urllib.parse import urljoin

# Header giả lập trình duyệt xịn
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Referer': 'https://sv2.tamquoc3.live/',
}

BASE_URL = 'https://sv2.tamquoc3.live/'

def get_m3u():
    m3u_lines = []
    try:
        session = requests.Session()
        # 1. Quét trang chủ lấy danh sách trận
        r_home = session.get(urljoin(BASE_URL, 'trang-chu'), headers=HEADERS, timeout=15).text
        
        # Bắt link các trận đấu (Tam Quốc thường dùng match/ hoặc watch/)
        matches = re.findall(r'href="([^"]*(?:truc-tiep|match|watch)/[^"]+)"', r_home)
        matches = list(dict.fromkeys(matches))[::-1] 

        for m_url in matches:
            full_u = urljoin(BASE_URL, m_url)
            try:
                # 2. Vào chi tiết trận đấu
                d = session.get(full_u, headers=HEADERS, timeout=10).text
                
                # Săn link m3u8
                streams = re.findall(r'(https?://[^\s"\'<>]+?\.m3u8[^\s"\'<>]*)', d)
                
                if streams:
                    t_match = re.search(r'<title>(.*?)</title>', d)
                    raw_title = t_match.group(1) if t_match else "Trực tiếp"
                    
                    # LỌC TÊN TRẬN (Sút văng rác quảng cáo)
                    clean_name = raw_title.split('|')[0].replace('Trực tiếp', '').split('-')[0].strip()
                    for trash in ["TAMQUOC", "LIVE", "VIP", "SV2", "WATCH", ".TV", ".LIVE"]:
                        clean_name = clean_name.replace(trash, "").strip()

                    # BẮT BLV (Tam Quốc hay để tên BLV sau dấu gạch đứng hoặc chữ BLV)
                    blv_tag = ""
                    blv_find = re.search(r'(?:BLV|Bình luận viên)[:\s]*([\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệđìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]+)', d, re.I)
                    if blv_find:
                        name = blv_find.group(1).strip().upper()
                        if len(name) < 15: blv_tag = f"[{name}] "
                    elif '|' in raw_title:
                        poten = raw_title.split('|')[-1].strip().upper()
                        if len(poten) < 15 and "TAM" not in poten:
                            blv_tag = f"[{poten}] "

                    for i, s_url in enumerate(list(dict.fromkeys(streams))):
                        final_link = s_url.replace('\\', '')
                        display_name = f"{blv_tag}{clean_name} - L{i+1}"
                        
                        # Cấu trúc cho mọi App (TiviMate, Televizo, OTT Navigator)
                        line = f'#EXTINF:-1 tvg-logo="https://sv2.tamquoc3.live/uploads/logo.png" group-title="Tam Quốc TV", {display_name}\n'
                        line += f'#EXTHTTP:{{"User-Agent":"{HEADERS["User-Agent"]}","Referer":"{full_u}"}}\n'
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
    
