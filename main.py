import pygame
import os 
import random
import csv 

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Treasure Hunter')

#framerate
clock =pygame.time.Clock()
FPS = 60 

#Gravity
SCROLL = 200 
GRAVITY = 0.75 
ROWS = 16
COLS = 150 
TILE_SIZE = SCREEN_HEIGHT // ROWS 
TILE_TYPES = 21
SCREEN_SCROLL = 0
bg_scroll = 0 
LEVEL = 1
MAX_LEVELS = 2 
start_game = False


#define player action variables 
moving_left = False
moving_right = False 
shoot = False
#load music
pygame.mixer.music.load('assets/music/audio.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_sound = pygame.mixer.Sound('assets/music/jump.mp3')
jump_sound.set_volume(0.5)
shot_sound = pygame.mixer.Sound('assets/music/shot.mp3')
shot_sound.set_volume(0.5)

#button image
start_img = pygame.image.load('assets/start_btn.png').convert_alpha()
exit_img = pygame.image.load('assets/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('assets/restart_btn.png').convert_alpha()

#background
bg_img = pygame.image.load('assets/Background/bg.jpg').convert_alpha()
#load image list 
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'assets/Terrain/{x}.png').convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)).convert_alpha()
    img_list.append(img)


#bullets
bullet_img = pygame.image.load('assets/Icons/waterbullet.png').convert_alpha()
#pick up boxes
health_box_img = pygame.image.load('assets/Icons/health_box.png').convert_alpha()
bullet_box_img = pygame.image.load('assets/Icons/ammo_box.png').convert_alpha()
item_boxes = {
    'Health' : health_box_img,
    'Ammo' : bullet_box_img

}
BG = (230, 230, 250)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
#define font
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))

def draw_background():
    screen.fill(BG)
    width = bg_img.get_width()
    for x in range(5): 
        screen.blit(bg_img, (x * width - bg_scroll, 0))

def reset():
    enemy_group.empty()
    bullet_group.empty()
    itembox_group.empty()
    chest_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    
    data = []
    for ROW in range(ROWS):
        R = [-1] * COLS 
        data.append(R)

    return data 

class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False 
        #get mouse position 
        pos = pygame.mouse.get_pos()
        #check mouseover nd click conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action 

class Character(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, amm):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True 
        self.char_type = char_type 
        self.speed = speed 
        self.amm = amm
        self.start_amm = amm 
        self.shoot_cd = 0 
        self.health = 100 
        self.max_health = self.health 
        self.direction = 1 
        self.vel_y = 0
        self.jump = False 
        self.in_air = True 
        self.flip = False 
        self.animation_list = []
        self.index = 0 
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        
        self.move_count = 0 
        self.vision = pygame.Rect(0, 0, 100, 20)
        self.idling = False
        self.idling_count = 0
        #load all images for the player
        animation_types = ['idle', 'jump', 'fall', 'run', 'hit']
        for animation in animation_types:
            #reset temp list of images
            temp_list = []
            #count number of files in folder
            num_of_files = len(os.listdir(f'assets/{self.char_type}/{animation}'))
            for i in range(num_of_files):
                img = pygame.image.load(f'assets/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        
        
        self.image = self.animation_list[self.action][self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cd > 0:
            self.shoot_cd -= 1
        

    def movement(self, moving_left, moving_right):
        #reset movement variables
        SCREEN_SCROLL = 0

        dx = 0
        dy  = 0

        #assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1 
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1
        #jump 
        if self.jump == True and self.in_air == False:
            self.vel_y = -15 
            self.jump = False
            self.in_air = True 
        #gravity 
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y 
        dy += self.vel_y 

        #check collision 
        for tile in world.obstacle_list:
            #check collision in x 
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                #if the enemy hit a wall, make it turn aroung
                if self.char_type == "Enemy":
                    self.direction *= -1 
                    self.move_count = 0 
            #check for collision in y 
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #check if below the ground (jumping)
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top 
                #check if above the ground (falling)
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom 

        #check if the player fall into the water or fall off the map
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0 
    
        #check for collision with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True 

        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0 

        
        
        #check if the player going off the screen
        if self.char_type == 'Player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0 

        #update rect position
        self.rect.x += dx
        self.rect.y += dy 

        #update scroll base on player position 
        if self.char_type == 'Player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL and bg_scroll < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                or (self.rect.left < SCROLL and bg_scroll > abs(dx)):
                self.rect.x -= dx
                SCREEN_SCROLL = -dx 
        return SCREEN_SCROLL, level_complete 
    


    def shoot(self):
        if self.shoot_cd == 0 and self.amm > 0:
            self.shoot_cd = 20
            bullet = Bullet(self.rect.centerx + (0.7 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            
            self.amm -= 1
            shot_sound.play()

    def auto(self):
        if self.alive and player.alive: 
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)#idle
                self.idling = True
                self.idling_count = 50
            #check if the enemy near the player
            if self.vision.colliderect(player.rect):
                #stop running and attack the player
                self.update_action(0) #idle
                #shoot
                self.shoot()
            else: 
                if self.idling == False:
                    if self.direction ==  -1:
                        auto_moving_left = True
                    else:
                        auto_moving_left = False
                    auto_moving_right = not auto_moving_left
                    self.movement(auto_moving_left, auto_moving_right)
                    self.update_action(3) #run
                    self.move_count += 1
                    #update vision
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_count > TILE_SIZE:
                        self.direction *= -1 
                        self.move_count *= -1
                else:
                    self.idling_count -= 1
                    if self.idling_count <= 0:
                        self.idling = False 
        #scroll 
        self.rect.x += SCREEN_SCROLL


    def update_animation(self):
        ANIMATION_COOLDOWN = 200
        
        #check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.index += 1  
        #reset the animation
        if self.index >= len(self.animation_list[self.action]):
            if self.action == 4:
                self.index = len(self.animation_list[self.action]) - 1
            else:
                self.index = 0 
        #update image depending on index
        self.image = self.animation_list[self.action][self.index]

    def update_action(self, new_action):
        
        if new_action != self.action:
            self.action = new_action 
            #update the animation setting
            self.index = 0
            self.update_time = pygame.time.get_ticks()
            
    def check_alive(self):
        if self.health <=  0:
            self.health = 0
            self.speed = 0
            self.alive = False 
            self.update_action(4)
            
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect) 

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        #iterate through each value and data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE  
                    img_rect.y = y * TILE_SIZE 
                    tile_data = (img, img_rect)
                    if tile >=0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile == 12:
                        chest = Chest(img, x* TILE_SIZE, y * TILE_SIZE)
                        chest_group.add(chest)
                    elif tile <= 14 and tile == 11:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15: #player
                        player = Character('Player', x * TILE_SIZE, y * TILE_SIZE, 2, 8, 20)
                        health_bar = HealthBar(10, 10, player.health, player.max_health)
                    elif tile == 16: #first enemy 
                        enemy = Character('Bunny', x * TILE_SIZE, y * TILE_SIZE, 1.5, 2, 20)
                        enemy_group.add(enemy)
                    elif tile == 17: #ammo box
                        item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
                        itembox_group.add(item_box)
                    elif tile == 18 and tile == 19: 
                        item_box = ItemBox('Health', 100, 260)
                        itembox_group.add(item_box)
                    elif tile == 20:#creat exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)  
        return player, health_bar 
    def draw(self): 
        for tile in self.obstacle_list:
            tile[1][0] += SCREEN_SCROLL 
            screen.blit(tile[0], tile[1])
class Chest(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self) 
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += SCREEN_SCROLL 

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self) 
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += SCREEN_SCROLL 

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self) 
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += SCREEN_SCROLL  

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self) 
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += SCREEN_SCROLL 


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_types, x, y):
        pygame.sprite.Sprite.__init__(self) 
        self.item_types = item_types
        self.image = item_boxes[self.item_types]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

   
        

    def update(self):
        self.rect.x += SCREEN_SCROLL   
        #check if the player has picked up the boxes
        if pygame.sprite.collide_rect(self, player):
            #check what kind of boxes
            if self.item_types == 'Health':
                player.health += 10
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_types == 'Ammo': 
                player.amm += 20
            #delete the boxes
            self.kill() 

