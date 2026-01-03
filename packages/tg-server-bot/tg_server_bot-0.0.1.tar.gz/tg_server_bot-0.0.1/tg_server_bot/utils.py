# -*- coding: utf-8 -*-
import functools
import logging
import logging.handlers
import queue
import os
import asyncio
from io import BytesIO
import aiohttp
import aiofiles
from telegram import Update
from telegram.error import NetworkError, TimedOut
from .const import IPV4_APIS, IPV6_APIS

# 配置日志系统 (使用队列模式，避免主线程阻塞)
log_queue = queue.Queue(-1)
queue_handler = logging.handlers.QueueHandler(log_queue)

logger = logging.getLogger('tg_server_bot')
logger.setLevel(logging.INFO)
logger.propagate = False  # 禁止日志向上传播，防止双重打印

# 避免重复添加 Handler
if not logger.handlers:
    logger.addHandler(queue_handler)


def setup_logging(log_file=None, enable_console=True):
    """
    初始化日志监听器。
    :param log_file: 日志文件路径。如果为空，则不记录文件。
    :param enable_console: 是否开启控制台输出 (stdout/stderr)。
    """
    handlers = []

    # 控制台输出总是保留
    if enable_console:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    # 仅当指定了 log_file 时才添加文件处理器
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except Exception as e:
            print(f"⚠️ 无法创建日志文件 {log_file}: {e}")

    listener = logging.handlers.QueueListener(log_queue, *handlers)
    listener.start()
    return listener


def singleton(cls):
    """单例模式装饰器"""
    instances = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


def get_file_modify_time(file_path: str) -> float:
    try:
        return os.path.getmtime(file_path)
    except OSError:
        return 0


def check_file_exist(file_path: str) -> bool:
    return bool(file_path and os.path.exists(file_path) and os.path.isfile(file_path))


async def reply_message_safely(update: Update, text: str, parse_mode=None, max_retries=3, reply_markup=None):
    """安全回复消息，带重试机制"""
    for attempt in range(max_retries):
        try:
            target_message = update.message if update.message else update.callback_query.message
            if not target_message:
                return
            await target_message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
            return
        except (NetworkError, TimedOut) as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                logger.warning(f"网络错误 ({attempt+1}/{max_retries}), {wait_time}s后重试: {e}")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"回复失败，已重试{max_retries}次: {e}")
        except Exception as e:
            logger.error(f"回复失败: {e}")
            return


async def send_doc_safely(update: Update, doc_path: str, max_retries=3):
    """安全发送文件，带重试机制"""
    for attempt in range(max_retries):
        try:
            async with aiofiles.open(doc_path, 'rb') as f:
                content = await f.read()
            bio = BytesIO(content)
            bio.name = os.path.basename(doc_path)
            await update.message.reply_document(document=bio)
            return
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"发送文件失败，正在重试 ({attempt+1}/{max_retries}): {e}")
                await asyncio.sleep(2)
            else:
                logger.error(f"发送文件失败 {doc_path}: {e}")
                await reply_message_safely(update, f"❌ 发送文件失败: {e}")


async def fetch_ip_text(is_ipv6: bool = False) -> str:
    """获取 IP 核心逻辑"""
    apis = IPV6_APIS if is_ipv6 else IPV4_APIS
    res = "❌ 无法获取"
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as s:
        for url in apis:
            try:
                async with s.get(url) as r:
                    if r.status == 200:
                        ip = (await r.text()).strip()
                        res = f"🌐 {'IPv6' if is_ipv6 else 'IPv4'}:{ip}"
                        break
            except:
                continue
    return res


def get_package_file_path(filename):
    """获取包安装目录下的文件绝对路径"""
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(pkg_dir, filename)
