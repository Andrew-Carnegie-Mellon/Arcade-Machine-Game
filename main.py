from modulesArcade import *
import random
from PIL import Image
import os, pathlib
import sys
import joystick

def onAppStart(app):
    restart(app)
    
def loadText(filename, app):
    prefix = "images"
    suffix = ".png"
    with open(filename, "r") as f:
        theText = f.read()
    for skill in theText.split("*"):
        n, d = skill.split("$")
        app.skillDescription1[n] = []
        app.skillImg[n] = prefix + f'/{n}' + suffix
        for line in d.splitlines():
            if not line == "":
                app.skillDescription1[n].append(line)

def loadAssets(app):
    app.explosionIMGs = []
    for i in range(1, 11):
        temp = openImage(f"images/Explosion/{i}.png")
        app.explosionIMGs.append(CMUImage(temp))

    app.lightningIMGs = []
    for i in range(1, 5):
        temp = openImage(f"images/Lightning/{i}.png")
        app.lightningIMGs.append(CMUImage(temp))

    temp = openImage("images/Type-A Drone.png")
    app.droneAImg = [CMUImage(temp), 
                     CMUImage(temp.transpose(Image.FLIP_LEFT_RIGHT))]
    temp = openImage("images/Type-B Drone.png")
    app.droneBImg = [CMUImage(temp), 
                     CMUImage(temp.transpose(Image.FLIP_LEFT_RIGHT))]
    
    app.RPGImg = CMUImage(openImage("images/RPG.png"))
    app.drillShotImg = CMUImage(openImage("images/Drill Shot.png"))
    app.bombImg = CMUImage(openImage("images/Bomb.png"))
    app.magnetImg = CMUImage(openImage("images/Magnet.png"))
    app.meatImg = CMUImage(openImage("images/Meat.png"))
    app.boxImg = CMUImage(openImage("images/Box.png"))

def loadCharacters(app):
    app.profImg = CMUImage(openImage("images/Characters/Prof.png"))
    app.dikaImg = CMUImage(openImage("images/Characters/Dika.png"))
    app.emuImg = CMUImage(openImage("images/Characters/Emu.png"))
    app.faizImg = CMUImage(openImage("images/Characters/Faiz.png"))
    app.furqanImg = CMUImage(openImage("images/Characters/Furqan.png"))
    app.rashidImg = CMUImage(openImage("images/Characters/Rashid.png"))
    app.sherImg = CMUImage(openImage("images/Characters/Sherkhan.png"))
    app.sudaisImg = CMUImage(openImage("images/Characters/Sudais.png"))
    app.adamImg = CMUImage(openImage("images/Characters/Adam.png"))
    app.bossImg = CMUImage(openImage("images/Characters/DavidKosbie.png"))


def openImage(fileName):
    return Image.open(os.path.join(pathlib.Path(__file__).parent, fileName))

def determineSelection(app):
    res = []
    possibilitiesW = list(app.possibleSelectionW.keys())
    possibilitiesP = list(app.possibleSelectionP.keys())
    
    possibilities = possibilitiesW + possibilitiesP

    choiceSize = len(app.possibleSelectionW) + len(app.possibleSelectionP)
    if choiceSize >= 3:
        for _ in range(3):
            choose = choice(possibilities)
            res.append(choose)
            possibilities.remove(choose)
    else:
        res = possibilities
    
    return res

