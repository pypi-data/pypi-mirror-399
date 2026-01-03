from nonebot import on_command
from nonebot.plugin import PluginMetadata
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters import Message
from nonebot.matcher import Matcher
from nonebot.log import logger

from .data_source import get_bf6_stats
from .models import BF6Stats

__plugin_meta__ = PluginMetadata(
    name="战地6战绩查询",
    description="查询BF6 玩家战绩信息",
    usage="指令：/bf6 [玩家ID]\n示例：/bf6 piptives",
    type="application",
    homepage="https://github.com/Xfjie314/nonebot-plugin-bf6-stats",
    config=Config,
    supported_adapters={"~onebot.v11", "~console"},
)

# 注册指令
bf6_matcher = on_command("战地6", aliases={"bf6", "BF6"}, priority=5, block=True)

@bf6_matcher.handle()
async def handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    plain_text = args.extract_plain_text().strip()
    if plain_text:
        matcher.set_arg("player_name", args)

@bf6_matcher.got("player_name", prompt="请输入要查询的战地6玩家ID (PC平台)：")
async def handle_query(player_name: str = ArgPlainText("player_name")):
    if not player_name.strip():
        await bf6_matcher.reject("ID不能为空，请重新输入！")

    await bf6_matcher.send(f"正在前往 Gametools 查询 {player_name} ...")

    try:
        # 获取真实数据
        stats = await get_bf6_stats(player_name)

        # 构造详细回复 
        msg = (
            f"📊 战地6 战绩报告\n"
            f"━━━━━━━━━━━━━━\n"
            f"🆔 玩家: {stats.user_name}\n"
            f"⏳ 时长: {stats.time_played_str}\n"
            f"🔫 最佳兵种: {stats.best_class}\n"
            f"━━━━━━━━━━━━━━\n"
            f"【核心数据】\n"
            f"K/D 比: {stats.kill_death:.2f}\n"
            f"KPM   : {stats.kills_per_minute:.2f}\n"
            f"胜率  : {stats.win_rate_display}\n"
            f"准确度: {stats.accuracy}\n"
            f"步战KD: {stats.infantry_kd:.2f}\n"
            f"━━━━━━━━━━━━━━\n"
            f"【详细统计】\n"
            f"击杀: {stats.kills} | 死亡: {stats.deaths}\n"
            f"胜场: {stats.wins} | 败场: {stats.loses}\n"
            f"协助: {stats.assists} | 爆头: {stats.headshots}\n"
            f"急救: {stats.revives} | 治疗: {stats.heals}\n"
            f"修理: {stats.repairs} | 局数: {stats.rounds}\n"
            f"━━━━━━━━━━━━━━\n"
            f"数据来源: Gametools.network"
        )
        
        await bf6_matcher.send(msg)
        return

    except ValueError:
        # 对应 404
        await bf6_matcher.finish(f"❌ 未找到玩家 [{player_name}]，请确认ID是否正确或是否开启了数据公开。")
    except RuntimeError as e:
        # 网络或API错误
        await bf6_matcher.finish(f"⚠️ 查询失败: 连接服务器超时或接口异常。")
    except Exception as e:
        logger.error(f"未知错误: {e}")
        await bf6_matcher.finish("🚫 发生未知错误，请检查后台日志。")