import yt_dlp
import os
import re
import requests
from typing import Generator, Dict, Any
from PIL import Image
from io import BytesIO
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('BiliDownloader')

class BiliDownloader:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com'
        }
        self.downloaded_files = set()
        self.base_url = "https://www.bilibili.com/video/"
        logger.info("BiliDownloader 初始化完成")
    
    def extract_bvid(self, url: str) -> str:
        """从URL中提取BV号"""
        pattern = r"BV[a-zA-Z0-9]+"
        match = re.search(pattern, url)
        if not match:
            logger.error(f"无效的哔哩哔哩链接: {url}")
            raise ValueError("无效的哔哩哔哩链接")
        bvid = match.group()
        logger.info(f"成功提取BV号: {bvid}")
        return bvid
    
    def get_cover_image(self, info: dict) -> bytes:
        """获取并处理封面图片"""
        if 'thumbnail' in info:
            logger.info(f"开始下载视频封面: {info.get('title', 'Unknown')}")
            response = requests.get(info['thumbnail'], headers=self.headers)
            if response.status_code == 200:
                logger.info("封面下载成功，开始处理图片")
                # 打开图片
                img = Image.open(BytesIO(response.content))
                # 调整大小为400x400
                img = img.resize((400, 400), Image.Resampling.LANCZOS)
                # 转换为字节
                output = BytesIO()
                img.save(output, format='JPEG')
                logger.info("封面处理完成 (400x400)")
                return output.getvalue()
            else:
                logger.warning(f"封面下载失败: HTTP {response.status_code}")
        else:
            logger.warning("视频信息中未找到封面")
        return None
    
    def embed_cover(self, mp3_path: str, cover_data: bytes):
        """将封面嵌入到MP3文件中"""
        try:
            logger.info(f"开始为音频文件添加封面: {os.path.basename(mp3_path)}")
            audio = MP3(mp3_path, ID3=ID3)
            
            # 如果没有ID3标签，创建一个
            if audio.tags is None:
                audio.add_tags()
                logger.info("创建新的ID3标签")
            
            # 添加封面
            audio.tags.add(
                APIC(
                    encoding=3,  # UTF-8
                    mime='image/jpeg',
                    type=3,  # 封面图片
                    desc='Cover',
                    data=cover_data
                )
            )
            audio.save()
            logger.info("封面添加成功")
        except Exception as e:
            logger.error(f"添加封面时出错: {str(e)}")
    
    def check_playlist(self, bvid: str) -> int:
        """检查播放列表中的视频数量"""
        url = f"{self.base_url}{bvid}"
        logger.info(f"开始检查播放列表: {url}")
        
        try:
            # 使用requests获取页面内容
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                logger.error(f"请求失败: HTTP {response.status_code}")
                return 1
            
            # 在页面内容中查找分P信息
            content = response.text
            # 查找包含分P数量的模式
            pattern = r'"page":(\d+),'
            matches = re.findall(pattern, content)
            
            if matches:
                # 如果找到匹配，取最大的数字
                max_page = max(map(int, matches))
                logger.info(f"检测到多P视频，共 {max_page} 个分P")
                return max_page
            else:
                logger.info("未检测到分P信息，视频为单集")
                return 1
                
        except Exception as e:
            logger.error(f"检查播放列表时出错: {str(e)}")
            return 1
    
    def download(self, bvid: str, output_dir: str, rename: bool = False) -> Generator[Dict[str, Any], None, None]:
        """下载音频文件"""
        base_path = os.path.join("audiobooks", output_dir)
        os.makedirs(base_path, exist_ok=True)
        logger.info(f"创建输出目录: {base_path}")
        
        count = self.check_playlist(bvid)
        logger.info(f"准备下载 {count} 个视频")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }],
            'outtmpl': os.path.join(base_path, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'retries': 3,
            'headers': self.headers,
            'writethumbnail': True,
        }
        
        for p in range(1, count + 1):
            url = f"{self.base_url}{bvid}?p={p}"
            logger.info(f"处理第 {p}/{count} 个视频: {url}")
            
            if url in self.downloaded_files:
                logger.info(f"跳过已下载的文件: {url}")
                yield {'status': 'skip', 'message': f'已跳过重复文件: {url}', 'progress': (p / count) * 100}
                continue
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    logger.info("开始下载音频")
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info).replace('.webm', '.mp3')
                    logger.info(f"音频下载完成: {os.path.basename(filename)}")
                    
                    # 获取并嵌入封面
                    cover_data = self.get_cover_image(info)
                    if cover_data:
                        self.embed_cover(filename, cover_data)
                    
                    if rename:
                        new_filename = os.path.join(base_path, f"{output_dir}-{p}.mp3")
                        if os.path.exists(filename):
                            logger.info(f"重命名文件: {os.path.basename(filename)} -> {os.path.basename(new_filename)}")
                            os.rename(filename, new_filename)
                            filename = new_filename
                    
                    self.downloaded_files.add(url)
                    yield {
                        'status': 'success',
                        'message': f'已下载: {os.path.basename(filename)}',
                        'progress': (p / count) * 100
                    }
            except Exception as e:
                logger.error(f"下载失败: {str(e)}")
                yield {
                    'status': 'error',
                    'message': f'下载失败: {str(e)}',
                    'progress': (p / count) * 100
                }
                continue 