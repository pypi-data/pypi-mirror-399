# -*- coding: utf-8 -*-
import asyncio
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    BotCommand
)
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler, Application

from .utils import logger, reply_message_safely, send_doc_safely, fetch_ip_text, check_file_exist
from .config import Config
from .decorators import authorized_only


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
        await update.message.reply_text(f"⏳ 正在执行: {command}")
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
    if not shell_cmd:
        return
    try:
        await update.message.reply_text(f"⏳ 正在执行: {shell_cmd}")
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
    if not update.message.text:
        return
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


@authorized_only
async def get_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """获取服务器 IP 地址"""
    is_ipv6 = 'ipv6' in update.message.text.lower()
    text = await fetch_ip_text(is_ipv6)
    await reply_message_safely(update, text=text)