import math
import random as rand
from cmu_graphics import *

class Sprite():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 25
    
    def onStep(self, app):
        a = angleTo(self.x, self.y, app.hero.x, app.hero.y)
        dx = self.speed * math.sin(math.radians(a))
        dy = self.speed * math.cos(math.radians(a))
        self.x += dx
        self.y -= dy
        self.boundaryCheck(app)

    def draw(self, app):
        drawCircle(self.x - app.scrollX, self.y - app.scrollY,
                   self.r, fill = self.color, border = "black")
    
    def checkCollision(self, other):
        d = distance(self.x, self.y, other.x, other.y)
        if d < (self.r + other.r) * 0.8:
            return True
        else:
            return False
        
    def knockback(self, other, power, app):
        a = angleTo(other.x, other.y, self.x, self.y)
        dx = power * math.sin(math.radians(a))
        dy = power * math.cos(math.radians(a))
        self.x += dx
        self.y -= dy
        self.boundaryCheck(app)
        
    def boundaryCheck(self, app):
        if not app.bossFight:
            if self.x - self.r <= -600:
                self.x = -600 + self.r
            if self.x + self.r >= 1400:
                self.x = 1400 - self.r
            if self.y - self.r <= -700:
                self.y = -700 + self.r
            if self.y + self.r >= 1300:
                self.y = 1300 - self.r
        else:
            if self.x - self.r <= 0:
                self.x = self.r
            if self.x + self.r >= app.width:
                self.x = app.width - self.r
            if self.y - self.r <= 0:
                self.y = self.r
            if self.y + self.r >= app.height:
                self.y = app.height - self.r
        
    def loseHP(self, damage):
        self.hp -= damage

