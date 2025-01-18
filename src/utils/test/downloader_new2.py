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
from datetime import datetime

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
        try:
            # 首先尝试从info中获取封面URL
            cover_url = None
            if 'thumbnail' in info:
                cover_url = info['thumbnail']
            elif 'thumbnails' in info and info['thumbnails']:
                # 选择最高质量的缩略图
                cover_url = info['thumbnails'][-1]['url']
            
            if not cover_url:
                # 尝试从网页中提取封面URL
                webpage_url = info.get('webpage_url')
                if webpage_url:
                    response = requests.get(webpage_url, headers=self.headers)
                    if response.status_code == 200:
                        # 在页面内容中查找封面URL
                        pattern = r'"coverUrl":"([^"]+)"'
                        match = re.search(pattern, response.text)
                        if match:
                            cover_url = match.group(1)

            if cover_url:
                logger.info(f"找到封面URL: {cover_url}")
                response = requests.get(cover_url, headers=self.headers)
                if response.status_code == 200:
                    logger.info("封面下载成功，开始处理图片")
                    # 打开图片
                    img = Image.open(BytesIO(response.content))
                    original_size = img.size
                    logger.info(f"原始图片尺寸: {original_size}")

                    # 计算裁剪区域（保持宽高比1:1）
                    size = min(img.width, img.height)
                    left = (img.width - size) // 2
                    top = (img.height - size) // 2
                    right = left + size
                    bottom = top + size

                    # 裁剪为正方形
                    img = img.crop((left, top, right, bottom))
                    logger.info(f"裁剪后尺寸: {img.size}")

                    # 调整大小为400x400
                    img = img.resize((400, 400), Image.Resampling.LANCZOS)
                    
                    # 转换为字节
                    output = BytesIO()
                    img.save(output, format='JPEG', quality=95)
                    logger.info(f"封面处理完成: {original_size} -> (400x400)")
                    return output.getvalue()
            else:
                logger.warning("未找到封面URL")
        except Exception as e:
            logger.error(f"处理封面时出错: {str(e)}")
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
        start_time = datetime.now()
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
                'preferredquality': '192',  # 设置音质
            }],
            'outtmpl': os.path.join(base_path, '%(title)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'retries': 3,
            'headers': self.headers,
            'extract_flat': False,  # 获取完整信息
            'writeinfojson': True,  # 保存视频信息
        }
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for p in range(1, count + 1):
            url = f"{self.base_url}{bvid}?p={p}"
            logger.info(f"处理第 {p}/{count} 个视频: {url}")
            
            if url in self.downloaded_files:
                logger.info(f"跳过已下载的文件: {url}")
                skip_count += 1
                yield {'status': 'skip', 'message': f'已跳过重复文件: {url}', 'progress': (p / count) * 100}
                continue
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    logger.info("开始下载音频")
                    info = ydl.extract_info(url, download=True)
                    
                    # 获取原始文件名（可能是.m4a或其他格式）
                    original_filename = ydl.prepare_filename(info)
                    logger.info(f"原始文件名: {original_filename}")
                    
                    # 检查文件是否存在，如果不存在，尝试其他可能的扩展名
                    possible_exts = ['.m4a', '.webm', '.mp3']
                    found_file = None
                    for ext in possible_exts:
                        test_filename = os.path.splitext(original_filename)[0] + ext
                        if os.path.exists(test_filename):
                            found_file = test_filename
                            logger.info(f"找到音频文件: {found_file}")
                            break
                    
                    if not found_file:
                        raise FileNotFoundError("无法找到下载的音频文件")
                    
                    # 获取MP3文件名
                    mp3_filename = os.path.splitext(found_file)[0] + '.mp3'
                    
                    # 如果原始文件不是MP3格式，等待转换完成
                    if found_file != mp3_filename:
                        logger.info(f"等待音频转换: {os.path.basename(found_file)} -> {os.path.basename(mp3_filename)}")
                        # 等待MP3文件出现（最多等待30秒）
                        for _ in range(30):
                            if os.path.exists(mp3_filename):
                                break
                            import time
                            time.sleep(1)
                    
                    if not os.path.exists(mp3_filename):
                        raise FileNotFoundError("MP3转换失败或超时")
                    
                    logger.info(f"音频下载和转换完成: {os.path.basename(mp3_filename)}")
                    
                    # 获取并嵌入封面
                    cover_data = self.get_cover_image(info)
                    if cover_data:
                        self.embed_cover(mp3_filename, cover_data)
                    else:
                        logger.warning("无法获取封面图片")
                    
                    if rename:
                        new_filename = os.path.join(base_path, f"{output_dir}-{p}.mp3")
                        if os.path.exists(mp3_filename):
                            logger.info(f"重命名文件: {os.path.basename(mp3_filename)} -> {os.path.basename(new_filename)}")
                            os.rename(mp3_filename, new_filename)
                            mp3_filename = new_filename
                    
                    # 清理临时文件
                    try:
                        # 清理原始音频文件（如果与MP3不同）
                        if found_file != mp3_filename and os.path.exists(found_file):
                            os.remove(found_file)
                            logger.info(f"清理原始音频文件: {os.path.basename(found_file)}")
                        
                        # 清理JSON文件
                        info_json = original_filename + '.info.json'
                        if os.path.exists(info_json):
                            os.remove(info_json)
                            logger.info("清理临时JSON文件")
                    except Exception as e:
                        logger.warning(f"清理临时文件失败: {str(e)}")
                    
                    self.downloaded_files.add(url)
                    success_count += 1
                    yield {
                        'status': 'success',
                        'message': f'已下载: {os.path.basename(mp3_filename)}',
                        'progress': (p / count) * 100
                    }
            except Exception as e:
                logger.error(f"下载失败: {str(e)}")
                error_count += 1
                yield {
                    'status': 'error',
                    'message': f'下载失败: {str(e)}',
                    'progress': (p / count) * 100
                }
                continue
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info("下载任务完成")
        logger.info(f"总计: {count} 个视频")
        logger.info(f"成功: {success_count} 个")
        logger.info(f"跳过: {skip_count} 个")
        logger.info(f"失败: {error_count} 个")
        logger.info(f"总耗时: {duration.total_seconds():.1f} 秒") 