def applyChoice(app):
    choice = app.currentChoices[app.choice - 1]
    app.hero.skills[choice][1] += 1
    app.hero.skills[choice][0] = True
    #Taking care of 5 level limit for every upgrade
    if choice in app.possibleSelectionW:
        app.possibleSelectionW[choice] -= 1
        if choice not in app.currentSelectionW:
            app.currentSelectionW.append(choice)
        if app.possibleSelectionW[choice] == 0:
            app.possibleSelectionW.pop(choice)
    else:
        app.possibleSelectionP[choice] -= 1
        if choice not in app.currentSelectionP:
            app.currentSelectionP.append(choice)
        if app.possibleSelectionP[choice] == 0:
            app.possibleSelectionP.pop(choice)

    if choice == "Ronin Oyoroi":
        app.hero.armor += 1
    elif choice == "Fitness Guide":
        app.hero.hp = (app.hero.hp // app.hero.maxHP) * (app.hero.maxHP + 20)
        app.hero.maxHP += 20
    elif choice == "HE Fuel":
        app.hero.bulletR += 1
    elif choice == "Energy Cube":
        app.hero.bulletCD += 10
    elif choice == "Ammo Thruster":
        app.hero.bulletSpeed += 5
    elif choice == "Sports Shoes":
        app.hero.dx += 2
        app.hero.dy += 2
    elif choice == "Forcefield":
        app.forceField.levelUP()
    elif choice == "Type-A Drone":
        app.droneA.levelUP()
    elif choice == "Type-B Drone":
        app.droneB.levelUP()
    elif choice == "Drill Shot":
        app.hero.projectiles.append(DrillShot(app.hero.x, app.hero.y, 45))
    elif choice == "Lightning Emitter":
        app.lightningEmitter.r += 5
        app.lightningEmitter.CD += 5

    #Taking care of 4 weapon and passive limit
    if len(app.currentSelectionW) == 4:
        fullW = True
    else:
        fullW = False
    
    if fullW:
        newPos = dict()
        for w in app.currentSelectionW:
            if w in app.possibleSelectionW:
                newPos[w] = app.possibleSelectionW[w]
        app.possibleSelectionW = newPos

    if len(app.currentSelectionP) == 4:
        fullP = True
    else:
        fullP = False
    
    if fullP:
        newPos = dict()
        for p in app.currentSelectionP:
            if p in app.possibleSelectionP:
                newPos[p] = app.possibleSelectionP[p]
        app.possibleSelectionP = newPos

    app.skillChoice = False
    app.paused = False

def offScreenPoint(app):
    heroX = app.hero.x
    heroY = app.hero.y
    posX = random.randint(int(heroX - 450), int(heroX + 450))
    if posX < -600 or posX > 1400:
        return offScreenPoint(app)
    if posX < heroX - 400 or posX > heroX + 400:
        posY = random.randint(int(heroY - 350), int(heroY + 350))
    else:
        posY = choice([random.randint(int(heroY - 350), int(heroY - 300)), 
            random.randint(int(heroY + 300), int(heroY + 350))])
    
    if posY < -700 or posY > 1300:
        return offScreenPoint(app)
    else:
        return (posX, posY)

def spawnEnemies(app, *args):
    if len(app.enemies) < 7:
        for enemyType in args:
            for _ in range(5):
                posX, posY = offScreenPoint(app)
                
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
                else:
                    app.enemies.append(Wizard(posX, posY))
    

def restart(app):
    app.mainMenuScreen = True
    app.mode = 1
    app.bossFight = False
    app.victoryScreen = False
    app.continued = False
    app.confirm = False
    app.levelWidth = 2000
    app.levelHeight = 2000
    app.scrollX = 0
    app.scrollY = 0
    app.step = 0
    app.stepsPerSecond = 30
    app.hero = Hero(app.width // 2, app.height // 2)
    app.enemies = []
    app.arrows = []
    app.isGameOver = False
    app.drop = []
    app.screenExplosions = []
    app.selector = 0
    app.explosions = []
    app.lightning = []
    app.skillDescription1 = dict()
    app.skillImg = dict()
    loadText("SkillDscps1.txt", app)
    app.skillChoice = False
    app.paused = False
    loadAssets(app)
    loadCharacters(app)
    app.currentChoices = None
    app.choice = None
    app.droneA = Drone("A", app)
    app.droneB = Drone("B", app)
    app.forceField = Forcefield(app.hero.x, app.hero.y)
    app.lightningEmitter = LightningEmitter()
    app.currentSelectionW = []
    app.currentSelectionP = []
    app.drop.append(Bomb(500, 500))
    app.weapon = ["Type-A Drone", "Type-B Drone", "RPG", "Lightning Emitter",
                  "Forcefield", "Drill Shot"]
    app.passive = ["Ammo Thruster", "Energy Cube", "Fitness Guide", "HE Fuel",
                   "Ronin Oyoroi", "Sports Shoes"]
    

    app.possibleSelectionW = dict()
    app.possibleSelectionP = dict()
    for upgrade in app.skillDescription1:
        if upgrade in app.weapon:
            app.possibleSelectionW[upgrade] = 5
        else:
            app.possibleSelectionP[upgrade] = 5

    app.joy = "Yay"
    app.currentJoy = None
    app.isJoy = False
    app.joyTime = 0
    
def onStep(app):
    if not app.isGameOver and not app.paused and not app.mainMenuScreen:
        app.step += 1

        #Mob Spawning
        if app.mode == 2:
            enemy1 = random.randint(1, 7)
            enemy2 = random.randint(1, 7)
            spawnEnemies(app, enemy1, enemy2)
        else:
            if app.step == (app.stepsPerSecond * 900):
                app.bossFight = True
                app.hero.x = app.width // 2
                app.hero.y = app.height // 2 + 100
                app.enemies.clear()
                app.drop.clear()
                app.continued = True
                app.boss = Boss(app.width // 2, app.height // 2)
                app.enemies.append(app.boss)
                app.paused = True
            elif app.step < (app.stepsPerSecond * 900):
                wave = app.step // (app.stepsPerSecond * 150)
                spawnEnemies(app, wave + 1, wave + 2)

        if not app.bossFight:
            if app.step % (app.stepsPerSecond * 30) == 0:
                posX = choice([-50, 650, choice([200, 400])])
                if posX == -50 or posX == 650:
                    posY = choice([-50, 250, 550, 850])
                else:
                    posY = choice([-50, 850])
                app.enemies.append(Box(posX - app.scrollX, posY - app.scrollY))
        
        app.hero.onStep(app)

        if app.hero.skills["RPG"][0] and \
            app.step % (app.stepsPerSecond * 4) == 0:
            target = app.hero.findClosestEnemy(app, 200)
            if target != None:
                app.hero.projectiles.append(RPGRocket(app.hero.x, app.hero.y, 
                                                    app.hero.aimDir, target[0], 
                                                    target[1]))
                
        if app.hero.skills["Forcefield"][0]:
            app.forceField.onStep(app)
            
        if app.hero.skills["Type-A Drone"][0]:
            app.droneA.onStep(app)

        if app.hero.skills["Type-B Drone"][0]:
            app.droneB.onStep(app)
        
        if app.hero.skills["Lightning Emitter"][0]:
            app.lightningEmitter.onStep(app)
        
        #Projectile mechanics
        i = 0
        while i < len(app.hero.projectiles):
            p = app.hero.projectiles[i]
            p.onStep(app)
            #Out of bound projectiles
            if type(p) != DrillShot:
                if p.x - app.scrollX < 0 or p.x - app.scrollX > app.width or \
                    p.y - app.scrollY < 0 or p.y - app.scrollY > app.height:
                        p.terminate(app)
                        break

            #Collision with enemies
            temp = len(app.hero.projectiles)
            for j in range(len(app.enemies)):
                e = app.enemies[j]
                if type(p) == DrillShot:
                    if e.checkCollisionDrill(app, p):
                        e.loseHP(app, p.damage)
                        break
                else:
                    if e.checkCollision(p):
                        e.loseHP(app, p.damage)
                        p.terminate(app)
                        break
            if temp == len(app.hero.projectiles):
                i += 1
                
            
        
        #Enemy movement and direct damage mechanics
        for e1 in app.enemies:
            e1.onStep(app)
            for e2 in app.enemies:
                if e1 != e2:
                    if e1.checkCollision(e2):
                        e1.knockback(e2, 3, app)
            if app.hero.checkCollision(e1):
                app.hero.knockback(e1, 3, app)
                app.hero.loseHP(e1.damage, app)
        
        #Enemy projectile mechanics
        i = 0
        while i < len(app.arrows):
            a = app.arrows[i]
            a.onStep(app)
            if a.x - app.scrollX < 0 or a.x - app.scrollX > app.width or \
               a.y - app.scrollY < 0 or a.y - app.scrollY > app.height:
                app.arrows.pop(i)
            elif app.hero.checkCollision(a):
                app.hero.knockback(a, 2, app)
                app.hero.loseHP(a.damage, app)
                app.arrows.pop(i)
            else:
                i += 1
                
        #Drop collection and level up mechanics
        i = 0
        while i < len(app.drop):
            d = app.drop[i]
            if type(d) == Crystal and d.isSucked:
                d.getSucked(app)
            if app.hero.checkDropCollision(d):
                app.hero.exp += d.value
                if app.hero.exp >= app.hero.levelEXPReq:
                    app.hero.levelUP(app)
                    if len(app.possibleSelectionW) + \
                        len(app.possibleSelectionP) >= 1:
                        app.currentChoices = determineSelection(app)
                        app.skillChoice = True
                        app.paused = True
                d.terminate(app)
            else:
                i += 1

        for e in app.explosions: 
            e.onStep(app)

        for l in app.lightning:
            l.onStep(app)

        for e in app.screenExplosions:
            e.onStep(app)

    if app.isJoy and app.mainMenuScreen:
        app.joyTime += 1
        if app.joyTime == (app.stepsPerSecond // 2):
            mainMenuMovement(app, app.currentJoy)
            app.joyTime = 0
            app.isJoy = False

    if app.isJoy and app.skillChoice:
        app.joyTime += 1
        if app.joyTime == (app.stepsPerSecond // 2):
            skillMenuMovement(app, app.currentJoy)
            app.joyTime = 0
            app.isJoy = False

def drawTree(app, x, y, size=70):
    greenRadius = size // 2
    trunkWidth = size // 4
    trunkHeight = size // 3
    
    # Drawing green part of a tree
    drawOval(x - app.scrollX, y - app.scrollY, size, size, fill = 'green', 
             border = 'darkgreen', borderWidth = 2)
    
    # Drawing trunk of a tree
    drawRect(x - app.scrollX - trunkWidth // 2, 
             y - app.scrollY + greenRadius - trunkHeight // 2, 
            trunkWidth, trunkHeight, fill = 'saddlebrown')
    
def drawStone(app, x, y, size=30, baseColor='gray', borderColor='darkGray'):
    # Main base stone shape
    drawOval(x - app.scrollX, y - app.scrollY, size * 1.5, size, 
             fill = baseColor, border = borderColor, borderWidth = 1)
    
    # Adding smaller shapes for irregularity
    drawOval(x - size * 0.2 - app.scrollX, y - size * 0.2 - app.scrollY, 
             size * 0.8, size * 0.5, fill = 'lightGray')
    drawOval(x + size * 0.2 - app.scrollX, y + size * 0.2 - app.scrollY, 
             size * 0.6, size * 0.4, fill = 'darkGray')
    
    # Drawing shades
    drawArc(x - app.scrollX, y + size * 0.1 - app.scrollY, 
            size * 1.4, size * 0.8, 180, 360, fill='darkGray')
    drawArc(x - app.scrollX, y - size * 0.1 - app.scrollY, 
            size * 1.2, size * 0.6, 0, 180, fill='lightGray')

def drawEXPBar(app):
    drawRect(50, 25, 700, 45, fill = "lightSlateGray", border = "black",
             opacity = 75)
    expBar = 700 * app.hero.exp // app.hero.levelEXPReq + 0.01
    drawRect(50, 25, expBar, 45, fill = "green", border = "black",
             opacity = 75)
    
def drawBossHealthBar(app):
    drawRect(50, 25, 700, 45, fill = "lightSlateGray", border = "black",
             opacity = 75)
    bossHP = abs(700 * app.boss.hp // 1000) + 0.01
    drawRect(50, 25, bossHP, 45, fill = "red", border = "black",
             opacity = 75)

def drawGameOverScreen(app):
    mins = str(app.step // app.stepsPerSecond // 60)
    secs = str(app.step // app.stepsPerSecond % 60)
    if int(secs) < 10:
        secs = "0" + str(secs)
    drawRect(150, 100, 500, 400, fill = "darkGray")
    drawLabel("You Lost!", app.width // 2, app.height // 2 - 50,
              fill = "gold", size = 30, font = "Luckiest Guy")
    drawLabel("Press R to try again", app.width // 2, app.height // 2,
              fill = "gold", size = 28, font = "Luckiest Guy")
    drawLabel(f"Survived Time: {mins}:{secs}", 
              app.width // 2, app.height // 2 + 50, font = "Luckiest Guy",
              fill = "gold", size = 28)
    
def drawVictoryScreen(app):
    if app.confirm:
        drawImage("images/Ducky.PNG", 0, 0, width = app.width, 
                  height = app.height)
        return
    drawRect(0, 0, app.width, app.height, 
             fill = gradient('darkblue', 'black', start='top'))
    # Victory Title
    titleSize = 50
    drawLabel("Campus Survivor", app.width / 2, app.height / 6,
              size=titleSize, fill='gold', bold=True, align='center',
              font = "Luckiest Guy")

    # Congratulations Label
    congratsSize = 25
    drawLabel("Congratulations, you completed the game!", app.width / 2, 
              app.height / 6 + 70,size=congratsSize, font = "Luckiest Guy",
              fill='gold', align='center')

    # Replay Instructions
    replaySize = 20
    drawLabel("Press 'R' to play again", app.width / 2, app.height * 5 / 6 - 60,
              size=replaySize, fill='seagreen', align='center',
              font = "Luckiest Guy")

    # Claim Instructions
    drawLabel("Click the button below to claim your reward!", app.width / 2, 
              app.height * 5 / 6 - 20,
              size=replaySize, fill='crimson', align='center',
              font = "Luckiest Guy")

    # Draw "Claim" Button
    buttonWidth, buttonHeight = 150, 50
    buttonX, buttonY = app.width / 2 - buttonWidth / 2, app.height - 80
    drawRect(buttonX, buttonY, buttonWidth, buttonHeight, 
             fill='seagreen', border='white', borderWidth=2)
    drawLabel("Claim", buttonX + buttonWidth / 2, buttonY + buttonHeight / 2, 
              size=25, fill='white', bold=True, font = "Luckiest Guy")
    selectorR = 25 // math.cos(math.radians(30))
    drawStar(buttonX - 75, buttonY, selectorR, 3, fill = "gold", 
             border = "white")

def drawContinueScreen(app):
    drawRect(0, 0, app.width, app.height, 
             fill = gradient('darkblue', 'black', start='top'))
    # Victory Title
    titleSize = 50
    drawLabel("Danger!", app.width / 2, app.height / 6,
              size=titleSize, fill='gold', bold=True, align='center',
              font = "Luckiest Guy")

    # Congratulations Label
    congratsSize = 25
    drawLabel("Your source code for Gradebook has been leaked!", app.width / 2, 
              app.height / 6 + 70,size=congratsSize, font = "Luckiest Guy",
              fill='gold', align='center')

    # Replay Instructions
    replaySize = 20
    drawLabel("Psychopath is coming for you!", app.width / 2, 
              app.height * 5 / 6 - 60, size=replaySize, fill='seagreen', 
              align='center',font = "Luckiest Guy")

    # Claim Instructions
    drawLabel("Click the button below to continue", app.width / 2, 
              app.height * 5 / 6 - 20,
              size=replaySize, fill='crimson', align='center',
              font = "Luckiest Guy")

    # Draw "Claim" Button
    buttonWidth, buttonHeight = 150, 50
    buttonX, buttonY = app.width / 2 - buttonWidth / 2, app.height - 80
    drawRect(buttonX, buttonY, buttonWidth, buttonHeight, 
             fill='seagreen', border='white', borderWidth=2)
    drawLabel("Continue", buttonX + buttonWidth / 2, buttonY + buttonHeight / 2, 
              size=25, fill='white', bold=True, font = "Luckiest Guy")
    
    selectorR = 25 // math.cos(math.radians(30))
    drawStar(buttonX - 75, buttonY, selectorR, 3, fill = "gold", 
             border = "white", roundness = 0)

def drawWalls(app):
    #Left Wall
    drawRect(-650 - app.scrollX, -750 - app.scrollY, 50, 2100,
             fill = "sienna")
    #Bottom Wall
    drawRect(-650 - app.scrollX, 1300 - app.scrollY, 2100, 50,
             fill = "sienna")
    #Top Wall
    drawRect(-650 - app.scrollX, -750 - app.scrollY, 2100, 50,
             fill = "sienna")
    #Right Wall
    drawRect(1400 - app.scrollX, -750 - app.scrollY, 50, 2100,
             fill = "sienna")
    
def drawBossWall(app):
    drawRect(-50 - app.scrollX, -50 - app.scrollY, 50, app.height + 100,
             fill = "sienna")
    drawRect(-50 - app.scrollX, -50 - app.scrollY, app.width + 100, 50,
             fill = "sienna")
    drawRect(-50 - app.scrollX, app.height - app.scrollY, app.width + 100, 50,
             fill = "sienna")
    drawRect(app.width - app.scrollX, -50 - app.scrollY, 50, app.height + 100, 
             fill = "sienna")
    
def drawSkillSelectionMenu(app):
    drawRect(200, 25, 400, 75, fill = "gold", border = "black")
    drawLabel("Skill Choice", 400, 62.5, font = "Luckiest Guy", size = 50,
              fill = "white", border = "black", borderWidth = 1)
    drawPolygon(25, 125, 25, 185, 365, 185, 415, 125, border = "black",
                fill = "lightSlateGray", rotateAngle = 0.001)
    drawPolygon(25, 125, 25, 185, 75, 185, 125, 125, fill = "gold",
                border = "black", rotateAngle = 0.002)
    drawPolygon(775, 125, 775, 185, 385, 185, 435, 125, border = "black",
                fill = "lightSlateGray", rotateAngle = 0.001)
    drawPolygon(775, 125, 775, 185, 675, 185, 725, 125, fill = "limeGreen",
                border = "black", rotateAngle = 0.002)
    
    for i in range(133, 315, 58):
        drawRect(i, 130, 50, 50, fill = rgb(51, 60, 81), border = "black")

    temp = 0
    for weapon in app.currentSelectionW:
        posX = 158 + temp * 58
        posY = 155
        drawImage(app.skillImg[weapon], posX, posY, align = "center",
                  height = 30, width = 30)
        temp += 1
    
    for i in range(443, 675, 58):
        drawRect(i, 130, 50, 50, fill = rgb(51, 60, 81), border = "black")

    temp = 0
    for passive in app.currentSelectionP:
        posX = 468 + temp * 58
        posY = 155
        drawImage(app.skillImg[passive], posX, posY, align = "center", 
                  width = 30, height = 30)
        temp += 1

    if len(app.currentChoices) == 3:
        drawThreeColumns(app)
    elif len(app.currentChoices) == 2:
        drawTwoColumns(app)
    else:
        drawOneColumn(app)
    

def drawThreeColumns(app):
    for i in range(25, 800, 258):
        drawRect(i, 210, 233, 365, fill = "lightSlateGray", border = "black")
        drawRect(i, 210, 233, 50, fill = "gold", border = "black")
        drawRect(i + 10, 360, 213, 145, fill = rgb(51, 60, 81),
                 border = "black")
        drawRect(i + 10, 510, 213, 55, fill = rgb(51, 60, 81),
                 border = "black")
        if i // 258 == app.selector:
            drawRect(i, 210, 233, 365, fill = None, border = "white")
    
    for i in range(3):
        centerY = 538
        centerX = 70 + i *  258
        for j in range(5):
            temp = centerX + j * 36
            drawStar(temp, centerY, 17, 5, fill = rgb(20, 27, 43),
                     border = "black", roundness = 50)
            
        for j in range(app.hero.skills[app.currentChoices[i]][1]):
            temp = centerX + j * 36
            drawStar(temp, centerY, 17, 5, fill = "gold",
                     border = "black", roundness = 50)
    
    choice = 0
    for i in range(142, 800, 258):
        if app.currentChoices != None:
            choiceName = app.currentChoices[choice]
            drawLabel(choiceName, i, 235, size = 25, 
                      fill = "white", border = "black", font = "Luckiest Guy", 
                      borderWidth = 1)
            drawImage(app.skillImg[choiceName], i, 300, align = "center")
            

            for j in range(len(app.skillDescription1[choiceName])):
                line = app.skillDescription1[choiceName][j]
                textPosY = 380 + j * 25
                drawLabel(line, i, textPosY, size = 18,
                    fill = "white", border = "black", font = "Luckiest Guy",
                    borderWidth = 1)
            choice += 1

def drawTwoColumns(app):
    for i in range(155, 414, 258):
        drawRect(i, 210, 233, 365, fill = "lightSlateGray", border = "black")
        drawRect(i, 210, 233, 50, fill = "gold", border = "black")
        drawRect(i + 10, 360, 213, 145, fill = rgb(51, 60, 81),
                 border = "black")
        drawRect(i + 10, 510, 213, 55, fill = rgb(51, 60, 81),
                 border = "black")
        if i // 258 == app.selector:
            drawRect(i, 210, 233, 365, fill = None, border = "white")
    
    for i in range(2):
        centerY = 538
        centerX = 200 + i *  258
        for j in range(5):
            temp = centerX + j * 36
            drawStar(temp, centerY, 17, 5, fill = rgb(20, 27, 43),
                     border = "black", roundness = 50)
            
        for j in range(app.hero.skills[app.currentChoices[i]][1]):
            temp = centerX + j * 36
            drawStar(temp, centerY, 17, 5, fill = "gold",
                     border = "black", roundness = 50)
    
    choice = 0
    for i in range(272, 600, 258):
        if app.currentChoices != None:
            choiceName = app.currentChoices[choice]
            drawLabel(choiceName, i, 235, size = 25, 
                      fill = "white", border = "black", font = "Luckiest Guy", 
                      borderWidth = 1)
            drawImage(app.skillImg[choiceName], i, 300, align = "center")
            

            for j in range(len(app.skillDescription1[choiceName])):
                line = app.skillDescription1[choiceName][j]
                textPosY = 380 + j * 25
                drawLabel(line, i, textPosY, size = 18,
                    fill = "white", border = "black", font = "Luckiest Guy",
                    borderWidth = 1)
            choice += 1

def drawOneColumn(app):
    for i in range(284, 300, 258):
        drawRect(i, 210, 233, 365, fill = "lightSlateGray", border = "black")
        drawRect(i, 210, 233, 50, fill = "gold", border = "black")
        drawRect(i + 10, 360, 213, 145, fill = rgb(51, 60, 81),
                 border = "black")
        drawRect(i + 10, 510, 213, 55, fill = rgb(51, 60, 81),
                 border = "black")
        drawRect(i, 210, 233, 365, fill = None, border = "white")
    
    for i in range(1):
        centerY = 538
        centerX = 329 + i *  258
        for j in range(5):
            temp = centerX + j * 36
            drawStar(temp, centerY, 17, 5, fill = rgb(20, 27, 43),
                     border = "black", roundness = 50)
            
        for j in range(app.hero.skills[app.currentChoices[i]][1]):
            temp = centerX + j * 36
            drawStar(temp, centerY, 17, 5, fill = "gold",
                     border = "black", roundness = 50)
    
    choice = 0
    for i in range(401, 500, 258):
        if app.currentChoices != None:
            choiceName = app.currentChoices[choice]
            drawLabel(choiceName, i, 235, size = 25, 
                      fill = "white", border = "black", font = "Luckiest Guy", 
                      borderWidth = 1)
            drawImage(app.skillImg[choiceName], i, 300, align = "center")
            

            for j in range(len(app.skillDescription1[choiceName])):
                line = app.skillDescription1[choiceName][j]
                textPosY = 380 + j * 25
                drawLabel(line, i, textPosY, size = 18,
                    fill = "white", border = "black", font = "Luckiest Guy",
                    borderWidth = 1)
            choice += 1

def drawMainMenu(app):
    drawRect(0, 0, app.width, app.height, 
             fill = gradient('darkblue', 'black', start='top'))
    # Title
    drawLabel('Campus Survivor', app.width / 2, app.height / 5,
                  size = 50, fill='gold', bold = True, font = "Luckiest Guy")
    
    # Buttons
    buttonWidth, buttonHeight = 200, 50
    buttonSpacing = 20
    buttonColors = ['dodgerblue', 'seagreen', 'crimson']
    buttonText = ['Story Mode', 'Endless Mode', 'Exit']
    
    startY = app.height / 3 + 50
    for i, text in enumerate(buttonText):
        # Create button background
        buttonX = app.width / 2
        buttonY = startY + i * (buttonHeight + buttonSpacing)
        drawRect(buttonX - buttonWidth / 2, buttonY - buttonHeight / 2,
                      buttonWidth, buttonHeight, fill=buttonColors[i],
                      border = 'white', borderWidth = 2)
        
        # Create button text
        drawLabel(text, buttonX, buttonY, size=25, fill='white', bold=True, 
                  font = "Luckiest Guy")
        
    selectorR = 25 // math.cos(math.radians(30))
    selectorY = startY + buttonHeight / 2 + \
        app.selector * (buttonHeight + buttonSpacing) - buttonHeight / 2
    selectorX = buttonX - buttonWidth / 2
    drawRegularPolygon(selectorX - 50, selectorY, selectorR, 3, fill = "gold", 
             border = "white", rotateAngle = 90, borderWidth = 2)
    

def redrawAll(app):
    if app.mainMenuScreen:
        drawMainMenu(app)
    else:
        drawRect(0, 0, app.width, app.height, fill="darkKhaki")
        drawTree(app, 400, 500)
        drawStone(app, -300, -200)
        drawTree(app, -400, -500)
        drawStone(app, 1200, 1100)
        drawWalls(app)

        for d in app.drop:
            d.draw(app)
        
        app.hero.draw(app)

        for e in app.enemies:
            e.draw(app)

        if app.hero.skills["Forcefield"][0]:
            app.forceField.draw(app)
        if app.hero.skills["Type-A Drone"][0]:  
            app.droneA.draw(app)
        if app.hero.skills["Type-B Drone"][0]:  
            app.droneB.draw(app)
            
        if not app.isGameOver:
            app.hero.drawHealthBar(app)
            for p in app.hero.projectiles:
                p.draw(app)
            for a in app.arrows:
                a.draw(app)
            for e in app.explosions:
                e.draw(app)
            for l in app.lightning:
                l.draw(app)
            for e in app.screenExplosions:
                e.draw(app)
            if app.bossFight:
                drawBossWall(app)
                app.boss.draw(app)
        else:
            drawGameOverScreen(app)

        if app.skillChoice:
            drawSkillSelectionMenu(app)
        else:
            if not app.bossFight:
                drawEXPBar(app)
            else:
                drawBossHealthBar(app)
        
        if app.continued:
            drawContinueScreen(app)

        if app.victoryScreen:
            drawVictoryScreen(app)
    
    drawLabel(app.joy, 700, 100, fill = "black", size = 30)

def onJoyPress(app, button, joystick):
    app.joy = button
    if button == '5':
        sys.exit(0)
    if button == "1":
        restart(app)
    
    if app.paused:
        if app.skillChoice:
            if button == '8':
                app.choice = app.selector + 1
                applyChoice(app)

    if app.mainMenuScreen:
        if button == '8':
            if app.selector < 2:
                app.mode = app.selector + 1
                app.mainMenuScreen = False
            elif app.selector == 2:
                sys.exit(0)

    if app.continued:
        if button == '8' or button == '9':
            app.continued = False
            app.paused = False

    if app.victoryScreen:
        if button == '8' or button == '9':
            app.confirm = True

def mainMenuMovement(app, move):
    if move == (1, -1):
        app.selector -= 1
        if app.selector == -1:
            app.selector = 2
    elif move == (1, 1):
        app.selector += 1
        if app.selector == 3:
            app.selector = 0

def skillMenuMovement(app, move):
    if len(app.currentChoices) == 3:
        upperBound = 3
    elif len(app.currentChoices) == 2:
        upperbound = 2
    else:
        upperbound = 1

    if move == (0, -1):
        app.selector -= 1
        if app.selector == -1:
            app.selector = 2
    elif move == (0, 1):
        app.selector += 1
        if app.selector == upperbound:
            app.selector = 0

def onDigitalJoyAxis(app, results, joystick):
    app.joy = str(results)
    if not app.isGameOver and not app.paused:
        if not app.bossFight:
            if (1, -1) in results and app.hero.y - app.hero.r > -700:
                app.hero.y -= app.hero.dy
                if app.hero.y - app.scrollY < 0.2 * app.height:
                    app.scrollY -= app.hero.dy
            if (1, 1) in results and app.hero.y + app.hero.r < 1300:
                app.hero.y += app.hero.dy
                if app.hero.y - app.scrollY > 0.8 * app.height:
                    app.scrollY += app.hero.dy
            if (0, -1) in results and app.hero.x - app.hero.r > -600:
                app.hero.x -= app.hero.dx
                if app.hero.x - app.scrollX < 0.2 * app.width:
                    app.scrollX -= app.hero.dx
            if (0, 1) in results and app.hero.x + app.hero.r < 1400:
                app.hero.x += app.hero.dx
                if app.hero.x - app.scrollX > 0.8 * app.width:
                    app.scrollX += app.hero.dx
        else:
            if (1, -1) in results and app.hero.y - app.hero.r > 0:
                app.hero.y -= app.hero.dy
                if app.hero.y - app.scrollY < 0.2 * app.height:
                    app.scrollY -= app.hero.dy
            if (1, 1) in results and app.hero.y + app.hero.r < app.height:
                app.hero.y += app.hero.dy
                if app.hero.y - app.scrollY > 0.8 * app.height:
                    app.scrollY += app.hero.dy
            if (0, -1) in results and app.hero.x - app.hero.r > 0:
                app.hero.x -= app.hero.dx
                if app.hero.x - app.scrollX < 0.2 * app.width:
                    app.scrollX -= app.hero.dx
            if (0, 1) in results and app.hero.x + app.hero.r < app.width:
                app.hero.x += app.hero.dx
                if app.hero.x - app.scrollX > 0.8 * app.width:
                    app.scrollX += app.hero.dx

    if app.mainMenuScreen:
        if (1, -1) in results:
            if app.currentJoy != (1, -1):
                app.joyTime = 0
            app.currentJoy = (1, -1)
            app.isJoy = True
        if (1, 1) in results:
            if app.currentJoy != (1, 1):
                app.joyTime = 0
            app.currentJoy = (1, 1)
            app.isJoy = True

    if app.skillChoice:
        if (0, -1) in results:
            if app.currentJoy != (0, -1):
                app.joyTime = 0
            app.currentJoy = (0, -1)
            app.isJoy = True
        if (0, 1) in results:
            if app.currentJoy != (0, 1):
                app.joyTime = 0
            app.currentJoy = (0, 1)
            app.isJoy = True

runApp(height = 600, width = 800)