class Hero(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "red"
        self.dx = 3
        self.dy = 3
        self.hp = 100
        self.r = 25
        self.maxHP = 100
        self.armor = 0
        self.level = 0
        self.exp = 0
        self.levelEXPReq = 1
        self.aimDir = 0
        self.bulletDamage = 10
        self.bulletR = 3
        self.bulletSpeed = 10
        self.bulletCD = 0
        self.projectiles = []
        self.step = 0
        self.skills = {
            "RPG": [False, 0], "Type-A Drone": [False, 0],
            "Type-B Drone": [False, 0], "Forcefield": [False, 0],
            "Lightning Emitter": [False, 0], "Drill Shot": [False, 0],
            "Energy Cube": [False, 0], "Ammo Thruster": [False, 0], 
            "Ronin Oyoroi": [False, 0], "Sports Shoes": [False, 0], 
            "HE Fuel": [False, 0], "Fitness Guide": [False, 0]
        }

    def onStep(self, app):
        self.step += 1
        if self.step % (app.stepsPerSecond * 3 - self.bulletCD) == 0:
            target = self.findClosestEnemy(app, 500)
            if target != None:
                targetX, targetY = target[0], target[1]
                self.aimDir = angleTo(self.x, self.y, targetX, targetY)
            else:
                self.aimDir = 0
            self.shoot()

    def draw(self, app):
        drawImage(app.profImg, self.x - app.scrollX, self.y - app.scrollY,
                   align = "center")

    def drawHealthBar(self, app):
        drawRect(self.x - self.r - 10 - app.scrollX, self.y + 35 - app.scrollY,
                 70, 15, fill = "gray")
        healthBar = 70 * self.hp // self.maxHP
        drawRect(self.x - self.r - 10 - app.scrollX, self.y + 35 - app.scrollY,
                 healthBar + 0.1, 15, fill = "green")
    
    def loseHP(self, damage, app):
        super().loseHP(damage)
        if self.hp <= 0:
            app.isGameOver = True
            
    def levelUP(self, app):
        self.hp += self.maxHP // 5
        if self.hp > self.maxHP:
            self.hp = self.maxHP
        self.exp -= self.levelEXPReq
        self.level += 1
        self.levelEXPReq += 0
            
    def shoot(self):
        self.projectiles.append(Bullet(self.x, self.y, self.aimDir, 
                                       self.bulletDamage, self.bulletR, 
                                       self.bulletSpeed))
        
    def checkDropCollision(self, other):
        d = distance(self.x, self.y, other.x, other.y)
        if d < (self.r + other.r // 2):
            return True
        else:
            return False
    
    def findClosestEnemy(self, app, r):
        if not app.enemies:
            return None
        
        minD = None
        targetIndex = None
            
        for i in range(len(app.enemies)):
            e = app.enemies[i]
            d = distance(self.x, self.y, e.x, e.y)
            if d <= r:
                if minD == None:
                    minD = d
                    targetIndex = i
                else:
                    if minD > d:
                        minD = d
                        targetIndex = i

        if minD == None:
            return None
        else:
            return (app.enemies[targetIndex].x, app.enemies[targetIndex].y, \
                    targetIndex)
        
class Enemy(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y)
    
    def terminate(self, app):
        app.enemies.remove(self)
        app.drop.append(Crystal(self.x, self.y, self.drop))

    def loseHP(self, app, damage):
        super().loseHP(damage)
        if self.hp <= 0:
            self.terminate(app)

    def checkCollisionDrill(self, app, drill):
        enemyX = self.x - app.scrollX
        enemyY = self.y - app.scrollY
        d = distance(drill.x, drill.y, enemyX, enemyY)
        if d < 0.8 * (self.r + drill.r):
            return True
        return False
        
class Zombie(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "green"
        self.speed = 2
        self.damage = 3
        self.drop = 1
        self.hp = 10

    def draw(self, app):
        drawImage(app.sherImg, self.x - app.scrollX, self.y - app.scrollY,
                  align = "center")
        
class ZombieArcher(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "purple"
        self.speed = 2
        self.arrowSpeed = 5
        self.step = 0
        self.damage = 4
        self.drop = 2
        self.hp = 10
        self.shootFreq = rand.choice([2, 3, 4])
        
    def shoot(self, app):
        a = angleTo(self.x, self.y, app.hero.x, app.hero.y)
        app.arrows.append(Arrow(self.x, self.y, a))
        
    def onStep(self, app):
        self.step += 1
        if self.step % (app.stepsPerSecond * self.shootFreq) == 0:
            self.shoot(app)
            
        super().onStep(app)
    
    def draw(self, app):
        drawImage(app.faizImg, self.x - app.scrollX, self.y - app.scrollY,
                  align = "center")

class Runner(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "orange"
        self.speed = 4
        self.hp = 5
        self.damage = 3
        self.drop = 1
    
    def draw(self, app):
        drawImage(app.rashidImg, self.x - app.scrollX, self.y - app.scrollY,
                  align = "center")
        
class Heavy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "blue"
        self.speed = 1
        self.hp = 30
        self.drop = 3
        self.damage = 3
        self.r = 40
    
    def draw(self, app):
        drawImage(app.sudaisImg, self.x - app.scrollX, self.y - app.scrollY,
                  align = "center")
        
class Multiplier(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "pink"
        self.speed = 2
        self.hp = 10
        self.drop = 2
        self.damage = 3
        self.r = 25
    
    def draw(self, app):
        drawImage(app.emuImg, self.x - app.scrollX, self.y - app.scrollY,
                  align = "center")
        
    def terminate(self, app):
        app.enemies.append(MultiplierKids(self.x - 25, self.y - 25))
        app.enemies.append(MultiplierKids(self.x - 25, self.y + 25))
        app.enemies.append(MultiplierKids(self.x + 25, self.y - 25))
        app.enemies.append(MultiplierKids(self.x + 25, self.y + 25))
        app.drop.append(Crystal(self.x, self.y, 3))
        app.enemies.remove(self)
        
class MultiplierKids(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "pink"
        self.speed = 2
        self.hp = 5
        self.drop = 1
        self.damage = 2
        self.r = 15
    
    def draw(self, app):
        drawImage(app.emuKidImg, self.x - app.scrollX, self.y - app.scrollY,
                  align = "center")
        
class Teleporter(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "yellow"
        self.speed = 2
        self.damage = 2
        self.drop = 2
        self.hp = 10
        self.step = 0

    def onStep(self, app):
        super().onStep(app)
        self.step += 1
        if self.step % (app.stepsPerSecond * 5) == 0:
            posX, posY = onScreenPoint(app)
            self.x = posX
            self.y = posY

    def draw(self, app):
        drawImage(app.adamImg, self.x - app.scrollX, self.y - app.scrollY,
                  align = "center", width = 2 * self.r, height = 2 * self.r)
        
class Wizard(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "cyan"
        self.speed = 2
        self.damage = 4
        self.drop = 3
        self.hp = 15
        self.step = 0
    
    def draw(self, app):
        drawImage(app.furqanImg, self.x - app.scrollX, self.y - app.scrollY,
                  align = "center")
        
    def onStep(self, app):
        super().onStep(app)
        self.step += 1

        if self.step % (app.stepsPerSecond * 5) == 0:
            app.enemies.append(Minion(self.x - 25, self.y))
            app.enemies.append(Minion(self.x + 25, self.y))

class Minion(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "brown"
        self.speed = 4
        self.hp = 5
        self.drop = 1
        self.damage = 2
        self.r = 15
    
    def draw(self, app):
        drawImage(app.dikaImg, self.x - app.scrollX, self.y - app.scrollY,
                  align = "center")
        
class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = "black"
        self.r = 50
        self.speed = 2
        self.hp = 1000
        self.drop = 0
        self.damage = 3
        self.step = 0
        self.chargetimer = 0
        self.summontimer = 0
        self.shottimer = 0
        self.charging = False
        self.shooting = False
        self.summoning = False
        self.checkDir = False
    
    def draw(self, app):
        drawImage(app.bossImg, self.x - app.scrollX, self.y - app.scrollY, 
                  align = "center")

    def novaShot(self, app):
        self.shottimer += 1
        if self.shottimer == (app.stepsPerSecond * 3):
            for a in range(0, 360, 45):
                app.arrows.append(Arrow(self.x, self.y, a))
            self.shottimer = 0
            self.shooting = False

    def charge(self, app):
        if self.chargetimer == (app.stepsPerSecond * 2):
            self.a = angleTo(self.x, self.y, app.hero.x, app.hero.y)
        self.chargetimer += 1
        if self.chargetimer >= (app.stepsPerSecond * 3):
            dx = 10 * math.sin(math.radians(self.a))
            dy = 10 * math.cos(math.radians(self.a))
            self.x += dx
            self.y -= dy
            self.boundaryCheck(app)
            if self.chargetimer >= (app.stepsPerSecond * 5):
                self.chargetimer = 0
                self.charging = False

    def summon(self, app):
        self.summontimer += 1
        if self.summontimer == (app.stepsPerSecond * 3):
            for i in range(2):
                for j in range(2):
                    enemyType = rand.randint(1, 7)
                    posX = self.x + (-25 * (-1)**i)
                    posY = self.y + (-25 * (-1)**j)
                    if enemyType == 1:
                        app.enemies.append(Zombie(posX, posY))
                    elif enemyType == 2:
                        app.enemies.append(ZombieArcher(posX, posY))
                    elif enemyType == 3:
                        app.enemies.append(Runner(posX, posY))
                    elif enemyType == 4:
                        app.enemies.append(Heavy(posX, posY))
                    elif enemyType == 5:
                        app.enemies.append(Multiplier(posX, posY))
                    elif enemyType == 6:
                        app.enemies.append(Teleporter(posX, posY))
                    elif enemyType == 7:
                        app.enemies.append(Wizard(posX, posY))
            self.summontimer = 0
            self.summoning = False

    def onStep(self, app):
        if self.charging:
            self.charge(app)
        elif self.shooting:
            self.novaShot(app)
        elif self.summoning:
            self.summon(app)
        else:
            self.step += 1
            if self.step % (app.stepsPerSecond * 5) == 0:
                specialMove = rand.randint(1, 3)
                if specialMove == 1:
                    self.shooting = True
                elif specialMove == 2:
                    self.charging = True
                else:
                    self.summoning = True
            else:
                super().onStep(app)

    def terminate(self, app):
        app.victoryScreen = True
        app.enemies.clear()
    
                    
class Projectile():
    def __init__(self, x, y, d):
        self.x = x
        self.y = y
        self.d = d
        
    def onStep(self, app):
        self.step += 1
        dx = self.speed * math.sin(math.radians(self.d))
        dy = self.speed * math.cos(math.radians(self.d))
        self.x += dx
        self.y -= dy
    
class Bullet(Projectile):
    def __init__(self, x, y, d, damage, r, speed):
        super().__init__(x, y, d)
        self.speed = speed
        self.r = r
        self.step = 0
        self.damage = damage
        
    def draw(self, app):
        drawCircle(self.x - app.scrollX, self.y - app.scrollY, self.r,
                   fill = "black")
        
    def terminate(self, app):
        app.hero.projectiles.remove(self)

class Explosion():
    def __init__(self, x, y, power):
        self.x = x
        self.y = y
        self.step = 0
        self.curExpImg = 1
        self.power = power
    
    def onStep(self, app):
        self.step += 1
        if self.step % (app.stepsPerSecond // 30) == 0:
            self.curExpImg += 1
            if self.curExpImg == 10:
                app.explosions.remove(self)

    def draw(self, app):
        drawImage(app.explosionIMGs[self.curExpImg], self.x - app.scrollX, 
                  self.y - app.scrollY, align = "center", 
                  width = self.power, height = self.power)

class Drone():
    def __init__(self, model, app):
        self.model = model
        self.dy = 1
        self.float = 0
        self.step = 0
        self.level = 0
        if self.model == "A":
            self.damage = 5
            self.CD = 0
            self.xSign = 1
            self.x = app.hero.x + 40
            self.y = app.hero.y - 40
        else:
            self.damage = 20
            self.CD = -60
            self.xSign = -1
            self.x = app.hero.x - 40
            self.y = app.hero.y - 40

    def onStep(self, app):
        self.step += 1
        self.x = app.hero.x + 40 * self.xSign
        self.y = app.hero.y - 40 + self.float

        #Floating animation
        if self.step % (app.stepsPerSecond // 6) == 0:
            self.float -= self.dy
        if self.step % (app.stepsPerSecond * 2) == 0:
            self.dy = -self.dy

        #Attack mechanics
        target = app.hero.findClosestEnemy(app, 150)
        if target != None:
            if self.step % (app.stepsPerSecond - self.CD) == 0:
                randomDir = rand.choice([0, 45, 90, 135, 180, 225, 
                                            270, 315])
                app.hero.projectiles.append(DroneMissle(self.x, self.y, 
                                randomDir, app.enemies[target[2]], self.damage))


    def draw(self, app):
        if self.model == "A":
            drawImage(app.droneAImg[0], self.x - app.scrollX,
                    self.y - app.scrollY, align = "center", width = 25, 
                    height = 25)
        else:
            drawImage(app.droneBImg[0], self.x - app.scrollX,
                    self.y - app.scrollY, align = "center", width = 25, 
                    height = 25)
            
    def levelUP(self):
        self.level += 1
        if self.level != 1:
            self.damage += 5
            self.CD += 5

class LightningEmitter():
    def __init__(self):
        self.r = 10
        self.damage = 10
        self.step = 0
        self.CD = -15
    
    def onStep(self, app):
        self.step += 1
        target = app.hero.findClosestEnemy(app, 600)
        if target != None:
            if self.step % (app.stepsPerSecond - self.CD) == 0:
                app.lightning.append(Lightning(target[0], target[1], self.r, 
                                               self.damage))
                areaDamage(target[0], target[1], self.r, app, self.damage)

class Lightning():
    def __init__(self, x, y, r, damage):
        self.x = x
        self.y = y
        self.r = r
        self.damage = damage
        self.step = 0
        self.curImg = 0

    def onStep(self, app):
        self.step += 1
        if self.step % (app.stepsPerSecond // 15) == 0:
            self.curImg += 1
            if self.curImg == 4:
                app.lightning.remove(self)

    def draw(self, app):
        drawImage(app.lightningIMGs[self.curImg], self.x - app.scrollX, 
                  self.y + 110 - app.scrollY, align = "bottom", width = 200, 
                  height = 800)

class Forcefield():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.r = 50
        self.lastR = 0
        self.level = 0
        self.damage = 5
        self.step = 0

    def draw(self, app):
        for i in range(self.level):
            drawCircle(self.x - app.scrollX, self.y - app.scrollY, 
                       self.r + i * 50, fill = "lime", border = "lime",
                       opacity = 20)
        
    def levelUP(self):
        self.level += 1
        self.damage += 5
        self.lastR += self.r

    def onStep(self, app):
        self.x = app.hero.x
        self.y = app.hero.y
        self.step += 1
        if self.step % (app.stepsPerSecond // 2) == 0:
            temp = len(app.enemies)
            for e in app.enemies:
                d = distance(self.x, self.y, e.x, e.y)
                if d - e.r < self.lastR:
                    e.loseHP(app, self.damage)

class RPGRocket(Projectile):
    def __init__(self, x, y, d, tx, ty):
        super().__init__(x, y, d)
        self.speed = 25
        self.r = 15
        self.expR = 20
        self.step = 0
        self.damage = 20
        self.step = 0

        #Registering target coordinates
        self.tx = tx
        self.ty = ty
        self.d = angleTo(self.x, self.y, self.tx, self.ty)
    
    def onStep(self, app):
        self.step += 1
        if self.step % (app.stepsPerSecond // 15) == 0:                
            dx = self.speed * math.sin(math.radians(self.d))
            dy = self.speed * math.cos(math.radians(self.d))
            self.x += dx
            self.y -= dy                
                
    def draw(self, app):
        drawImage(app.RPGImg, self.x - app.scrollX, 
                    self.y - app.scrollY, width = 40, height = 40, 
                    align = "center", rotateAngle = self.d - 45)
        
    def terminate(self, app):
        app.explosions.append(Explosion(self.x, self.y, 30))
        areaDamage(self.x, self.y, self.expR, app, self.damage)
        app.hero.projectiles.remove(self)
            
class DroneMissle(Projectile):
    def __init__(self, x, y, d, targetEntity, damage):
        super().__init__(x, y, d)
        self.speed = 15
        self.r = 15
        self.step = 0
        self.damage = damage
        self.step = 0
        self.targetEntity = targetEntity

        #Registering target coordinates and direction (td) to target
        self.tx = targetEntity.x
        self.ty = targetEntity.y
        self.td = angleTo(self.x, self.y, self.tx, self.ty)
        self.dd = 45
    
    def onStep(self, app):
        self.step += 1
        if self.step % (app.stepsPerSecond // 30) == 0:
            #Updating target coordinates and direction (td) to target
            self.tx = self.targetEntity.x
            self.ty = self.targetEntity.y
            self.td = angleTo(self.x, self.y, self.tx, self.ty)

            directionDif = self.td - self.d
            if directionDif > 0:
                if directionDif < self.dd:
                    self.d = self.td
                else:
                    self.d += self.dd
            elif directionDif < 0:
                if abs(directionDif) < self.dd:
                    self.d = self.td
                else:
                    self.d -= self.dd  

            dx = self.speed * math.sin(math.radians(self.d))
            dy = self.speed * math.cos(math.radians(self.d))
            self.x += dx
            self.y -= dy  
        
        if self.step == app.stepsPerSecond * 3:
            self.terminate(app)


    def draw(self, app):
        drawImage(app.RPGImg, self.x - app.scrollX, 
                    self.y - app.scrollY, width = 20, height = 20, 
                    align = "center", rotateAngle = self.d - 45) 
        
    def terminate(self, app):
        app.explosions.append(Explosion(self.x, self.y, 20))
        app.hero.projectiles.remove(self)

class DrillShot(Projectile):
    def __init__(self, x, y, d):
        super().__init__(x, y, d)
        self.r = 5
        self.speed = 10
        self.step = 0
        self.damage = 8

    def onStep(self, app):
        self.step += 1
        dx = self.speed * math.sin(math.radians(self.d))
        dy = self.speed * math.cos(math.radians(self.d))

        #Wall bouncing mechanics
        if self.x + dx + self.r > 1400 - app.scrollX:
            self.x  = 1400 - app.scrollX - self.r
            self.d = -self.d
        elif self.x + dx - self.r < -600 - app.scrollX:
            self.x = -600 - app.scrollX + self.r
            self.d = -self.d

        if self.y - dy + self.r > 1300 - app.scrollY:
            self.y = 1300 - app.scrollY - self.r
            self.d += (self.d // 45) * 90
        elif self.y - dy + self.r < -700 - app.scrollY:
            self.y = -700 - app.scrollY + self.r
            self.d += (self.d // 45) * 90

        #Screen bouncing mechanics
        if self.x + dx + self.r > app.width:
            self.x = app.width - self.r
            self.d = -self.d
        elif self.x + dx - self.r < 0:
            self.x = self.r
            self.d = -self.d
        else:
            self.x += dx

        if self.y - dy + self.r > app.height:
            self.y = app.height - self.r
            self.d += (self.d // 45) * 90
        elif self.y - dy - self.r < 0:
            self.y = self.r
            self.d += (self.d // 45) * 90
        else:
            self.y -= dy

    def draw(self, app):
        drawImage(app.drillShotImg, self.x, self.y, rotateAngle = self.d - 45,
                  align = "center", width = 20, height = 20)
    
    def terminate(self, app):
        return
        
    
class Arrow(Projectile):
    def __init__(self, x, y, d):
        super().__init__(x, y, d)
        self.speed = 6
        self.r = 4
        self.step = 0
        self.damage = 10
        
    def draw(self, app):
        drawCircle(self.x - app.scrollX, self.y - app.scrollY, self.r,
                   fill = "orange")

class Box(Enemy):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 1
        self.r = 15
        self.damage = 0
        self.content = rand.choice([Meat(self.x, self.y), 
                                    Magnet(self.x, self.y), 
                                    Bomb(self.x, self.y)])
    
    def onStep(self, app):
        return

    def terminate(self, app):
        app.drop.append(self.content)
        app.enemies.remove(self)

    def draw(self, app):
        drawImage(app.boxImg, self.x - app.scrollX, self.y - app.scrollY, 
                  align = "center", width = 40, height = 40)
    

class Collectable():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Meat(Collectable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.r = 20
        self.value = 0
    
    def terminate(self, app):
        app.hero.hp += app.hero.maxHP * 0.5
        if app.hero.hp > app.hero.maxHP:
            app.hero.hp = app.hero.maxHP
        app.drop.remove(self)

    def draw(self, app):
        drawImage(app.meatImg, self.x - app.scrollX, self.y - app.scrollY, 
                  align = "center", width = 30, height = 30)

class Magnet(Collectable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.r = 20
        self.value = 0

    def terminate(self, app):
        for d in app.drop:
            if type(d) == Crystal:
                d.isSucked = True
        app.drop.remove(self)

    def draw(self, app):
        drawImage(app.magnetImg, self.x - app.scrollX, self.y - app.scrollY, 
                  align = "center", width = 30, height = 30)

class ScreenExplosion():
    def __init__(self):
        self.step = 0
        self.visibility = 0
        self.fadeOut = False

    def onStep(self, app):
        self.step += 1
        if not self.fadeOut:
            self.visibility += 5
            if self.visibility >= 100:
                self.visibility = 100
                for e in app.enemies:
                    if type(e) != Box:
                        app.drop.append(Crystal(e.x, e.y, e.drop))
                    else:
                        app.drop.append(rand.choice([Meat(e.x, e.y), 
                                                     Bomb(e.x, e.y), 
                                                    Magnet(e.x, e.y)]))
                app.enemies.clear()
                self.fadeOut = True
        else:
            self.visibility -= 5
        
        if self.step % (40) == 0:
            app.screenExplosions.remove(self)

    def draw(self, app):
        drawRect(0, 0, app.width, app.height, fill = "white", 
                     opacity = abs(self.visibility))

class Bomb(Collectable):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.r = 20
        self.value = 0

    def terminate(self, app):
        app.screenExplosions.append(ScreenExplosion())
        app.drop.remove(self)

    def draw(self, app):
        drawImage(app.bombImg, self.x - app.scrollX, self.y - app.scrollY, 
                  align = "center", width = 30, height = 30)

    

class Crystal(Collectable):
    def __init__(self, x, y, value):
        super().__init__(x, y)
        self.value = value
        self.r = 10
        if self.value == 1:
            self.color = "chartreuse"
        elif self.value == 2:
            self.color = "lightSkyBlue"
        elif self.value == 3:
            self.color = "gold"
        else:
            self.color = None
        self.isSucked = False
        self.step = 0
            
    def draw(self, app):
        drawRect(self.x - app.scrollX, self.y - app.scrollY, self.r,
                 self.r, fill = self.color, rotateAngle = 45,
                 border = "black", borderWidth = 1)
        
    def getSucked(self, app):
        flightspeed = 20
        a = angleTo(self.x, self.y, app.hero.x, app.hero.y)
        dx = flightspeed * math.sin(math.radians(a))
        dy = flightspeed * math.cos(math.radians(a))
        self.x += dx
        self.y -= dy

    def terminate(self, app):
        app.drop.remove(self)
        
def areaDamage(x, y, r, app, damage):
    for e in app.enemies:
        if distance(x, y, e.x, e.y) < r:
            e.loseHP(app, damage)


def onScreenPoint(app):
    posX = rand.randint(int(app.hero.x - 400), int(app.hero.x + 400))
    if posX < -600 or posX > 1400:
        return onScreenPoint(app)
    posY = rand.randint(int(app.hero.y - 300), int(app.hero.y + 300))
    if posY < -700 or posY > 1300:
        return onScreenPoint(app)
    
    return (posX, posY)