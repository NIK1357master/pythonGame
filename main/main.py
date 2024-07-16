import tkinter as tk
import random

GRID_SIZE = 32
CELL_SIZE = 20
PLAYER_COLOR = "blue"
ENEMY_COLOR = "red"
HUD_HEIGHT = 40
ENEMY_SPAWN_RATE = 10

class Game:
    def __init__(self, master):
        self.master = master
        self.master.title("Игра на выживание")

        self.health = 3
        self.moves_left = 100
        self.turn_count = 0

        self.attack_mode = None
        self.attack_direction = None
        self.cooldowns = {'A': 0, 'S': 0, 'D': 0}

        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack()

        self.top_hud = tk.Canvas(self.main_frame, width=GRID_SIZE*CELL_SIZE, height=HUD_HEIGHT)
        self.top_hud.pack()

        self.canvas = tk.Canvas(self.main_frame, width=GRID_SIZE*CELL_SIZE, height=GRID_SIZE*CELL_SIZE)
        self.canvas.pack()

        self.bottom_hud = tk.Canvas(self.main_frame, width=GRID_SIZE*CELL_SIZE, height=HUD_HEIGHT)
        self.bottom_hud.pack()

        self.player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]
        self.enemies = []

        self.draw_grid()
        self.draw_player()
        self.update_hud()

    def draw_grid(self):
        self.canvas.delete("grid")
        for i in range(0, GRID_SIZE*CELL_SIZE, CELL_SIZE):
            self.canvas.create_line(i, 0, i, GRID_SIZE*CELL_SIZE, fill="gray", tags="grid")
            self.canvas.create_line(0, i, GRID_SIZE*CELL_SIZE, i, fill="gray", tags="grid")

    def draw_player(self):
        x, y = self.player_pos
        self.canvas.create_rectangle(x*CELL_SIZE, y*CELL_SIZE, 
                                     (x+1)*CELL_SIZE, (y+1)*CELL_SIZE, 
                                     fill=PLAYER_COLOR, tags="player")

    def draw_enemies(self):
        self.canvas.delete("enemies")
        for enemy in self.enemies:
            x, y = enemy
            self.canvas.create_rectangle(x*CELL_SIZE, y*CELL_SIZE, 
                                         (x+1)*CELL_SIZE, (y+1)*CELL_SIZE, 
                                         fill=ENEMY_COLOR, tags="enemies")

    def spawn_enemy(self):
        while True:
            x = random.randint(0, GRID_SIZE-1)
            y = random.randint(0, GRID_SIZE-1)
            if [x, y] != self.player_pos and [x, y] not in self.enemies:
                return [x, y]

    def move_enemies(self):
        for i, enemy in enumerate(self.enemies):
            dx = self.player_pos[0] - enemy[0]
            dy = self.player_pos[1] - enemy[1]

            if abs(dx) > abs(dy):
                move_x = 1 if dx > 0 else -1
                move_y = 0
            else:
                move_x = 0
                move_y = 1 if dy > 0 else -1

            new_x = enemy[0] + move_x
            new_y = enemy[1] + move_y

            self.enemies[i] = [new_x, new_y]

    def check_collision(self):
        if self.player_pos in self.enemies:
            self.health -= 1
            self.enemies = [enemy for enemy in self.enemies if enemy != self.player_pos]
            if self.health <= 0:
                self.game_over()

    def game_over(self):
        self.canvas.delete("all")
        self.canvas.create_text(GRID_SIZE*CELL_SIZE//2, GRID_SIZE*CELL_SIZE//2, 
                                text="GAME OVER", font=("Arial", 30), fill="red")

    def move_player(self, dx, dy):
        if self.health <= 0 or self.attack_mode:
            return

        self.canvas.delete("all")
        self.draw_grid()

        new_x = max(0, min(GRID_SIZE-1, self.player_pos[0] + dx))
        new_y = max(0, min(GRID_SIZE-1, self.player_pos[1] + dy))
        self.player_pos = [new_x, new_y]

        self.turn_count += 1
        self.moves_left -= 1

        if self.turn_count % ENEMY_SPAWN_RATE == 0:
            self.enemies.append(self.spawn_enemy())

        self.move_enemies()
        self.check_collision()

        self.draw_grid()
        self.update_hud()

        self.draw_player()
        self.draw_enemies()

        for key in self.cooldowns:
            if self.cooldowns[key] > 0:
                self.cooldowns[key] -= 1

    def update_hud(self):
        #верхний HUD
        self.top_hud.delete("all")
        hud_width = GRID_SIZE * CELL_SIZE
        half_width = hud_width // 2

        self.top_hud.create_line(half_width, 0, half_width, HUD_HEIGHT, fill="black")

        for i in range(3):
            color = "red" if i < self.health else "gray"
            self.top_hud.create_oval(10 + i*30, 10, 30 + i*30, 30, fill=color)

        self.top_hud.create_text(half_width + half_width//2, HUD_HEIGHT//2, 
                                 text=f"Ходов: {self.moves_left}", font=("Arial", 12))

        #нижний HUD
        self.bottom_hud.delete("all")
        section_width = hud_width // 3
        attack_types = ['A', 'S', 'D']

        for i, attack_type in enumerate(attack_types):
            # Определяем цвет фона ячейки
            if self.attack_mode == attack_type:
                bg_color = "yellow"  # Подсветка выбранной атаки
            elif self.cooldowns[attack_type] > 0:
                bg_color = "light gray"  # Атака на перезарядке
            else:
                bg_color = "white"  # Атака доступна

            self.bottom_hud.create_rectangle(i*section_width, 0, (i+1)*section_width, HUD_HEIGHT, 
                                             fill=bg_color, outline="black")

            self.bottom_hud.create_text(i*section_width + section_width//2, HUD_HEIGHT//4, 
                                        text=attack_type, font=("Arial", 14, "bold"))

            if self.cooldowns[attack_type] > 0:
                self.bottom_hud.create_text(i*section_width + section_width//2, 3*HUD_HEIGHT//4, 
                                            text=f"CD: {self.cooldowns[attack_type]}", font=("Arial", 10))

        # Отображаем направление атаки, если выбран режим атаки
        if self.attack_mode and self.attack_direction:
            direction_text = f"Направление: {self.attack_direction}"
            self.bottom_hud.create_text(hud_width//2, HUD_HEIGHT//2, text=direction_text, font=("Arial", 10))

    def enter_attack_mode(self, attack_type):
        if self.cooldowns[attack_type] == 0:
            if self.attack_mode == attack_type:
                # Выход из режима атаки, если нажата та же клавиша
                self.attack_mode = None
                self.attack_direction = None
            else:
                # Вход в режим или переключение между режимами
                self.attack_mode = attack_type
                if not self.attack_direction:
                    self.attack_direction = 'Up'  # По умолчанию

    def change_attack_direction(self, direction):
        if self.attack_mode:
            self.attack_direction = direction
            self.draw_grid()

    def perform_attack(self):
        if not self.attack_mode or not self.attack_direction:
            return

        affected_cells = self.get_affected_cells()
        for cell in affected_cells:
            if cell in self.enemies:
                self.enemies.remove(cell)

        if self.attack_mode == 'D' and self.attack_direction:
            self.player_pos = affected_cells[-1]

        self.cooldowns[self.attack_mode] = {'A': 3, 'S': 2, 'D': 5}[self.attack_mode]
        self.attack_mode = None
        self.attack_direction = None
        self.draw_grid()

    def get_affected_cells(self):
        x, y = self.player_pos
        affected_cells = []

        if self.attack_mode == 'A':
            if self.attack_direction == 'Up':
                affected_cells = [(x-1, y-1), (x, y-1), (x+1, y-1), (x+1, y)]
            elif self.attack_direction == 'Right':
                affected_cells = [(x+1, y-1), (x+1, y), (x+1, y+1), (x, y+1)]
            elif self.attack_direction == 'Down':
                affected_cells = [(x-1, y+1), (x, y+1), (x+1, y+1), (x-1, y)]
            elif self.attack_direction == 'Left':
                affected_cells = [(x-1, y-1), (x-1, y), (x-1, y+1), (x, y-1)]

        elif self.attack_mode == 'S':
            if self.attack_direction == 'Up':
                affected_cells = [(x-1, y), (x-1, y-1), (x, y-1)]
            elif self.attack_direction == 'Right':
                affected_cells = [(x, y-1), (x+1, y-1), (x+1, y)]
            elif self.attack_direction == 'Down':
                affected_cells = [(x+1, y), (x+1, y+1), (x, y+1)]
            elif self.attack_direction == 'Left':
                affected_cells = [(x, y+1), (x-1, y+1), (x-1, y)]

        elif self.attack_mode == 'D':
            if self.attack_direction == 'Up':
                affected_cells = [(x, y-1), (x, y-2), (x, y-3), (x, y-4)]
            elif self.attack_direction == 'Right':
                affected_cells = [(x+1, y), (x+2, y), (x+3, y), (x+4, y)]
            elif self.attack_direction == 'Down':
                affected_cells = [(x, y+1), (x, y+2), (x, y+3), (x, y+4)]
            elif self.attack_direction == 'Left':
                affected_cells = [(x-1, y), (x-2, y), (x-3, y), (x-4, y)]

        return [(x, y) for x, y in affected_cells if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE]

    def draw_attack_preview(self):
        if self.attack_mode and self.attack_direction:
            affected_cells = self.get_affected_cells()
            for x, y in affected_cells:
                self.canvas.create_line(x*CELL_SIZE, y*CELL_SIZE, 
                                        (x+1)*CELL_SIZE, (y+1)*CELL_SIZE, 
                                        fill="red", width=2)
                self.canvas.create_line(x*CELL_SIZE, (y+1)*CELL_SIZE, 
                                        (x+1)*CELL_SIZE, y*CELL_SIZE, 
                                        fill="red", width=2)

    def key_press(self, event):
        if event.char in ['a', 's', 'd']:
            self.enter_attack_mode(event.char.upper())
        elif event.keysym in ["Up", "Down", "Left", "Right"]:
            if self.attack_mode:
                self.change_attack_direction(event.keysym)
            else:
                dx = {"Left": -1, "Right": 1}.get(event.keysym, 0)
                dy = {"Up": -1, "Down": 1}.get(event.keysym, 0)
                self.move_player(dx, dy)
        elif event.keysym == "space":
            self.perform_attack()

root = tk.Tk()
game = Game(root)
root.bind("<KeyPress>", game.key_press)
root.mainloop()
    
