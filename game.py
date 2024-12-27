import pygame
import sys
import time
import random

# 初始化Pygame
pygame.init()

# 常量定义
WINDOW_SIZE = 800  # 窗口大小
BOARD_SIZE = 15    # 棋盘大小 15x15
GRID_SIZE = 40     # 每个格子的大小
PIECE_SIZE = 18    # 棋子大小
MARGIN = (WINDOW_SIZE - (BOARD_SIZE - 1) * GRID_SIZE) // 2  # 边距

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (205, 133, 63)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 创建窗口
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("五子棋")

# 初始化字体
pygame.font.init()
font = pygame.font.SysFont('SimHei', 24)  # 设置字体

class AI:
    def __init__(self, difficulty):
        self.difficulty = difficulty  # 'easy', 'medium', 'hard'
        
    def evaluate_position(self, board, x, y, player):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        score = 0
        
        for dx, dy in directions:
            count = 1
            block = 0
            
            # 正向检查
            tx, ty = x + dx, y + dy
            while 0 <= tx < BOARD_SIZE and 0 <= ty < BOARD_SIZE:
                if board[tx][ty] == player:
                    count += 1
                elif board[tx][ty] is None:
                    break
                else:
                    block += 1
                    break
                tx += dx
                ty += dy
            
            # 反向检查
            tx, ty = x - dx, y - dy
            while 0 <= tx < BOARD_SIZE and 0 <= ty < BOARD_SIZE:
                if board[tx][ty] == player:
                    count += 1
                elif board[tx][ty] is None:
                    break
                else:
                    block += 1
                    break
                tx -= dx
                ty -= dy
            
            # 评分
            if count >= 5:
                score += 100000
            elif count == 4:
                if block == 0:
                    score += 10000
                elif block == 1:
                    score += 1000
            elif count == 3:
                if block == 0:
                    score += 1000
                elif block == 1:
                    score += 100
            elif count == 2:
                if block == 0:
                    score += 100
                elif block == 1:
                    score += 10
            
        return score
    
    def get_move(self, game):
        empty_positions = [(i, j) for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) 
                          if game.board[i][j] is None]
        
        if not empty_positions:
            return None
            
        if self.difficulty == 'easy':
            # 简单难度：
            # 1. 检查自己是否能直接获胜
            # 2. 检查对手是否能直接获胜并阻止
            # 3. 在已有棋子周围随机选择一个位置
            
            # 检查获胜机会
            for i, j in empty_positions:
                # 检查AI是否能赢
                game.board[i][j] = 'white'
                if game.check_win(i, j):
                    game.board[i][j] = None
                    return (i, j)
                # 检查玩家是否能赢
                game.board[i][j] = 'black'
                if game.check_win(i, j):
                    game.board[i][j] = None
                    return (i, j)
                game.board[i][j] = None
            
            # 在已有棋子周围随机选择一个位置
            near_positions = []
            for i, j in empty_positions:
                has_neighbor = False
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if 0 <= i + dx < BOARD_SIZE and 0 <= j + dy < BOARD_SIZE:
                            if game.board[i + dx][j + dy] is not None:
                                has_neighbor = True
                                break
                    if has_neighbor:
                        break
                if has_neighbor:
                    near_positions.append((i, j))
            
            # 如果有邻近位置，从中随机选择；否则完全随机选择
            return random.choice(near_positions) if near_positions else random.choice(empty_positions)
            
        elif self.difficulty == 'medium':
            # 评估每个位置，但只看较少的步数
            best_score = -float('inf')
            best_move = None
            for i, j in empty_positions:
                score = self.evaluate_position(game.board, i, j, 'white')
                # 同时考虑防守
                score += self.evaluate_position(game.board, i, j, 'black') * 0.8
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
            return best_move
            
        else:  # hard
            # 评估所有位置，考虑进攻和防守
            best_score = -float('inf')
            best_move = None
            for i, j in empty_positions:
                attack_score = self.evaluate_position(game.board, i, j, 'white')
                defense_score = self.evaluate_position(game.board, i, j, 'black')
                score = attack_score + defense_score * 0.9
                
                # 在邻近位置加分
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if 0 <= i + dx < BOARD_SIZE and 0 <= j + dy < BOARD_SIZE:
                            if game.board[i + dx][j + dy] is not None:
                                score += 10
                
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
            return best_move

