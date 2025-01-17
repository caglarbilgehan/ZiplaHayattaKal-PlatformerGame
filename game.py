import pgzrun
import random


class Game:
    def __init__(self):
        self.WIDTH = 800
        self.HEIGHT = 600
        self.music_on = True
        self.music_played = False

    def toggle_music(self):
        self.music_on = not self.music_on
        if self.music_on:
            sounds.game_music.play(loops=True)
            sounds.game_music.set_volume(0.15)
        else:
            sounds.game_music.stop()

    def update_music(self):
        if self.music_on and not self.music_played:
            sounds.game_music.play(loops=True)
            sounds.game_music.set_volume(0.15)
            self.music_played = True
        elif not self.music_on and self.music_played:
            sounds.game_music.stop()
            self.music_played = False

    def draw_game_screen(self, hero):
        screen.blit("arkaplan", (0, 0))
        self.draw_health_bar(hero)
        screen.draw.text(f"Puan: {hero.score}", topright=(self.WIDTH - 20, 15), fontsize=30, color="white")
        hero.draw()

    def draw_health_bar(self, hero):
        bar_width = 200
        bar_height = 20
        bar_x = (self.WIDTH - bar_width) // 2
        bar_y = 10
        health_ratio = hero.health / hero.max_health
        screen.draw.filled_rect(Rect(bar_x, bar_y, bar_width, bar_height), "red")
        screen.draw.filled_rect(Rect(bar_x, bar_y, bar_width * health_ratio, bar_height), "green")
        screen.draw.text(f"CAN DEĞERİ: {hero.health}/{hero.max_health}", center=(self.WIDTH // 2, bar_y + bar_height // 2), fontsize=20, color="black")

# Oyun nesnesi
game = Game()

# Kahraman sınıfı
class Hero:
    def __init__(self):
        self.actor = Actor("player_idle_0")
        self.actor.x = game.WIDTH / 2
        self.ground_y = game.HEIGHT - 122
        self.actor.y = self.ground_y
        self.is_jumping = False
        self.jump_speed = 0
        self.gravity = 1.4
        self.jump_height = 30
        self.health = 100
        self.max_health = 100
        self.walk_left_anim = ["player_walk_left_1", "player_walk_left_2"]
        self.walk_right_anim = ["player_walk_right_1", "player_walk_right_2"]
        self.idle_anim = ["player_idle_1", "player_idle_2", "player_idle_3"]  # Boş durma animasyonu için kareler
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_time = 10
        self.footstep_counter = 0  # Adım sesi için zamanlayıcı
        self.footstep_time = 14   # Adım sesinin kaç ms'de bir çalacağı
        self.jump_left_image = "player_jump_left"
        self.jump_right_image = "player_jump_right"
        self.jump_idle_image = "player_jump"
        self.score = 0
        self.idle_timer = 0  # Kahramanın boş durma süresi için zamanlayıcı
        self.idle_time_threshold = 1  # Boş durma animasyonu için süre eşiği (örneğin, 60 frame)

    def draw(self):
        self.actor.draw()

    def update(self):
        self.move_logic()
        self.jump_logic()
        self.idle_logic()

    def move_logic(self):
        if keyboard.left or keyboard.a:
            self.actor.x -= 5
            if not self.is_jumping:
                self.animate_walk(self.walk_left_anim)
            else:
                self.actor.image = self.jump_left_image
            if not self.is_jumping:
                self.play_footstep()
            self.idle_timer = 0  # Kahraman hareket ettiğinde idle timer sıfırlanır

        elif keyboard.right or keyboard.d:
            self.actor.x += 5
            if not self.is_jumping:
                self.animate_walk(self.walk_right_anim)
            else:
                self.actor.image = self.jump_right_image
            if not self.is_jumping:
                self.play_footstep()
            self.idle_timer = 0  # Kahraman hareket ettiğinde idle timer sıfırlanır

        # Ekran sınırlarını kontrol et
        if self.actor.x < 0:
            self.actor.x = 0
        elif self.actor.x > game.WIDTH:
            self.actor.x = game.WIDTH

    def jump_logic(self):
        if self.is_jumping:
            self.actor.y -= self.jump_speed
            self.jump_speed -= self.gravity
            if self.actor.y >= self.ground_y:
                self.actor.y = self.ground_y
                self.is_jumping = False
                self.actor.image = "player_idle_0"
                if game.music_on:
                    sounds.jump_end.play()  # Yere düşme sesi çal
        elif keyboard.space and not self.is_jumping:
            self.is_jumping = True
            self.jump_speed = self.jump_height
            if keyboard.left or keyboard.a:
                self.actor.image = self.jump_left_image
            elif keyboard.right or keyboard.d:
                self.actor.image = self.jump_right_image
            else:
                self.actor.image = self.jump_idle_image
            if game.music_on:
                sounds.jump_start.play()  # Zıplama sesi çal

    def animate_walk(self, anim_list):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_time:
            self.current_frame = (self.current_frame + 1) % len(anim_list)
            self.actor.image = anim_list[self.current_frame]
            self.frame_counter = 0

    def idle_logic(self):
        if not keyboard.left and not keyboard.right and not keyboard.a and not keyboard.d and not self.is_jumping:
            self.idle_timer += 1
            if self.idle_timer >= self.idle_time_threshold:
                self.animate_walk(self.idle_anim)
        else:
            self.idle_timer = 0

    def play_footstep(self):
        self.footstep_counter += 1
        if game.music_on and self.footstep_counter >= self.footstep_time:
            sounds.footstep.play()
            self.footstep_counter = 0

# Kahraman nesnesi
hero = Hero()


# Örümcek düşman sınıfı
class Spider:
    def __init__(self, side):
        self.walk_left_anim = ["spider_walk_left_1", "spider_walk_left_2"]
        self.walk_right_anim = ["spider_walk_right_1", "spider_walk_right_2"]
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_time = 10  # Animasyon hızı
        self.actor = Actor(self.walk_left_anim[self.current_frame])
        self.side = side
        self.actor.y = hero.ground_y + 30

        if side == "left":
            self.actor.x = 0
            self.speed = random.randint(2, 3)
        else:  # "right"
            self.actor.x = game.WIDTH
            self.speed = -random.randint(2, 3)

    def draw(self):
        self.actor.draw()

    def update(self):
        self.animate_walk()
        self.actor.x += self.speed
        if self.side == "left" and self.actor.x > game.WIDTH:
            self.reset_position()
        elif self.side == "right" and self.actor.x < 0:
            self.reset_position()

    def reset_position(self):
        if self.side == "left":
            self.actor.x = 0
        else:
            self.actor.x = game.WIDTH
        self.actor.y = hero.ground_y + 30

    def animate_walk(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_time:
            self.current_frame = (self.current_frame + 1) % len(self.walk_left_anim)
            if self.speed > 0:
                self.actor.image = self.walk_left_anim[self.current_frame]
            else:
                self.actor.image = self.walk_right_anim[self.current_frame]
            self.frame_counter = 0

# Örümcek düşmanları listesi
spiders = []

# Yeni örümcek oluşturma
def create_spider():
    side = random.choice(["left", "right"])
    spiders.append(Spider(side))

# Zamanlayıcı ile örümcek oluşturma
clock.schedule_interval(create_spider, 3.0)

# Örümcek arı sınıfı
class Bee:
    def __init__(self, side):
        self.walk_left_anim = ["bee_left_fly_1", "bee_left_fly_2"]
        self.walk_right_anim = ["bee_right_fly_1", "bee_right_fly_2"]
        self.current_frame = 0
        self.frame_counter = 0
        self.frame_time = 10  # Animasyon hızı
        self.actor = Actor(self.walk_left_anim[self.current_frame])
        self.side = side
        self.actor.y = random.randint(game.HEIGHT / 5, game.HEIGHT / 2)

        if side == "left":
            self.actor.x = 0
            self.speed = random.randint(2, 3)
        else:  # "right"
            self.actor.x = game.WIDTH
            self.speed = -random.randint(2, 3)

    def draw(self):
        self.actor.draw()

    def update(self):
        self.animate()
        self.actor.x += self.speed
        if self.side == "left" and self.actor.x > game.WIDTH:
            self.reset_position()
        elif self.side == "right" and self.actor.x < 0:
            self.reset_position()

    def reset_position(self):
        if self.side == "left":
            self.actor.x = 0
        else:
            self.actor.x = game.WIDTH
        self.actor.y = hero.ground_y + 30

    def animate(self):
        self.frame_counter += 1
        if self.frame_counter >= self.frame_time:
            self.current_frame = (self.current_frame + 1) % len(self.walk_left_anim)
            if self.speed > 0:
                self.actor.image = self.walk_left_anim[self.current_frame]
            else:
                self.actor.image = self.walk_right_anim[self.current_frame]
            self.frame_counter = 0

# Örümcek düşmanları listesi
bees = []

# Yeni örümcek oluşturma
def create_bee():
    side = random.choice(["left", "right"])
    bees.append(Bee(side))

# Zamanlayıcı ile örümcek oluşturma
clock.schedule_interval(create_bee, 4.0)

class Menu:
    def __init__(self):
        self.active = True
        self.how_to_play_active = False
        self.win_active = False
        self.game_over = False
        self.menu_text_play = "1. Oyuna Başla"
        self.buttons = {
            "play": Rect((game.WIDTH // 2 - 100, game.HEIGHT // 2 - 60), (200, 40)),
            "how_to_play": Rect((game.WIDTH // 2 - 100, game.HEIGHT // 2), (200, 40)),
            "toggle_music": Rect((game.WIDTH // 2 - 100, game.HEIGHT // 2 + 60), (200, 40)),
            "exit": Rect((game.WIDTH // 2 - 100, game.HEIGHT // 2 + 120), (200, 40))
        }

    def draw(self):
        if self.how_to_play_active:
            self.draw_how_to_play()
        else:
            screen.fill("black")

            if self.game_over:
                screen.draw.text("KAYBETTİNİZ!", center=(game.WIDTH // 2, game.HEIGHT // 4 - 50), fontsize=60, color="red")

            if self.win_active:
                screen.draw.text("TEBRİKLER! KAZANDINIZ!", center=(game.WIDTH // 2, game.HEIGHT // 4 - 50), fontsize=60, color="green")

            title_width = game.WIDTH // 2
            title_height = game.HEIGHT // 4
            screen.draw.text("Zıpla ve Hayatta Kal!", center=(title_width, title_height), fontsize=60, color="white")
            screen.draw.text("Platform Oyunu", center=(title_width, title_height + 40), fontsize=40, color="white")

            for name, rect in self.buttons.items():
                color = "white"
                text = ""
                if name == "play":
                    text = "1. Oyuna Başla" if self.game_over or self.win_active else self.menu_text_play
                elif name == "how_to_play":
                    text = "2. Nasıl Oynanır"
                elif name == "toggle_music":
                    text = "3. Sesi Aç/Kapat"
                elif name == "exit":
                    text = "4. Çıkış"
                screen.draw.filled_rect(rect, color)
                screen.draw.text(text, center=rect.center, fontsize=30, color="black")

            screen.draw.text("Oyun Geliştiricisi: Ercüment Çağlar Bilgehan", center=(game.WIDTH // 2, game.HEIGHT - 100), fontsize=30, color="white")

    def draw_how_to_play(self):
        screen.fill("black")
        screen.draw.text("Nasıl Oynanır", center=(game.WIDTH // 2, game.HEIGHT // 6), fontsize=60, color="white")
        instructions = [
            "Klavyedeki YÖN TUŞLARI veya A/D tuşlarıyla hareket edin.",
            "BOŞLUK tuşuna basarak zıplayın.",
            "Örümceklerin ÜZERİNDEN zıplayarak puan kazanın.",
            "Örümceklere yandan çarpmamaya dikkat edin, canınız azalır.",
            "Oyunda en yüksek puanı elde etmeye çalışın!",
            "Bir düşman oyun alanından tamamen çıktığında 1 puan kazanırsın!",
            "20 puana ulaştığında oyunu kazanırsın!"
        ]
        for i, line in enumerate(instructions):
            screen.draw.text(line, center=(game.WIDTH // 2, game.HEIGHT // 4 + i * 40), fontsize=30, color="white")
        screen.draw.text("Ana Menüye dönmek için ESC tuşuna basın.", center=(game.WIDTH // 2, game.HEIGHT - 50), fontsize=30, color="yellow")

    def handle_mouse_down(self, pos):
        for name, rect in self.buttons.items():
            if rect.collidepoint(pos):
                if name == "play":
                    if menu.game_over or menu.win_active:
                        reset_game()  # Oyunu sıfırla
                    self.active = False
                    self.menu_text_play = "1. Devam Et"
                elif name == "how_to_play":
                    self.how_to_play_active = True
                elif name == "toggle_music":
                    game.toggle_music()
                elif name == "exit":
                    exit()

    def handle_key_down(self, key):
        if key == keys.K_1:
            if menu.game_over or menu.win_active:
                reset_game()  # Oyunu sıfırla
            self.active = False
            self.menu_text_play = "1. Devam Et"
        elif key == keys.K_2:
            self.how_to_play_active = True
        elif key == keys.K_3:
            game.toggle_music()
        elif key == keys.K_4:
            exit()

        if key == keys.ESCAPE:
            if self.how_to_play_active:
                self.how_to_play_active = False
            else:
                self.active = True
        
        if self.active:
            game.update_music()

# Menü nesnesi oluştur
menu = Menu()

# draw fonksiyonunu güncelle
def draw():
    if menu.active:
        menu.draw()
    else:
        game.draw_game_screen(hero)
        for spider in spiders:
            spider.draw()
        for bee in bees:
            bee.draw()

# update fonksiyonunu güncelle
def update():
    if menu.active:
        game.update_music()
        return

    hero.update()

    # Örümceklerin güncellenmesi
    for spider in spiders:
        spider.update()

    # Arıların güncellenmesi
    for bee in bees:
        bee.update()

    # Kahraman ve örümcek çarpışma kontrolü
    check_collision(hero, spiders)
    # Kahraman ve örümcek çarpışma kontrolü 
    check_collision(hero, bees)


    if hero.health <= 0:
        menu.game_over = True
        menu.active = True
        return

    if hero.score >= 20:
        menu.win_active = True
        menu.active = True
        return

# Çarpışma Kontrolü
def check_collision(hero, enemies):
    for enemy in enemies:
        if hero.actor.colliderect(enemy.actor):
            sounds.hit.play()
            hero.health -= 10
            # Kahramanın canı sıfırın altına düşmesin
            if hero.health < 0:
                hero.health = 0
            # Çarpışmadan sonra örümceği sil
            enemies.remove(enemy)
        elif enemy.actor.x <= 0 or enemy.actor.x >= game.WIDTH:
            hero.score += 1
            enemies.remove(enemy)

def reset_game():
    # Kahramanın durumunu sıfırla
    hero.health = hero.max_health
    hero.score = 0
    hero.actor.x = game.WIDTH / 2
    hero.actor.y = hero.ground_y
    hero.is_jumping = False

    # Düşman listelerini temizle
    spiders.clear()
    bees.clear()

    # Menü durumlarını sıfırla
    menu.game_over = False
    menu.win_active = False

# Mouse tıklama olayını güncelle
def on_mouse_down(pos):
    if menu.active:
        menu.handle_mouse_down(pos)

# Klavye tuş olayını güncelle
def on_key_down(key):
    if menu.active:
        menu.handle_key_down(key)
    else:
        if key == keys.ESCAPE:
            menu.active = True

pgzrun.go()
