from pydantic import BaseModel, Field

class BF6Stats(BaseModel):
    # --- 基础信息 ---
    user_name: str = Field(alias="userName")      # 玩家ID
    rank: int = Field(default=0)                  # 等级 (API可能没有返回这个，设默认值)
    avatar: str = Field(default="")               # 头像URL
    
    # --- 核心数据 ---
    kill_death: float = Field(alias="killDeath")          # K/D
    kills_per_minute: float = Field(alias="killsPerMinute") # KPM
    win_percent: str = Field(alias="winPercent")          # 胜率 (API返回通常是 "56.59%")
    accuracy: str = Field(default="0%")                   # 准度
    best_class: str = Field(alias="bestClass", default="Unknown") # 最佳兵种
    
    # --- 详细数据 ---
    kills: int = Field(default=0)       # 击杀
    deaths: int = Field(default=0)      # 死亡
    assists: int = Field(alias="killAssists", default=0) # 协助
    
    headshots: int = Field(alias="headShots", default=0) # 爆头数
    headshot_rate: str = Field(alias="headshots", default="0%") # 爆头率 (注意API字段可能是小写)
    
    wins: int = Field(default=0)        # 胜场
    loses: int = Field(default=0)       # 败场
    rounds: int = Field(alias="roundsPlayed", default=0) # 总局数
    
    revives: int = Field(default=0)     # 急救数
    heals: int = Field(default=0)       # 治疗分/量
    repairs: int = Field(default=0)     # 修理分/量
    infantry_kd: float = Field(alias="infantryKillDeath", default=0.0) # 步战KD
    
    seconds_played: float = Field(alias="secondsPlayed", default=0) # 游玩秒数

    # --- 辅助方法：格式化游玩时间 ---
    @property
    def time_played_str(self) -> str:
        seconds = int(self.seconds_played)
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        if days > 0:
            return f"{days}天 {hours}小时"
        return f"{hours}小时"

    # --- 辅助方法：处理可能的百分比格式 ---
    # 有些API返回是 0.56，有些是 "56%"，这里统一处理显示
    @property
    def win_rate_display(self) -> str:
        return str(self.win_percent).replace("%", "") + "%"