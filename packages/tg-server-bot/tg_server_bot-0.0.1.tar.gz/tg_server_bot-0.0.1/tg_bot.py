#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import functools
import logging
import threading
import time
import argparse
import os
import configparser
import shutil
import queue
import logging.handlers
from io import BytesIO
from typing import Optional, List, Dict, Set

import aiohttp
import aiofiles
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from telegram.error import NetworkError, TimedOut

# 全局常量
DEF_CONFIG_FILE_NAME = 'tg_bot.ini'
DEF_LOG_FILE = 'tg_bot.log'
DEF_ALLOW_USER_FILE = 'verified_id.txt'

IPV4_APIS = [
    'http://api-ipv4.ip.sb/ip',
    'https://v4.myip.la',
    'http://whatismyip.akamai.com'
]

IPV6_APIS = [
    'https://ipv6.whatismyip.akamai.com',
    'http://api-ipv6.ip.sb/ip',
    'https://v6.ident.me',
    'http://v6.ipv6-test.com/api/myip.php',
    'http://ipv6.icanhazip.com',
]

# 配置日志系统 (使用队列模式，避免主线程阻塞)
log_queue = queue.Queue(-1)
queue_handler = logging.handlers.QueueHandler(log_queue)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(queue_handler)

file_handler = logging.FileHandler(DEF_LOG_FILE, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

listener = logging.handlers.QueueListener(log_queue, file_handler)
listener.start()


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


@singleton
class Config:
    def __init__(self) -> None:
        self.get_cmds: Dict[str, str] = {}
        self.run_cmds: Dict[str, str] = {}
        self.runtime_keys: Set[str] = set()
        self.token: Optional[str] = None
        self.proxy: Optional[str] = None
        self.log_file: str = DEF_LOG_FILE
        self.allow_user_file: str = DEF_ALLOW_USER_FILE
        self.config_path: str = DEF_CONFIG_FILE_NAME

    def save_cmd(self, section: str, cmd: str, value: str):
        """保存新指令到配置文件"""
        if section == 'get':
            self.get_cmds[cmd] = value
        else:
            self.run_cmds[cmd] = value
        parser = configparser.ConfigParser()
        parser.read(self.config_path, 'utf-8')
        if not parser.has_section(section):
            parser.add_section(section)
        parser.set(section, cmd, value)
        try:
            if os.path.exists(self.config_path):
                shutil.copy2(self.config_path, self.config_path + ".bak")
        except Exception as e:
            logger.error(f"配置文件备份失败: {e}")
            raise Exception(f"配置文件备份失败: {e}")
        with open(self.config_path, 'w', encoding='utf-8') as f:
            parser.write(f)

    def add_runtime_cmd(self, section: str, cmd: str, value: str):
        if section == 'get':
            self.get_cmds[cmd] = value
        else:
            self.run_cmds[cmd] = value
        self.runtime_keys.add(cmd)

    def clear_runtime_cmds(self):
        for cmd in list(self.runtime_keys):
            if cmd in self.get_cmds:
                del self.get_cmds[cmd]
            if cmd in self.run_cmds:
                del self.run_cmds[cmd]
        count = len(self.runtime_keys)
        self.runtime_keys.clear()
        return count

    def is_config_cmd(self, cmd: str) -> bool:
        return (cmd in self.get_cmds or cmd in self.run_cmds) and cmd not in self.runtime_keys


@singleton
class PermissionHelper:
    def __init__(self) -> None:
        self.config = Config()
        self.allow_user_ids: List[str] = []
        self.last_modify_time: float = 0
        self._running = True
        self.__update_allow_users()
        self.__watch_config()

    def __watch_config(self):
        self.last_modify_time = get_file_modify_time(self.config.allow_user_file)
        watcher = threading.Thread(target=self.__watch_file_change, daemon=True)
        watcher.start()

    def __update_allow_users(self):
        new_allow_ids = []
        if not os.path.exists(self.config.allow_user_file):
            self.allow_user_ids = []
            return
        try:
            with open(self.config.allow_user_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    new_allow_ids.append(line)
            self.allow_user_ids = new_allow_ids
            logger.info(f"已更新授权用户列表: {len(self.allow_user_ids)} 个用户")
        except Exception as e:
            logger.error(f"读取鉴权文件失败: {e}")

    def __watch_file_change(self):
        while self._running:
            try:
                current_time = get_file_modify_time(self.config.allow_user_file)
                if current_time > self.last_modify_time:
                    self.last_modify_time = current_time
                    logger.info('鉴权文件检测到更新，正在重新加载...')
                    self.__update_allow_users()
            except Exception as e:
                logger.error(f"监听鉴权文件出错: {e}")
            time.sleep(3)

    def is_allowed(self, user_id: str) -> bool:
        return str(user_id) in self.allow_user_ids


def check_file_exist(file_path: str) -> bool:
    return bool(file_path and os.path.exists(file_path) and os.path.isfile(file_path))


async def reply_message_safely(update: Update, text: str, parse_mode=None, max_retries=3, reply_markup=None):
    """安全回复消息，带重试机制"""
    for attempt in range(max_retries):
        try:
            target_message = update.message if update.message else update.callback_query.message
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


def authorized_only(func):
    """装饰器：检查用户是否有权限，并记录所有请求状态"""
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_user:
            return
        user = update.effective_user
        content = update.message.text if update.message and update.message.text else "Interaction"
        is_allowed = PermissionHelper().is_allowed(user.id)
        status = "✅ AUTHORIZED" if is_allowed else "⛔ UNAUTHORIZED"
        logger.info(f"[{status}] User: {user.name}({user.id}) | Action: {func.__name__} | Content: {content}")
        if not is_allowed:
            await reply_message_safely(update, '⚠️ 警告: 你没有访问权限！')
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


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
                await asyncio.sleep(2)
            else:
                logger.error(f"发送文件失败 {doc_path}: {e}")
                await reply_message_safely(update, f"❌ 发送文件失败: {e}")

def get_main_keyboard():
    """动态生成快捷键菜单"""
    config = Config()
    keyboard = [[KeyboardButton("/ip"), KeyboardButton("/ipv6"), KeyboardButton("/list")]]
    custom_btns = []
    for k in sorted(config.get_cmds.keys()):
        custom_btns.append(KeyboardButton(f"📂 /{k}"))
    for k in sorted(config.run_cmds.keys()):
        custom_btns.append(KeyboardButton(f"🚀 /{k}"))
    for i in range(0, len(custom_btns), 2):
        keyboard.append(custom_btns[i:i+2])
    keyboard.append([KeyboardButton("/start"), KeyboardButton("/clear")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


@authorized_only
async def list_cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """列出所有可用指令"""
    config = Config()
    lines = ["🤖 **当前支持的指令列表**", ""]
    lines.append("🔹 **系统管理**")
    lines.append("/start - 🏠 唤起面板")
    lines.append("/list - 📜 刷新列表")
    lines.append("/ip - 🌐 IPv4 查询")
    lines.append("/ipv6 - 🌍 IPv6 查询")
    lines.append("/clear - 🗑️ 清空临时指令")
    lines.append("")
    if config.get_cmds:
        lines.append("📂 **文件下载指令**")
        for k in sorted(config.get_cmds.keys()):
            tag = "⚡" if k in config.runtime_keys else "💾"
            lines.append(f"/{k} - {tag} `{config.get_cmds[k]}`")
        lines.append("")
    if config.run_cmds:
        lines.append("🚀 **快捷执行指令**")
        for k in sorted(config.run_cmds.keys()):
            tag = "⚡" if k in config.runtime_keys else "💾"
            lines.append(f"/{k} - {tag} `{config.run_cmds[k]}`")
    lines.append("")
    lines.append("🔸 **注册新指令**")
    lines.append("`/add_get <name> <path>`")
    lines.append("`/add_run <name> <cmd>`")
    await reply_message_safely(update, "\n".join(lines), parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard())


@authorized_only
async def clear_cmds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """清除所有运行态指令"""
    count = Config().clear_runtime_cmds()
    await update_bot_commands(context.application)
    await reply_message_safely(update, f"🗑️ 已清空 {count} 条临时指令。", reply_markup=get_main_keyboard())


@authorized_only
async def add_get_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """动态添加文件下载指令 (Runtime)"""
    if not context.args or len(context.args) != 2:
        await reply_message_safely(update, "⚠️ 格式: `/add_get <name> <path>`")
        return
    name = context.args[0]
    path = context.args[1]
    reserved = ['start', 'run', 'ip', 'ipv6', 'add_get', 'add_run', 'list', 'clear', 'help']
    if name in reserved or Config().is_config_cmd(name):
        await reply_message_safely(update, "❌ 无法覆盖永久或保留指令！")
        return
    Config().add_runtime_cmd('get', name, path)
    # 不再动态添加 Handler，由 dynamic_command_dispatcher 统一接管
    await update_bot_commands(context.application)
    await reply_message_safely(update, f"✅ 已添加临时文件指令: /{name}", reply_markup=get_main_keyboard())


@authorized_only
async def add_run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """动态添加Shell执行指令 (Runtime)"""
    if not context.args or len(context.args) < 2:
        await reply_message_safely(update, "⚠️ 格式: `/add_run <name> <cmd>`")
        return
    name = context.args[0]
    cmd = " ".join(context.args[1:])
    reserved = ['start', 'run', 'ip', 'ipv6', 'add_get', 'add_run', 'list', 'clear', 'help']
    if name in reserved or Config().is_config_cmd(name):
        await reply_message_safely(update, "❌ 无法覆盖永久或保留指令！")
        return
    Config().add_runtime_cmd('run_cmds', name, cmd)
    # 不再动态添加 Handler，由 dynamic_command_dispatcher 统一接管
    await update_bot_commands(context.application)
    await reply_message_safely(update, f"✅ 已添加临时执行指令: /{name}", reply_markup=get_main_keyboard())


@authorized_only
async def run_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """手动执行任意 Shell 命令"""
    if not context.args:
        await reply_message_safely(update, '⚠️ 请输入指令，例如: /run echo hello', parse_mode=ParseMode.MARKDOWN)
        return
    command = ' '.join(context.args)
    try:
        status_msg = await update.message.reply_text(f"⏳ 正在执行: {command}")
        process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        output = (stdout.decode().strip() + "\n" + stderr.decode().strip()).strip() or "✅ 执行成功，无输出。"
        final_text = f"🖥️ {command} 结果:\n\n{output[-4000:]}"
        await reply_message_safely(update, final_text)
    except Exception as e:
        logger.error(f"Run cmd error: {e}")
        await reply_message_safely(update, f"❌ 执行 {command} 出错: {e}")


@authorized_only
async def run_dynamic_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理动态注册的 Shell 命令"""
    raw_text = update.message.text
    cmd_name = raw_text.split("🚀 /")[-1] if "🚀 /" in raw_text else raw_text.split()[0].lstrip('/')
    shell_cmd = Config().run_cmds.get(cmd_name)
    if not shell_cmd: return
    try:
        msg = await update.message.reply_text(f"⏳ 正在执行: {shell_cmd}")
        proc = await asyncio.create_subprocess_shell(shell_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        out, err = await proc.communicate()
        res = (out.decode().strip() + "\n" + err.decode().strip()).strip() or "✅ 执行成功，无输出。"
        await reply_message_safely(update, f"🖥️ {shell_cmd} 结果:\n\n{res[-4000:]}")
    except Exception as e:
        logger.error(f"Dynamic execution failed: {e}")
        await reply_message_safely(update, f"❌ 执行 {shell_cmd} 出错: {e}")


@authorized_only
async def get_cmd_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """读取文件内容"""
    if not update.message.text: return
    raw_text = update.message.text
    cmd_name = raw_text.split("📂 /")[-1] if "📂 /" in raw_text else raw_text.split()[0].lstrip('/')
    path = Config().get_cmds.get(cmd_name)
    if path and check_file_exist(path):
        await send_doc_safely(update, path)
    else:
        await reply_message_safely(update, "❌ 文件不存在或指令失效")


@authorized_only
async def dynamic_command_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """统一分发动态指令和未知文本"""
    text = update.message.text.strip()

    # 尝试作为指令处理 (去掉 / 前缀)
    cmd_candidate = text.lstrip('/')
    config = Config()

    if cmd_candidate in config.get_cmds:
        # 伪装消息文本以便 get_cmd_file 处理
        # 注意：这里不需要修改 update.message.text，因为 get_cmd_file 内部会再次解析
        await get_cmd_file(update, context)
        return

    if cmd_candidate in config.run_cmds:
        await run_dynamic_cmd(update, context)
        return

    # 如果不是指令，则作为普通路径处理
    if check_file_exist(text):
        await send_doc_safely(update, text)
    else:
        await reply_message_safely(update, "❓ 未知指令或文件。输入 /start 唤起面板。")


@authorized_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """主面板入口"""
    inline_keyboard = [
        [InlineKeyboardButton("🌐 IPv4 查询", callback_data='get_ipv4'), InlineKeyboardButton("🌍 IPv6 查询", callback_data='get_ipv6')],
        [InlineKeyboardButton("❓ 帮助 / 状态", callback_data='help_status')]
    ]
    await reply_message_safely(update, "🎮 **服务器控制面板已就绪**\n点击下方按钮快速执行指令：", parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard())
    await update.message.reply_text("快捷查询：", reply_markup=InlineKeyboardMarkup(inline_keyboard))


@authorized_only
async def reply_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理带图标的快捷按键点击"""
    text = update.message.text
    if text.startswith("📂 /"):
        await get_cmd_file(update, context)
    elif text.startswith("🚀 /"):
        await run_dynamic_cmd(update, context)


@authorized_only
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 Inline 按钮点击事件"""
    query = update.callback_query
    await query.answer()
    if query.data == 'get_ipv4':
        await reply_message_safely(update, "⏳ 正在查询 IPv4...", parse_mode=ParseMode.MARKDOWN)
        text = await fetch_ip_text(is_ipv6=False)
        await reply_message_safely(update, text)
    elif query.data == 'get_ipv6':
        await reply_message_safely(update, "⏳ 正在查询 IPv6...", parse_mode=ParseMode.MARKDOWN)
        text = await fetch_ip_text(is_ipv6=True)
        await reply_message_safely(update, text)
    elif query.data == 'help_status':
        await list_cmds(update, context)


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
            except: continue
    return res


@authorized_only
async def get_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """获取服务器 IP 地址"""
    is_ipv6 = 'ipv6' in update.message.text.lower()
    text = await fetch_ip_text(is_ipv6)
    await reply_message_safely(update, text=text)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """全局错误处理"""
    logger.error("Update Error:", exc_info=context.error)

def parse_config(path):
    """解析配置文件"""
    if not os.path.exists(path):
        logger.error(f"配置文件不存在: {path}")
        return Config()
    p = configparser.ConfigParser()
    p.read(path, 'utf-8')
    c = Config()
    c.config_path = path
    if p.has_section('common'):
        c.token = p.get('common', 'token', fallback=None)
        c.proxy = p.get('common', 'proxy', fallback=None)
    if p.has_section('get'): c.get_cmds = dict(p.items('get'))
    if p.has_section('run_cmds'): c.run_cmds = dict(p.items('run_cmds'))
    return c


async def update_bot_commands(application: Application):
    """更新机器人的菜单指令列表"""
    config = Config()
    commands = [
        BotCommand("start", "🏠 唤起面板"),
        BotCommand("list", "📜 指令列表"),
        BotCommand("ip", "🌐 IPv4 查询"),
        BotCommand("ipv6", "🌍 IPv6 查询"),
        BotCommand("run", "💻 执行 Shell"),
        BotCommand("clear", "🗑️ 清空临时指令"),
        BotCommand("add_get", "➕ 文件指令"),
        BotCommand("add_run", "➕ Shell指令"),
    ]

    # 动态添加配置中的指令
    for k in sorted(config.get_cmds.keys()):
        commands.append(BotCommand(k, f"📂 下载 {k}"))
    for k in sorted(config.run_cmds.keys()):
        commands.append(BotCommand(k, f"🚀 执行 {k}"))

    try:
        await application.bot.set_my_commands(commands)
        logger.info(f"已更新菜单指令，共 {len(commands)} 个")
    except Exception as e:
        logger.error(f"更新菜单指令失败: {e}")


async def post_init(application: Application) -> None:
    """启动后自动设置菜单指令"""
    await update_bot_commands(application)


def main():
    """程序入口"""
    arg_p = argparse.ArgumentParser()
    arg_p.add_argument('-c', '--config', default=os.path.join(os.path.dirname(__file__), DEF_CONFIG_FILE_NAME))
    args = arg_p.parse_args()
    cfg = parse_config(args.config)
    if not cfg.token:
        logger.error("Token 未配置，程序退出！")
        return
    PermissionHelper()
    app = ApplicationBuilder().token(cfg.token).post_init(post_init)
    if cfg.proxy: app.get_updates_proxy(cfg.proxy).proxy(cfg.proxy)
    bot = app.build()
    bot.add_handler(CommandHandler('start', start, block=False))
    bot.add_handler(CommandHandler('run', run_cmd, block=False))
    bot.add_handler(CommandHandler(['ip', 'ipv6'], get_ip, block=False))
    bot.add_handler(CommandHandler('add_get', add_get_cmd, block=False))
    bot.add_handler(CommandHandler('add_run', add_run_cmd, block=False))
    bot.add_handler(CommandHandler('clear', clear_cmds, block=False))
    bot.add_handler(CommandHandler(['list', 'help'], list_cmds, block=False))
    bot.add_handler(CallbackQueryHandler(button_handler, block=False))
    bot.add_handler(MessageHandler(filters.Regex(r'^(📂 /|🚀 /)'), reply_menu_handler, block=False))
    # 移除单独注册的循环，改为统一由 dynamic_command_dispatcher 处理
    # 它可以处理：
    # 1. 动态/静态注册的指令 (例如 /myfile, /mycmd)
    # 2. 直接输入的文件路径
    # 3. 未知指令
    bot.add_handler(MessageHandler(filters.ALL, dynamic_command_dispatcher, block=False))
    bot.add_error_handler(error_handler)
    logger.info("机器人已启动...")
    bot.run_polling()


if __name__ == '__main__':
    main()
