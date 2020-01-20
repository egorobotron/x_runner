import pygame
import os
import sys

os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
size = width, height = (420, 205)
K_OF_RESOLUTHION = min(
    [pygame.display.Info().current_w // width, (pygame.display.Info().current_h - 150) // height])
if K_OF_RESOLUTHION < 1:
    K_OF_RESOLUTHION = 1
elif K_OF_RESOLUTHION > 3:
    K_OF_RESOLUTHION = 3

size = width, height = (width * K_OF_RESOLUTHION, height * K_OF_RESOLUTHION)
screen = pygame.display.set_mode(size)
FPS = 60

DEBUG_ON = False

clock = pygame.time.Clock()


def load_image(name, colorkey=None, need_scale=True):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    if need_scale:
        image = pygame.transform.scale(image, (
            image.get_width() * K_OF_RESOLUTHION, image.get_height() * K_OF_RESOLUTHION))
    return image


def create_image_sheet(name_of_image, number_of_images, colorkey=-1):
    images = []
    for i in range(1, number_of_images + 1):
        name = name_of_image + '_' + str(i) + '.png'
        images.append(load_image(name, colorkey))
    return images


def create_image_sheetseses(names_of_images_with_numbers=[('empty.png', 1, 6)]):
    image_sheetseses = []
    for i in names_of_images_with_numbers:
        if len(i) == 2:
            k = 6
        else:
            k = i[2]
        image_sheetseses.append([create_image_sheet(i[0], i[1]), i[1], k])
    return image_sheetseses  # возвращаетс список с [0] - картинками [1] - кол-во картинок в списке картинок [2] - кол-во кадров задержки


def debug_output(textes):
    font = pygame.font.Font(None, 10 * K_OF_RESOLUTHION)
    text_coord = 10
    for line in textes:
        string_rendered = font.render(str(line), 1, pygame.Color('yellow'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 20
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


if DEBUG_ON:
    tile_images = {'wall': load_image('empty.png', -1), 'empty': load_image('empty.png', -1),
                   'jump_wall': load_image('empty1.png', -1), 'x_wall': load_image('empty2.png', -1),
                   'ladder': load_image('empty3.png', -1), 'trigger': load_image('empty4.png', -1),
                   'v_wall': load_image('empty5.png', -1), 'spikes': load_image('empty6.png', -1)}
else:
    tile_images = {'wall': load_image('empty_0.png', -1), 'empty_0': load_image('empty.png', -1),
                   'jump_wall': load_image('empty_0.png', -1),
                   'x_wall': load_image('empty_0.png', -1),
                   'ladder': load_image('empty_0.png', -1), 'trigger': load_image('empty_0.png', -1),
                   'v_wall': load_image('empty_0.png', -1), 'spikes': load_image('empty_0.png', -1)}
enemy_images = {'wall': load_image('wall.png')}

tile_width = tile_height = 15 * K_OF_RESOLUTHION

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
walls_group = pygame.sprite.Group()
jump_walls_group = pygame.sprite.Group()
x_wall_group = pygame.sprite.Group()
v_wall_group = pygame.sprite.Group()
ladder_group = pygame.sprite.Group()
triger_group = pygame.sprite.Group()
spikes_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


# class Base_Charecter(pygame.sprite.Sprite):
#     def __init__(self, pos_x, pos_y):
#         super().__init__(all_sprites)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.cur_sprite = 0

        self.image_number = 0
        self.last_image_number = 0
        self.image_sheetseses = create_image_sheetseses(
            [('run', 11), ('stand_still', 12, 6), ('jump_on_wall', 5), ('jump_up', 3, 6),
             ('jump_down', 5, 6), ('ladder', 4, 12), ('dead', 12, 6)])
        self.image = self.image_sheetseses[0][0][0]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 0, tile_height * pos_y + 0)
        self.is_in_air = True
        self.delay = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.have_jump = False
        self.directhion = 'r'
        self.is_stand = False
        self.on_wall = False
        self.after_wall = 50
        self.napr_after_wall = 0
        self.on_ladder = False
        self.time = 0
        self.graviti_k = 0.24
        self.level = 1
        self.heath = 10
        self.is_dead = False
        self.must_kill = False

    def move(self, s=(0, 0, 0)):
        if self.on_wall and s[1] == -1:
            self.velocity_x = -s[0] * K_OF_RESOLUTHION * 2
            self.after_wall = 0
            self.velocity_y = -5 * K_OF_RESOLUTHION
        elif self.after_wall < 10 and s[0] == self.napr_after_wall:
            self.velocity_x = -s[0] * K_OF_RESOLUTHION * 2
            self.after_wall += 1
        else:
            self.velocity_x = s[0] * K_OF_RESOLUTHION * 2
            self.after_wall = 50
        if s[1] == -1 and not self.have_jump and not self.on_wall:
            self.velocity_y += -5 * K_OF_RESOLUTHION
            self.have_jump = True
        if s[1] == 1:
            self.rect.y += 1
        if self.on_ladder:
            self.rect.y += s[1] * K_OF_RESOLUTHION
            self.velocity_x = 0
            self.delay = (self.delay + abs(s[1])) % self.image_sheetseses[self.image_number][2]
        if s[0] == 1:
            self.directhion = 'r'
        elif s[0] == -1:
            self.directhion = 'l'
        if self.velocity_y != 0:
            self.is_in_air = True

    def next_sprite(self, sprite_number):
        self.cur_sprite = (self.cur_sprite + 1) % sprite_number

    def update(self):
        if self.last_image_number != self.image_number:
            self.cur_sprite = 0
        self.last_image_number = self.image_number
        if self.image_number in [0, 1, 6]:
            self.delay = (self.delay + 1) % self.image_sheetseses[self.image_number][2]
            if self.delay == self.image_sheetseses[self.image_number][2] - 1:
                self.next_sprite(self.image_sheetseses[self.image_number][1])
                if self.directhion == 'r':
                    self.image = self.image_sheetseses[self.image_number][0][self.cur_sprite]
                else:
                    self.image = pygame.transform.flip(
                        self.image_sheetseses[self.image_number][0][self.cur_sprite], 1, 0)
        elif self.image_number != 5:
            self.delay = (self.delay + 1) % self.image_sheetseses[self.image_number][2]
            if self.delay == self.image_sheetseses[self.image_number][2] - 1:
                if self.cur_sprite == 2:
                    pass
                else:
                    self.next_sprite(self.image_sheetseses[self.image_number][1])
                    if self.directhion == 'r':
                        self.image = self.image_sheetseses[self.image_number][0][self.cur_sprite]
                    else:
                        self.image = pygame.transform.flip(
                            self.image_sheetseses[self.image_number][0][self.cur_sprite], 1, 0)
        else:
            if self.on_ladder:
                self.image = self.image_sheetseses[self.image_number][0][self.cur_sprite]
            if self.delay == self.image_sheetseses[self.image_number][2] - 1:
                self.next_sprite(self.image_sheetseses[self.image_number][1])
                self.image = self.image_sheetseses[self.image_number][0][self.cur_sprite]
                self.delay = 0

        sp = pygame.sprite.groupcollide(player_group, walls_group, False, False)
        if sp:
            self.is_in_air = False
            self.after_wall = 50
            if DEBUG_ON:
                debug_output(['', '', '', '', '', '', '', [i.rect for i in sp[list(sp.keys())[0]]]])
            for i in sp[list(sp.keys())[0]]:
                if (
                        (self.rect.y + self.rect.h > i.rect.y) and (self.rect.y < i.rect.y) and (
                        self.rect.x + self.rect.w > i.rect.x)):
                    self.rect.y = -self.rect.h + i.rect.y
                    self.velocity_y = 0
                elif (
                        (self.rect.y < i.rect.y + i.rect.h) and (
                        self.rect.y + self.rect.h > i.rect.y + i.rect.h) and (
                                self.rect.x + self.rect.w > i.rect.x + self.velocity_x)):
                    self.rect.y = i.rect.y + i.rect.h
                    self.velocity_y = 0.001
        else:
            self.is_in_air = True
            self.on_wall = False

        spj = pygame.sprite.groupcollide(player_group, jump_walls_group, False, False)
        if spj:
            for i in spj[list(spj.keys())[0]]:
                if ((self.rect.y + self.rect.h > i.rect.y + tile_height // 2) and (
                        self.rect.y < i.rect.y)):
                    if self.rect.x + self.rect.w > i.rect.x and self.rect.x < i.rect.x:
                        self.rect.x = i.rect.x - self.rect.w
                        self.image_number = 2
                        self.on_wall = True
                        self.napr_after_wall = 1
                    elif self.rect.x < i.rect.x + i.rect.w and self.rect.x + self.rect.w > i.rect.x:
                        self.rect.x = i.rect.x + i.rect.w
                        self.image_number = 2
                        self.on_wall = True
                        self.napr_after_wall = -1

        spx = pygame.sprite.groupcollide(player_group, x_wall_group, False, False)
        if spx:
            for i in spx[list(spx.keys())[0]]:
                if self.rect.y + self.rect.h > i.rect.y + tile_height // 2 and self.rect.y < i.rect.y:
                    if self.rect.x + self.rect.w > i.rect.x and self.rect.x < i.rect.x:
                        self.rect.x = i.rect.x - self.rect.w
                        self.on_wall = True
                    elif self.rect.x < i.rect.x + i.rect.w and self.rect.x + self.rect.w > i.rect.x:
                        self.rect.x = i.rect.x + i.rect.w
                        self.on_wall = True
                elif ((self.rect.y + self.rect.h > i.rect.y) and (self.rect.y < i.rect.y) and (
                        self.rect.y + self.rect.h < i.rect.y + i.rect.h // 2)):
                    self.rect.y = -self.rect.h + i.rect.y
                    self.velocity_y = 0
                    self.is_stand = True
                    self.on_wall = False

        spv = pygame.sprite.groupcollide(player_group, v_wall_group, False, False)
        if spv:
            for i in spv[list(spv.keys())[0]]:
                if ((self.rect.y + self.rect.h > i.rect.y + tile_height // 2) and (
                        self.rect.y < i.rect.y)):
                    if self.rect.x + self.rect.w > i.rect.x and self.rect.x < i.rect.x:
                        self.rect.x = i.rect.x - self.rect.w
                        self.on_wall = True
                    elif self.rect.x < i.rect.x + i.rect.w and self.rect.x + self.rect.w > i.rect.x:
                        self.rect.x = i.rect.x + i.rect.w
                        self.on_wall = True

                elif ((self.rect.y < i.rect.y + i.rect.h) and (
                        self.rect.y + self.rect.h > i.rect.y + i.rect.h)):
                    self.rect.y = i.rect.y + i.rect.h
                    self.velocity_y = 0.001
                    self.on_wall = False

        spl = pygame.sprite.groupcollide(player_group, ladder_group, False, False)
        if spl:
            self.on_ladder = True
            self.velocity_y = 0
            self.is_stand = True
            self.image_number = 5
            if len(spl[list(spl.keys())[0]]) >= 3:
                self.rect.x = spl[list(spl.keys())[0]][1].rect.x + tile_width // 2 - self.rect.w // 2
            else:
                self.rect.x = spl[list(spl.keys())[0]][0].rect.x + tile_width // 2 - self.rect.w // 2
        else:
            self.on_ladder = False

        if pygame.sprite.groupcollide(player_group, triger_group, False, False):
            if self.level == 2:
                if not player.must_kill:
                    end_screen()
            else:
                self.level = 2
        if pygame.sprite.groupcollide(player_group, spikes_group, False, False):
            self.heath = 0
        if self.is_in_air and not self.is_stand:
            if self.velocity_y < tile_height:
                self.velocity_y += self.graviti_k * K_OF_RESOLUTHION
            if self.on_wall:
                if self.velocity_y > 1 * K_OF_RESOLUTHION:
                    self.velocity_y = 1 * K_OF_RESOLUTHION
            self.graviti_k = 0.24

        if self.velocity_y == 0:
            self.have_jump = False

        x = self.rect.x
        y = self.rect.y

        self.rect.x += round(self.velocity_x)
        self.rect.y += round(self.velocity_y)

        if self.rect.x < 0:
            self.rect.x = 0
        if self.rect.y < 0:
            self.rect.y = 0
        if self.rect.x > width - (2 * tile_width):
            self.rect.x = width - (2 * tile_width)
        if self.rect.y > height - (2 * tile_height):
            self.rect.y = height - (2 * tile_height)
            self.have_jump = False
            self.is_stand = True

        if x == self.rect.x and self.image_number != 2 and not self.on_ladder:
            self.image_number = 1
        elif y == self.rect.y and not self.on_ladder:
            self.image_number = 0
        if self.have_jump and not self.on_wall and not self.on_ladder:
            self.image_number = 3
            if self.velocity_y > 0:
                self.image_number = 4
        if ((pygame.sprite.groupcollide(player_group, walls_group, False, False)) or (
                pygame.sprite.groupcollide(player_group, x_wall_group, False, False)) or (
                pygame.sprite.groupcollide(player_group, ladder_group, False, False))):
            self.is_stand = True
        else:
            self.rect.y += 1
            if ((not pygame.sprite.groupcollide(player_group, walls_group, False, False)) and (
                    not pygame.sprite.groupcollide(player_group, x_wall_group, False, False)) and (
                    not pygame.sprite.groupcollide(player_group, ladder_group, False, False))):
                self.is_stand = False
            self.rect.y += -1

        if self.heath <= 0:
            self.is_dead = True
        if self.is_dead:
            self.image_number = 6
            self.is_dead = False
            if self.cur_sprite == 0:
                sound1.play()
            if self.cur_sprite == self.image_sheetseses[self.image_number][1] - 1:
                self.is_dead = True
        self.time += 1
        if DEBUG_ON:
            debug_output(
                [self.image_number, self.velocity_y, self.velocity_x, self.rect.x, self.rect.y,
                 self.rect.x + self.rect.w, self.rect.y + self.rect.h])


# class Enemy(pygame.sprite.Sprite):
#     def __init__(self, pos_x, pos_y):
#         super().__init__(enemy_group, all_sprites)


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                pass
            elif level[y][x] == '#':
                walls_group.add(Tile('wall', x, y))
            elif level[y][x] == '@':
                new_player = Player(x, y)
            elif level[y][x] == 'j':
                jump_walls_group.add(Tile('jump_wall', x, y))
            elif level[y][x] == 'w':
                x_wall_group.add(Tile('x_wall', x, y))
            elif level[y][x] == 'l':
                ladder_group.add(Tile('ladder', x, y))
            elif level[y][x] == 't':
                triger_group.add(Tile('trigger', x, y))
            elif level[y][x] == 'v':
                v_wall_group.add(Tile('v_wall', x, y))
            elif level[y][x] == 's':
                spikes_group.add(Tile('spikes', x, y))
    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.x = 0
        self.y = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        if ((self.x >= 0 and (-(target.rect.x + target.rect.w // 2 - width // 2) > 0)) or
                (((-self.x) < level_x * tile_width + tile_width // 2) and (
                        -(target.rect.x + target.rect.w // 2 - width // 2) < 0) and (
                         (-self.x) > level_x * tile_width - width + tile_width // 2))):
            self.dx = 0
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)
        if ((self.y >= -tile_height and -(target.rect.y + target.rect.h // 2 - height // 2) > 0) or
                ((((-self.y) <= level_y * tile_height) and -(
                        target.rect.y + target.rect.h // 2 - height // 2) < 0) and (
                         (-self.y) > level_y * tile_height - height))):
            self.dy = 0
        self.x += self.dx
        self.y += self.dy


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def end_screen():
    fon = load_image('ending.png')
    screen.blit(fon, (0, 0))
    pygame.mixer.music.load('data/ending.mp3')
    pygame.mixer.music.play(1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                player.must_kill = True
                pygame.mixer.music.load('data/TunnelRhino.mp3')
                pygame.mixer_music.set_volume(0.8)
                pygame.mixer.music.play(-1)
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


# start_screen()
player, level_x, level_y = generate_level(load_level('map.txt'))
camera = Camera()
running = True
level_i_1 = load_image('level_1.png', -1)
back_1 = load_image('level_fon_start.png')
level_i_2 = load_image('level_2.png', -1)
back_2_3 = load_image('level_fon_2_1.png')
back_2_2 = load_image('level_fon_2_2.png')
back_2_1 = load_image('level_fon_2_3.png')
is_on_pause = False
delay = 0
sound1 = pygame.mixer.Sound('data/SFX/die.wav')
# sound1.play()
pygame.mixer.music.load('data/TunnelRhino.mp3')
pygame.mixer_music.set_volume(0.8)
pygame.mixer.music.play(-1)
# pygame.mixer_music.stop()
while running:
    previos_level = player.level
    if not is_on_pause:
        if player.level == 1:
            screen.fill(pygame.Color('white'))
            screen.blit(back_1, (camera.x // 2, 0))
            screen.blit(level_i_1, (camera.x, camera.y))
        elif player.level == 2:
            delay = (delay + 1) % 24
            screen.fill(pygame.Color('white'))
            if delay in list(range(8)):
                screen.blit(back_2_1, (camera.x // 3 + 12 * tile_width, 0))
            elif delay in list(range(8, 16)):
                screen.blit(back_2_2, (camera.x // 3 + 12 * tile_width, 0))
            else:
                screen.blit(back_2_3, (camera.x // 3 + 12 * tile_width, 0))
            screen.blit(level_i_2, (camera.x, camera.y))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                is_on_pause = not is_on_pause
                if is_on_pause:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            if event.key == pygame.K_UP:
                player.move((0, -1))
    if not is_on_pause:

        keys = pygame.key.get_pressed()
        moves = [0, 0, 0]
        if keys[pygame.K_LEFT]:
            moves[0] = -1
        if keys[pygame.K_RIGHT]:
            moves[0] = 1
        if player.on_ladder:
            if keys[pygame.K_UP]:
                moves[1] = -1
        if keys[pygame.K_DOWN]:
            moves[1] = 1
        if keys[pygame.K_x]:
            moves[2] = 1
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    moves[1] = -1
        player.move(tuple(moves))
        # изменяем ракурс камеры

        camera.update(player)
        # обновляем положение всех спрайтов
        if camera.dx or camera.dy:
            for sprite in all_sprites:
                camera.apply(sprite)
        tiles_group.draw(screen)
        player_group.draw(screen)
        if DEBUG_ON:
            pygame.draw.rect(screen, pygame.Color('green'), player.rect, 3)
        player_group.update()
        # all_sprites.update()
        clock.tick(FPS)
        pygame.display.flip()
        if player.level != previos_level:
            for i in all_sprites:
                i.kill()
            player, level_x, level_y = generate_level(load_level('map_2.txt'))
            camera = Camera()
            player.level = 2
        if player.is_dead or player.must_kill:
            for i in all_sprites:
                i.kill()
            player, level_x, level_y = generate_level(load_level('map.txt'))
            sound1.stop()
            camera = Camera()
            must_kill = False

pygame.quit()
