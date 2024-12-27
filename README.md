# 五子棋游戏

一个基于Pygame实现的五子棋游戏，支持人人对战和人机对战模式，具有三个AI难度级别。

## 功能特点

- 支持人人对战和人机对战
- 三种AI难度级别（简单/一般/困难）
- 实时显示游戏时间和当前玩家
- 黑白棋子交替落子
- 自动判定胜负
- 支持重新开始和返回主菜单

## 技术实现

### 核心架构

项目主要包含两个核心类：
1. `Game`类：负责游戏主逻辑和界面渲染
2. `AI`类：实现人机对战的AI逻辑

### AI实现思路

AI采用评估函数方法，根据不同难度级别采用不同的策略：

#### 简单难度
- 检查是否有直接获胜机会
- 检查是否需要阻止对手直接获胜
- 在已有棋子周围随机选择位置落子
- 适合初学者，具有基本对抗性但判断能力有限

#### 中等难度
- 评估每个可能的落子位置
- 同时考虑进攻和防守价值
- 进攻权重略高于防守
- 具有一定预判能力

#### 困难难度
- 全面评估所有可能位置
- 综合考虑进攻、防守和棋型
- 优先选择靠近已有棋子的位置
- 具有较强的预判和对抗能力

### 评估函数设计

评估函数通过以下因素计算每个位置的分数：
1. 连子数量（2子、3子、4子、5子）
2. 两端是否被封堵
3. 与已有棋子的距离
4. 进攻和防守的权重

分数设置：
- 五连：100000分
- 活四：10000分
- 冲四：1000分
- 活三：1000分
- 眠三：100分
- 活二：100分
- 眠二：10分

### 界面实现

使用Pygame实现图形界面：
- 棋盘大小：15x15
- 动态显示当前玩家和游戏模式
- 实时计时器
- AI落子添加随机延时，提升游戏体验

## 操作说明

1. 运行游戏后，首先进入模式选择界面
2. 选择游戏模式：
   - 人人对战
   - 人机对战-简单
   - 人机对战-一般
   - 人机对战-困难
3. 游戏操作：
   - 鼠标左键：落子
   - ESC键：返回主菜单
   - 空格键：游戏结束后重新开始

## 依赖要求

- Python 3.x
- Pygame