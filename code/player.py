import pygame
from settings import *
from support import import_folder
from entity import Entity
class Player(Entity):
    
    def __init__(self,pos,groups,obstacle_sprites,create_attack,destroy_attack,create_magic):
        super().__init__(groups)
        self.image=pygame.image.load('../graphics/test/player.png').convert_alpha()
        self.rect=self.image.get_rect(topleft=pos)
        self.hitbox=self.rect.inflate(-6,HITBOX_OFFSET['player'])
        # Graphics setup
        self.import_player_assests()
        self.status='down'

        # movement
        self.attacking=False
        self.attack_cooldown=400
        self.attack_time=None

        
        self.obstacle_sprite=obstacle_sprites

        # Weapon
        self.create_attack=create_attack
        self.destroy_attack=destroy_attack
        self.weapon_index=0
        self.weapon= list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon=True
        self.weapon_switch_time=None
        self.switch_duration_cooldown=200

        # magic
        self.create_magic=create_magic
        self.magic_index=0
        self.magic= list(magic_data.keys())[self.magic_index]
        self.can_switch_magic=True
        self.magic_switch_time=None



        # stats
        self.stats={'health':100,'energy':60,'attack':10,'magic':4,'speed':5}
        self.max_stats={'health':300,'energy':140,'attack':20,'magic':10,'speed':10}
        self.upgrade_cost={'health':100,'energy':100,'attack':100,'magic':100,'speed':100}
        self.health=self.stats['health']*0.5
        self.energy=self.stats['energy']*0.8
        self.exp=500
        self.speed=self.stats['speed']

        # damage timer
        self.vulnerable=True
        self.hurt_time=None
        self.invulnerability_duration=500

        # import a sound
        self.weapon_attac_sound=pygame.mixer.Sound('../audio/sword.wav')
        self.weapon_attac_sound.set_volume(0.4)


    def import_player_assests(self):
        character_path='../graphics/player/'
        self.animations={
            'up':[],
            'down':[],
            'left':[],
            'right':[],
            'right_idle':[],
            'left_idle':[],
            'up_idle':[],
            'down_idle':[],
            'right_attack':[],
            'left_attack':[],
            'up_attack':[],
            'down_attack':[],
        }
        for animation in self.animations.keys():
            full_path=character_path+animation
            self.animations[animation]=import_folder(full_path)


    def input(self):
        if not self.attacking:
            keys=pygame.key.get_pressed()
            # Movement input
            if keys[pygame.K_UP]:
                self.direction.y=-1
                self.status='up'
            elif keys[pygame.K_DOWN]:
                self.status='down'
                self.direction.y=1
            else:
                self.direction.y=0


            if keys[pygame.K_RIGHT]:
                self.status='right'
                self.direction.x=1
            elif keys[pygame.K_LEFT]:
                self.status='left'
                self.direction.x=-1
            else:
                self.direction.x=0
            # attack input
            if keys[pygame.K_SPACE]:
                self.attacking=True
                self.attack_time=pygame.time.get_ticks()
                self.create_attack()
                self.weapon_attac_sound.play()
            # Magic input
            if keys[pygame.K_LCTRL]:
                self.attack_time=pygame.time.get_ticks()
                self.attacking=True
                self.create_magic(style=self.magic,
                                  strength=magic_data[self.magic]['strength']+self.stats['magic'],
                                  cost=magic_data[self.magic]['cost'])

            # switching weapon
            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon=False
                self.weapon_switch_time=pygame.time.get_ticks()
                self.weapon_index=(self.weapon_index+1)%len(weapon_data.keys())
                self.weapon= list(weapon_data.keys())[self.weapon_index]

            # switching magic
            if keys[pygame.K_e] and self.can_switch_magic:
                self.can_switch_magic=False
                self.magic_switch_time=pygame.time.get_ticks()
                self.magic_index=(self.magic_index+1)%len(magic_data.keys())
                self.magic= list(magic_data.keys())[self.magic_index]

    def get_status(self):
        # idle status
        if self.direction.x==0 and self.direction.y==0:
            if not '_idle' in self.status and not 'attack' in self.status:
                self.status=self.status+'_idle'
        if self.attacking:
            self.direction.x=0
            self.direction.y=0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status=self.status.replace('_idle','_attack')
                else:
                    self.status=self.status+'_attack'
        else:
            if 'attack' in self.status:
                self.status=self.status.replace('_attack','')

    def get_value_by_index(self,index):
        return list(self.stats.values())[index]

    def get_cost_by_index(self,index):
        return list(self.upgrade_cost.values())[index]


    def cooldowns(self):
        current_time=pygame.time.get_ticks()
        if self.attacking:
            if current_time-self.attack_time>=self.attack_cooldown+weapon_data[self.weapon]['cooldown']:
                self.attacking=False
                self.destroy_attack()
        if not self.can_switch_weapon:
            if current_time-self.weapon_switch_time>=self.switch_duration_cooldown:
                self.can_switch_weapon=True
        if not self.can_switch_magic:
            if current_time-self.magic_switch_time>=self.switch_duration_cooldown:
                self.can_switch_magic=True

        if not self.vulnerable:
            if current_time-self.hurt_time>=self.invulnerability_duration:
                self.vulnerable=True

    def animate(self):
        animation=self.animations[self.status]
        # loop over frame index
        self.frame_index+=self.animation_speed
        if self.frame_index>=len(animation):
            self.frame_index=0

        # set the image
        self.image=animation[int(self.frame_index)]
        self.rect=self.image.get_rect(center=self.hitbox.center)

        # flicker
        if not self.vulnerable:
            alpha=self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):
        base_damage= self.stats["attack"]
        weapon_demage= weapon_data[self.weapon]['damage']
        return base_damage+weapon_demage

    def get_full_magic_damage(self):
        base_damage=self.stats['magic']
        spell_damge=magic_data[self.magic]['strength']
        return base_damage+spell_damge
    def energy_recovery(self):
        if self.energy<self.stats['energy']:
            self.energy+=0.01*self.stats['magic']
        else:
            self.energy=self.stats['energy']

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.stats['speed'])
        self.energy_recovery()