class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        #update with new hp
        self.health = health
        #calculate health ratio
        ratio = self.health / self.max_health 
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

    


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
    def update(self):
        #move bullets
        self.rect.x += (self.direction * self.speed) + SCREEN_SCROLL 
        #check if bullet has gone off
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH - 20:
            self.kill()
        #check collision with obstacle
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        #check collision with character
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()
        for enemy in enemy_group: 
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 20 
                    self.kill()
                else: 
                    enemy_count += 1 
#creat button
start_button = Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_img, 1)

exit_button = Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

#create sprite group
bullet_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
itembox_group = pygame.sprite.Group()
chest_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()



#creat empty tile list
world_data = []
for ROW in range(ROWS):
    R = [-1] * COLS 
    world_data.append(R)
#load in level date and creat world
with open(f'level{LEVEL}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)




run = True
while run:
    clock.tick(FPS)
    if start_game == False:
        #main menu
        screen.fill(BG)
        if start_button.draw(screen):
            start_game = True
        if exit_button.draw(screen):
            run = False 
    else:
        draw_background()
        world.draw()
        health_bar.draw(player.health)
        draw_text(f'Bullet: ', font, WHITE, 10, 60)
        for x in range(player.amm):
            screen.blit(bullet_img, (80 + (x * 15), 60))

        player.update()
        player.draw()
        for enemy in enemy_group:
            enemy.auto()
            enemy.update()
            enemy.draw()

        #update and draw group
        bullet_group.update()
        itembox_group.update()
        chest_group.update( )
        decoration_group.update()
        water_group.update()
        exit_group.update()

        bullet_group.draw(screen)
        itembox_group.draw(screen)
        chest_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        #update player action
        if player.alive:
            #shoot bullets
            if shoot:
                player.shoot()

            if player.in_air: 
                player.update_action(1) # jump
            elif moving_left or moving_right: 
                player.update_action(3) # run
            else: 
                player.update_action(0) # idle
                
            SCREEN_SCROLL, level_complete = player.movement(moving_left, moving_right)
            bg_scroll -= SCREEN_SCROLL 
            if level_complete:
                LEVEL += 1
                bg_scroll = 0
                world_data = reset()
                if LEVEL <= MAX_LEVELS:
                    with open(f'level{LEVEL}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)

                    world = World()
                    player, health_bar = world.process_data(world_data)
                
                                        
        else:
            SCREEN_SCROLL = 0
            if restart_button.draw(screen):
                bg_scroll = 0
                word_data = reset()
                #load in level date and creat world
                with open(f'level{LEVEL}_data.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)

                world = World()
                player, health_bar = world.process_data(world_data)




    
    


    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        #keyboard pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a and player.alive:
                moving_left = True
            if event.key == pygame.K_d and player.alive:
                moving_right = True 
            if event.key == pygame.K_w and player.alive:
                player.jump = True 
                jump_sound.play()
            if event.key == pygame.K_SPACE and player.alive:
                shoot = True 
            if event.key == pygame.K_ESCAPE:
                run = False
        #keyboard released 
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False 
            if event.key == pygame.K_SPACE and player.alive:
                shoot = False

    
    pygame.display.update()
pygame.quit()