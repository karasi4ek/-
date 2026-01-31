import arcade
import math
import random


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
SCREEN_TITLE = 'Осада призраков'
PLAYER_SCALING = 0.2
GRAVITY = 0.8
PLAYER_JUMP_SPEED = 22




class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.title_text = arcade.Text('Осада призраков', SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50,
                                      arcade.color.BLACK, font_size=50, anchor_x='center')
        self.start_text = arcade.Text('Нажмите ЛКМ, чтобы начать', SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50,
                                      arcade.color.DARK_BLUE, font_size=20, anchor_x='center')

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DIM_GRAY)




    def on_draw(self):
        self.clear()
        self.title_text.draw()
        self.start_text.draw()



    def on_mouse_press(self, x, y, button, modifiers):
        game_view = MyGame()
        game_view.setup()
        self.window.show_view(game_view)




class MyGame(arcade.View):
    def __init__(self):
        super().__init__()
        self.player = None
        self.scene = None
        self.physics_engine = None
        self.hp = 100
        self.kills = 0
        self.stats_saved = False
        self.hero_speed = 5
        self.puli = []
        self.keys_pressed = set()
        self.wave_count = 1
        self.wave_timer = 0
        self.is_wave_waiting = False
        self.coin_list = arcade.SpriteList()
        self.coins_counter = 0

        self.camera_sprites = arcade.camera.Camera2D()
        self.camera_gui = arcade.camera.Camera2D()
        self.gunshot_sound = arcade.load_sound(r'C:\Users\karas\PycharmProjects\PythonProject\build\Стрелялка\laser1.wav')

        self.gui_score_text = arcade.Text("", 10, 20, arcade.color.BLACK, 16, bold=True)
        self.gui_wave_text = arcade.Text("", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, arcade.color.WHITE, 30, anchor_x='center', bold=True)
        self.gui_game_over_text = arcade.Text("GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, arcade.color.RED, 60, anchor_x='center')




    def setup(self):
        self.puli = []
        self.hp = 100
        self.kills = 0
        self.stats_saved = False
        map_name = r'C:\Users\karas\PycharmProjects\PythonProject\build\Стрелялка\карта_2.tmx'
        self.layer_name = 'Слой тайлов 1'


        self.tile_map = arcade.load_tilemap(map_name, scaling=1.0)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)


        base_tex = arcade.load_texture(r'C:\Users\karas\Documents\Project\Солдат лево.png')
        self.tex_left = base_tex
        self.tex_right = base_tex.flip_left_right()


        self.player = arcade.Sprite()
        self.player.texture = self.tex_left
        self.player.scale = PLAYER_SCALING
        self.player.center_x, self.player.center_y = 200, 102


        self.scene.add_sprite('Player', self.player)
        self.scene.add_sprite_list('Enemies')


        self.spawn_coins()
        self.spawn_enemies(5)



    def spawn_coins(self):
        self.coin_list.clear()



        for _ in range(10):
            coin = arcade.Sprite(r'C:\Users\karas\PycharmProjects\PythonProject\build\Стрелялка\coinGold.png', scale=0.5)
            coin.center_x = random.randint(100, SCREEN_WIDTH * 2)
            coin.center_y = random.randint(150, 400)
            self.coin_list.append(coin)


        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            gravity_constant=GRAVITY,
            walls=self.scene[self.layer_name])






    def spawn_enemies(self, count):
        for _ in range(count):
            enemy = arcade.Sprite(r'C:\Users\karas\PycharmProjects\PythonProject\build\Стрелялка\slimeBlue.png', scale=0.6)
            enemy.center_x = random.randint(0, SCREEN_WIDTH * 2)
            enemy.center_y = random.randint(500, SCREEN_HEIGHT + 300)
            self.scene.add_sprite('Enemies', enemy)




    def on_draw(self):
        self.clear()
        with self.camera_sprites.activate():
            self.coin_list.draw()
            self.scene.draw()
            for bullet in self.puli:
                arcade.draw_circle_filled(bullet['x'], bullet['y'], 4, arcade.color.BLACK)


        with self.camera_gui.activate():
            self.gui_score_text.draw()
            if self.is_wave_waiting:
                self.gui_wave_text.draw()
            if self.hp <= 0:
                self.gui_game_over_text.draw()




    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        if key == arcade.key.W or key == arcade.key.UP or key == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED




    def on_key_release(self, key, modifiers):
        self.keys_pressed.discard(key)




    def on_update(self, delta_time):
        target_x = self.player.center_x
        target_y = max(self.player.center_y, SCREEN_HEIGHT / 2)
        self.camera_sprites.position = (arcade.math.lerp(self.camera_sprites.position.x, target_x, 0.1),
                                        arcade.math.lerp(self.camera_sprites.position.y, target_y, 0.1))


        if self.hp <= 0:
            if not self.stats_saved:
                with open('статистика.txt', 'w', encoding="utf-8") as file:
                    file.write(f'ИГРА ОКОНЧЕНА\nВсего убито врагов: {self.kills}\nДостигнуто волн: {self.wave_count}\nМонет собрано: {self.coins_counter}')
                self.stats_saved = True
            return


        self.player.change_x = 0
        if arcade.key.D in self.keys_pressed or arcade.key.RIGHT in self.keys_pressed:
            self.player.change_x = self.hero_speed
            self.player.texture = self.tex_left
        elif arcade.key.A in self.keys_pressed or arcade.key.LEFT in self.keys_pressed:
            self.player.change_x = -self.hero_speed
            self.player.texture = self.tex_right


        coins_hit_list = arcade.check_for_collision_with_list(self.player, self.coin_list)


        for coin in coins_hit_list:
            coin.remove_from_sprite_lists()
            self.coins_counter += 1


        self.physics_engine.update()


        for b in self.puli[:]:
            b['x'] += b['dx'] * delta_time;
            b['y'] += b['dy'] * delta_time;
            b['life'] -= delta_time
            hits = arcade.get_sprites_at_point((b['x'], b['y']), self.scene['Enemies'])
            if hits:
                for e in hits:
                    e.remove_from_sprite_lists()
                    self.kills += 1
                if b in self.puli: self.puli.remove(b)
            elif b['life'] <= 0:
                if b in self.puli: self.puli.remove(b)


        for enemy in self.scene['Enemies']:
            angle = math.atan2(self.player.center_y - enemy.center_y, self.player.center_x - enemy.center_x)
            enemy.center_x += math.cos(angle) * 130 * delta_time
            enemy.center_y += math.sin(angle) * 130 * delta_time
            if arcade.check_for_collision(self.player, enemy):
                self.hp -= 40 * delta_time


        if len(self.scene['Enemies']) == 0 and not self.is_wave_waiting:
            self.is_wave_waiting, self.wave_timer = True, 3.0
        if self.is_wave_waiting:
            self.wave_timer -= delta_time
            if self.wave_timer <= 0:
                self.is_wave_waiting = False
                self.wave_count += 1
                self.spawn_enemies(5 + (self.wave_count * 2))
                self.spawn_coins()

        self.gui_score_text.text = f'Волна: {self.wave_count} | Убито: {self.kills} | Враги: {len(self.scene["Enemies"])} | Монеты: {self.coins_counter} | HP: {int(self.hp)}'
        if self.is_wave_waiting:
            self.gui_wave_text.text = f'НОВАЯ ВОЛНА ЧЕРЕЗ: {int(self.wave_timer) + 1}'




    def on_mouse_press(self, x, y, button, modifiers):
        if self.hp > 0:
            arcade.play_sound(self.gunshot_sound, volume=0.2)
            world_pos = self.camera_sprites.unproject((x, y))
            target_x = world_pos.x
            target_y = world_pos.y
            angle = math.atan2(target_y - self.player.center_y, target_x - self.player.center_x)
            self.puli.append({'x': self.player.center_x, 'y': self.player.center_y,
                              'dx': math.cos(angle) * 750, 'dy': math.sin(angle) * 750, 'life': 2.0})




def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(MenuView())
    arcade.run()


if __name__ == "__main__":
    main()