class Game:
    def __init__(self):
        self.ai = None
        self.game_mode = None
        self.show_menu = True
        self.reset_game()
    
    def reset_game(self):
        self.board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'black'  # 黑子先手
        self.game_over = False
        self.start_time = time.time()
        self.elapsed_time = 0
    
    def draw_menu(self):
        screen.fill(BROWN)
        title = font.render("五子棋", True, BLACK)
        screen.blit(title, (WINDOW_SIZE//2 - 50, 100))
        
        modes = [
            ("人人对战", "pvp"),
            ("人机对战-简单", "easy"),
            ("人机对战-一般", "medium"),
            ("人机对战-困难", "hard")
        ]
        
        for i, (text, mode) in enumerate(modes):
            color = BLUE if self.check_mouse_on_button(i) else BLACK
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(WINDOW_SIZE//2, 250 + i * 60))
            screen.blit(text_surface, text_rect)
    
    def check_mouse_on_button(self, button_index):
        mouse_pos = pygame.mouse.get_pos()
        button_y = 250 + button_index * 60
        return (WINDOW_SIZE//2 - 100 <= mouse_pos[0] <= WINDOW_SIZE//2 + 100 and
                button_y - 20 <= mouse_pos[1] <= button_y + 20)
    
    def handle_menu_click(self):
        mouse_pos = pygame.mouse.get_pos()
        for i, mode in enumerate(["pvp", "easy", "medium", "hard"]):
            button_y = 250 + i * 60
            if (WINDOW_SIZE//2 - 100 <= mouse_pos[0] <= WINDOW_SIZE//2 + 100 and
                button_y - 20 <= mouse_pos[1] <= button_y + 20):
                self.game_mode = mode
                if mode != "pvp":
                    self.ai = AI(mode)
                self.show_menu = False
                self.reset_game()
                return True
        return False
        
    def draw_board(self):
        # 填充棋盘背景色
        screen.fill(BROWN)
        
        # 绘制棋盘线
        for i in range(BOARD_SIZE):
            # 横线
            pygame.draw.line(screen, BLACK,
                           (MARGIN, MARGIN + i * GRID_SIZE),
                           (WINDOW_SIZE - MARGIN, MARGIN + i * GRID_SIZE))
            # 竖线
            pygame.draw.line(screen, BLACK,
                           (MARGIN + i * GRID_SIZE, MARGIN),
                           (MARGIN + i * GRID_SIZE, WINDOW_SIZE - MARGIN))
        
        # 绘制棋子
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == 'black':
                    pygame.draw.circle(screen, BLACK,
                                    (MARGIN + i * GRID_SIZE,
                                     MARGIN + j * GRID_SIZE),
                                    PIECE_SIZE)
                elif self.board[i][j] == 'white':
                    pygame.draw.circle(screen, WHITE,
                                    (MARGIN + i * GRID_SIZE,
                                     MARGIN + j * GRID_SIZE),
                                    PIECE_SIZE)
                    # 为白子添加黑色边框
                    pygame.draw.circle(screen, BLACK,
                                    (MARGIN + i * GRID_SIZE,
                                     MARGIN + j * GRID_SIZE),
                                    PIECE_SIZE, 1)
        
        # 显示当前玩家和模式
        mode_text = "人人对战" if self.game_mode == "pvp" else f"人机对战-{{'easy': '简单', 'medium': '一般', 'hard': '困难'}}[{self.game_mode}]"
        current_player_text = f"当前玩家: {'黑棋' if self.current_player == 'black' else '白棋'} | {mode_text}"
        player_surface = font.render(current_player_text, True, BLACK)
        screen.blit(player_surface, (10, 10))
        
        # 显示游戏时间
        if not self.game_over:
            self.elapsed_time = int(time.time() - self.start_time)
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        time_text = f"游戏时间: {minutes}分{seconds}秒"
        time_surface = font.render(time_text, True, BLACK)
        screen.blit(time_surface, (10, 40))
        
        # 如果游戏结束，显示获胜信息和重新开始提示
        if self.game_over:
            winner = '黑棋' if self.current_player == 'black' else '白棋'
            win_text = f"{winner}获胜！按空格键重新开始，按ESC返回菜单"
            win_surface = font.render(win_text, True, RED)
            text_rect = win_surface.get_rect(center=(WINDOW_SIZE//2, 60))
            screen.blit(win_surface, text_rect)
    
    def get_position(self, pos):
        x, y = pos
        # 将鼠标位置转换为棋盘坐标
        i = round((x - MARGIN) / GRID_SIZE)
        j = round((y - MARGIN) / GRID_SIZE)
        
        # 确保位置在棋盘范围内
        if 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE:
            return i, j
        return None
    
    def place_piece(self, pos):
        if self.game_over:
            return
            
        position = self.get_position(pos)
        if position:
            i, j = position
            if self.board[i][j] is None:  # 确保该位置没有棋子
                self.board[i][j] = self.current_player
                # 立即重绘棋盘并更新显示
                self.draw_board()
                pygame.display.flip()
                
                if self.check_win(i, j):
                    self.game_over = True
                else:
                    self.current_player = 'white' if self.current_player == 'black' else 'black'
                    # AI回合
                    if not self.game_over and self.game_mode != "pvp" and self.current_player == 'white':
                        time.sleep(random.uniform(0.3, 0.8))  # AI思考时添加随机延时
                        self.ai_move()
    
    def ai_move(self):
        if self.ai:
            move = self.ai.get_move(self)
            if move:
                i, j = move
                self.board[i][j] = 'white'
                if self.check_win(i, j):
                    self.game_over = True
                else:
                    self.current_player = 'black'
    
    def check_win(self, i, j):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 水平、竖直、对角线
        for dx, dy in directions:
            count = 1  # 当前位置的棋子
            # 正向检查
            x, y = i + dx, j + dy
            while 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and \
                  self.board[x][y] == self.current_player:
                count += 1
                x += dx
                y += dy
            # 反向检查
            x, y = i - dx, j - dy
            while 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and \
                  self.board[x][y] == self.current_player:
                count += 1
                x -= dx
                y -= dy
            if count >= 5:
                return True
        return False

def main():
    game = Game()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    if game.show_menu:
                        game.handle_menu_click()
                    else:
                        game.place_piece(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game.game_over:
                    game.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    game.show_menu = True
        
        if game.show_menu:
            game.draw_menu()
        else:
            game.draw_board()
        pygame.display.flip()

if __name__ == "__main__":
    main()
