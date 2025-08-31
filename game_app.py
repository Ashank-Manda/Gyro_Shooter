from motion_server import startMotionServer
from motion_server import playerRotation, playerStart, playerConnected
from motion_server import shootButtonPressedDict, specialAttackButtonPressedDict
import math
import threading
import random as random_module
from cmu_graphics import *

def onAppStart(app):
    app.gameOver = False
    app.startButton = Button(app.width//2, 5*app.height//8, 
                             app.width//3, app.height//12, "Press To Start", 20)
    app.instructionsButton = Button(9*app.width//10, app.height//10, 
                                    50, 50, "?", 40)
    app.instructions = False
    gameAudioUrl = '../src/Sounds/GameAudio.wav'
    app.gameAudio = Sound(gameAudioUrl)
    app.gameAudio.play(loop=True)

    
    reset(app)

def resetGame(app):
    app.bullets = []
    app.beams = []
    app.velocity = 1
    app.numberOfBullets = 1
    # Initial spaceships position
    app.spaceShip1X = app.width // 2
    app.spaceShip1Y = 400
    app.spaceShip1 = SpaceShip(app.spaceShip1X, app.spaceShip1Y, "p1", 
                               app.chosenShipIndex1, app)

    app.spaceShip2X = app.width // 4
    app.spaceShip2Y = 400
    app.spaceShip2 = SpaceShip(app.spaceShip2X, app.spaceShip2Y, "p2", 
                               app.chosenShipIndex2, app)

    app.spaceShipList = [app.spaceShip1, app.spaceShip2]

    # Movement & firing parameters
    app.steeringMultiplier = 0.02
    app.asteroids = []
    app.powerUps = []

    # Firing delay and step rate
    app.fireDelay = 5
    app.delayTime = 10
    app.stepsPerSecond = 200
    app.paused = False

    #Game difficulty parameters
    app.level = 2
    app.lowerAsteroidSpeed = 1
    app.higherAsteroidSpeed = 2
    

    #PowerUp Variables
    app.asteroidsDestroyed = 1

    #To restart game
    app.winAdded = False

def reset(app):
    app.screen = "Start"
    app.backgroundUrl = 'src/Sprites/Background.png'

    app.spaceShipGif = 'src/Sprites/SpaceShip.gif'

    app.bullet = 'src/Sprites/Bullet1.gif'
    bulletUrl = '../src/Sounds/ShootingBullet.wav'
    app.bulletSound = Sound(bulletUrl)
    bulletHit = '../src/Sounds/BulletHit.mp3'
    app.bulletHitSound = Sound(bulletHit)
    app.beamAttack = 'src/Sprites/BeamAttack'
    beamUrl = '../src/Sounds/BeamSound.wav'
    app.beamSound = Sound(beamUrl)


    #Asteroid
    app.explodingAsteroid = 'src/Sprites/ExplodingAsteroid'
    app.baseAsteroid = 'src/Sprites/baseAsteroid.gif'
    asteroidSoundUrl = '../src/Sounds/AsteroidExplosion.wav'
    app.asteroidExplosionSound = Sound(asteroidSoundUrl)

    #PowerUps
    app.healthPowerUp = 'src/Sprites/PowerUps/PowerUp1.gif'
    app.shipSpeedPowerUp = 'src/Sprites/PowerUps/PowerUp2.gif'
    app.bulletPowerUp = 'src/Sprites/PowerUps/PowerUp3.gif'
    app.shipUpgradePowerUp = 'src/Sprites/PowerUps/PowerUP4.gif'
    app.specialAttackPowerUp = 'src/Sprites/PowerUps/PowerUp5.gif'

    powerUpUrl = '../src/Sounds/PowerUpPickUp.wav'
    app.powerUpSound = Sound(powerUpUrl)
    app.powerUpList = [app.healthPowerUp, 
                       app.bulletPowerUp, 
                       app.shipSpeedPowerUp]

    resetGameLogic(app)
    resetGame(app)

    # Start the motion server thread
    threading.Thread(target=startMotionServer, 
                     daemon=True).start() 

def resetGameLogic(app):
    #For GameBoard Screen
    app.raceTrack = "src/Sprites/Racetrack.png"
    app.showingWinsDelay = 100

    #Game Logic
    app.p1Wins = 0 
    app.p2Wins = 0
    app.p1Position = 100
    app.p2Position = 100
    app.p1FinalPosition = 100
    app.p2FinalPosition = 100

    #For connecting
    app.spaceShipOptions = ['src/Sprites/SpaceShip.gif', 
                            'src/Sprites/Scout.png', 
                            'src/Sprites/SpaceShip3.png']
    app.chosenShipIndex1 = 1
    app.chosenShipIndex2 = 0
    app.movementDelay = 0


def onResize(app):
    app.startButton = Button(app.width//2, 5*app.height//8, 
                             app.width//3, app.height//12, "Press To Start", 20)
    app.instructionsButton = Button(9*app.width//10, app.height//10, 
                                    50, 50, "?", 40)
    app.spaceShip1 = SpaceShip(app.spaceShip1X, app.spaceShip1Y, "p1", 
                               app.chosenShipIndex1, app)
    app.spaceShip2 = SpaceShip(app.spaceShip2X, app.spaceShip2Y, "p2", 
                               app.chosenShipIndex2, app)
    
# Entity Classes
class Button: 
    def __init__(self, cx, cy, width, height, label, fontSize):
        self.cx = cx
        self.cy = cy
        self.width = width
        self.height = height
        self.label = label
        self.fontSize = fontSize
    
    def drawButton(self):
        drawRect(self.cx - self.width//2, self.cy - self.height//2, 
                 self.width, self.height, fill = "orange", border = "white")
        drawLabel(self.label, self.cx, self.cy, font = "Orbitron", 
                  size = self.fontSize, fill = "white", bold = True)
    def isClicked(self, mouseX, mouseY):
        left = self.cx - self.width//2
        right = self.cx + self.width//2
        bottom = self.cy - self.height//2
        top =  self.cy + self.height//2
        return ((left <= mouseX <= self.cx + right) and
            (bottom <= mouseY <= self.cy + top))
    
class SpaceShip:
    def __init__(self, x, y, id, index, app):
        self.x = x
        self.y = y
        self.id = id
        self.rotation = 0
        self.size = 100
        self.index = index
        self.r = self.size / 2
        self.health = 100
        self.link = app.spaceShipOptions[self.index]
        self.maxBullets = 100
        self.velocity = app.velocity
        self.numberOfBullets = app.numberOfBullets
        self.bullets = app.bullets
        self.fireCooldown = 0
        self.specialAttacks = 3

    def drawSpaceShip(self):
        xDistanceFromBar = math.cos(self.rotation)
        yDistanceFromBar = -math.sin(self.rotation)

        drawImage(self.link, self.x, self.y, width=self.size, height=self.size,
                  rotateAngle=math.degrees(self.rotation), align='center')
        if self.health > 0:
            drawRect(self.x + xDistanceFromBar, self.y - yDistanceFromBar + 50, 
                    50, 10, fill='gray',
                    rotateAngle=math.degrees(self.rotation), align='center')
            if self.health > 70:
                healthColor = 'green'
            elif self.health > 40:
                healthColor = 'yellow'
            else:
                healthColor = 'red'
            try:
                drawRect((self.x + xDistanceFromBar - (100 - self.health) / 2), 
                        self.y  - yDistanceFromBar + 50, self.health//2, 10,
                        fill=healthColor, 
                        rotateAngle=math.degrees(self.rotation), align='center')
            except:
                return
    
    def moveSpaceShip(self, app):
        self.rotation += -playerRotation[self.id] * app.steeringMultiplier

        # Update position and rotation from phone
        self.x += self.velocity * math.sin(self.rotation)
        self.y -= self.velocity * math.cos(self.rotation)


        # Keep SpaceShip in Bounds
        if (self.x + self.r >= app.width):
            self.x = app.width - self.r
        if (self.x - self.r <= 0):
            self.x = self.r + 20
        if (self.y + self.r >= app.height):
            self.y = app.height - self.r
        if (self.y - self.r <= 0):
            self.y = self.r + 20

    def shoot(self, app):
        # Handle firing delay and new bullets
        app.fireDelay -= 1
        if app.fireDelay <= 0:
            app.fireDelay = app.delayTime
            if len(app.bullets) < self.maxBullets:
                for i in range(self.numberOfBullets):
                    angleOffset = (i - (self.numberOfBullets - 1) / 2) * 0.1
                    newRotation = self.rotation + angleOffset
                    app.bullets.append(Bullet(self.x-8, self.y, 
                                              newRotation, app, self.id))
                    app.bulletSound.play()
    def shootSpecial(self, app):
        if self.specialAttacks > 0:
            beamOffset = self.r + 150 # Adjust this value for spacing
            beamX = self.x + beamOffset * math.sin(self.rotation)
            beamY = self.y - beamOffset * math.cos(self.rotation)
            app.beams.append(BeamAttack(beamX, beamY, 
                                        self.rotation, app, self.id))
            self.specialAttacks -= 1

class Bullet:
    def __init__(self, x, y, rotation, app, ownerId):
        self.x = x
        self.y = y
        self.size = 20
        self.r = self.size / 2
        self.link = app.bullet
        self.speed = 10
        self.rotation = rotation
        self.id = ownerId

    def move(self):
        self.x += self.speed * math.sin(self.rotation)
        self.y -= self.speed * math.cos(self.rotation)

    def drawBullet(self, app):
        drawImage(self.link, self.x, self.y, width=self.size, height=self.size)

class BeamAttack:
    def __init__(self, x, y, rotation, app, ownerId):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.length = 300
        self.width = 50
        self.ownerId = ownerId
        self.frames = [f'{app.beamAttack}/Beam{i}.gif' for i in range(1, 9)]
        self.frameIndex = 0
        self.active = True
        self.timer = 0
        self.duration = 15
        self.hitAsteroids = set()

    def update(self):
        self.frameIndex = (self.frameIndex + 1) % len(self.frames)
        self.timer += 1
        if self.timer > self.duration:
            self.active = False


    def drawBeam(self):
        drawImage(self.frames[self.frameIndex], self.x, self.y, 
                  width=self.width, height=self.length, 
                  rotateAngle=math.degrees(self.rotation), align='center')


class Asteroid:
    def __init__(self, x, y, size, app):
        self.x = x
        self.y = y
        self.size = size
        self.r = size / 2
        self.link = app.baseAsteroid
        self.speed = random_module.randint(app.lowerAsteroidSpeed, 
                                           app.higherAsteroidSpeed)
        
        self.isExploding = False
        self.explosionFrames = [f'{app.explodingAsteroid}/Asteroid{i}.gif' 
                                for i in range(1, 9)]
        self.explosionIndex = 0
        self.isDestroyed = False

        
    def drawAsteroid(self):
        if self.isExploding:
            drawImage(self.explosionFrames[self.explosionIndex], self.x, self.y, 
                      width=self.size, height=self.size)
        elif not self.isDestroyed:
            drawImage(self.link, self.x, self.y, 
                      width=self.size, height=self.size)

    def updateExplosion(self, app):
        if self.isExploding:
            app.asteroidExplosionSound.play()
            self.explosionIndex += 1
            if self.explosionIndex >= len(self.explosionFrames):
                self.isExploding = False
                self.isDestroyed = True

    def moveTowardSpaceship(self, spaceship):
        dx = spaceship.x - self.x
        dy = spaceship.y - self.y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return
        dx /= distance
        dy /= distance
        self.x += dx * self.speed
        self.y += dy * self.speed

class PowerUp:
    def __init__(self, x, y, app):
        self.x = x
        self.y = y
        self.size = 50
        self.r = self.size / 2
        self.link = random_module.choice(app.powerUpList)

    def drawPowerUp(self):
        drawImage(self.link, self.x, self.y, width=self.size, height=self.size)
    def apply(self, app):
        pass
  
class HealthPowerUp(PowerUp):
    def __init__(self, x, y, app):
        super().__init__(x, y, app)
        self.link = app.healthPowerUp  
    def apply(self, app, spaceShip):
        spaceShip.health += 30
        if spaceShip.health > 100:
            spaceShip.health = 100
        app.powerUps.remove(self)

class BulletPowerUp(PowerUp):
    def __init__(self, x, y, app):
        super().__init__(x, y, app)
        self.link = app.bulletPowerUp 
    def apply(self, app, spaceShip):
        spaceShip.numberOfBullets += 1
        app.powerUps.remove(self)


class ShipSpeedPowerUp(PowerUp):
    def __init__(self, x, y, app):
        super().__init__(x, y, app)
        self.link = app.shipSpeedPowerUp 
    def apply(self, app, spaceShip):
        spaceShip.velocity += 1
        app.powerUps.remove(self)

class SpecialAttackPowerUp(PowerUp):
    def __init__(self, x, y, app):
        super().__init__(x, y, app)
        self.link = app.specialAttackPowerUp  
    def apply(self, app, spaceShip):
        spaceShip.specialAttacks += 1
        if spaceShip.specialAttacks >= 100:
            spaceShip.specialAttacks = 50
        app.powerUps.remove(self)


# === Collision Detection ===
def distance(x1, y1, x2, y2):
    return (((x2- x1)**2 + (y2- y1)**2)**0.5)

def checkCollsion(object1X, object1Y, object1Radius, 
                  object2X, object2Y, object2Radius):
    
    d = distance(object1X, object1Y, object2X, object2Y)
    return d < object1Radius + object2Radius


def redrawAll(app):
    #draw background
    if app.screen != "GameBoard":
        drawImage(app.backgroundUrl, 0, 0, 
                  width=app.width, height=app.height)

    #draw Start Screen
    if app.screen == "Start":
        drawStart(app)
            
    #draw Connecting Screen
    if app.screen == "Connecting": 
        drawConnecting(app)

    #for Gameboard Screen
    if app.screen == "GameBoard":
        drawGameboard(app)
    
    #for Winning Screen
    if app.screen == "Winning":
        drawWinning(app)

    if app.screen == "Game":
        drawGame(app)
       
def drawStart(app):
    app.instructionsButton.drawButton()
    if not app.instructions:
        app.startButton.drawButton()
        drawLabel("GYRO SHOOTER", app.width//2, 4*app.height//8, 
                align = "center", fill = "orange", 
                border = "white", size = 50, font = "Orbitron", 
                bold = True, borderWidth = 3)
    else: 
        drawLabel("Instructions", app.width//2, 2* app.height//8, 
                align = "center", fill = "orange", 
                border = "white", size = 50, font = "Orbitron", 
                bold = True, borderWidth = 3)
        drawLabel("On Next Page, Swipe Phone to the Left",
                    app.width // 2, 3*app.height // 8, size = 30, bold=True, 
                    fill = "orange")
        drawLabel("to choose different characters", app.width // 2, 
                    4*app.height // 8, size = 30, bold=True, fill = "orange")
        drawLabel("and Player 1 rotate phone towards yourself", 
                    app.width // 2,  5*app.height // 8, size = 30, 
                    bold=True, fill = "orange")
        drawLabel("TO BEGIN!", app.width // 2,
                    6*app.height // 8, size = 30, bold=True, 
                    fill = "orange")
            
def drawConnecting(app):
    #Spaceship Drawn Based on Chosen Index
    drawImage(app.spaceShipOptions[app.chosenShipIndex1], app.width//4, 
                app.height//2, width=app.width//3, height = app.height//2, 
                align="center")
    drawImage(app.spaceShipOptions[app.chosenShipIndex2], 3*app.width//4, 
                app.height//2, width=app.width//3, height = app.height//2, 
                align="center")
    
    drawLabel("PLAYER 1", app.width//4, app.height//4, 
                size = 50, fill = "orange", border = "white",
                font = "Orbitron")
    drawLabel("PLAYER 2", 3*app.width//4, app.height//4, 
                size = 50, fill = "orange", border = "white",
                font = "Orbitron")
    
    #Shows if Each Player is Connected
    if playerConnected["p1"] == True:
        label1 = "Connected"
        color1 = "green"
    else: 
        label1 = "Not Connected"
        color1 = "red"
    drawLabel(label1, app.width//4, 7*app.height//10, 
                fill = color1, size = 40)
    
    if playerConnected["p2"] == True:
        label2 = "Connected"
        color2 = "green"
    else: 
        label2 = "Not Connected"
        color2 = "red"
    drawLabel(label2, 3*app.width//4, 7*app.height//10,
                fill = color2, size = 40)

def drawWinning(app):
    winner = "PLAYER 1" if app.p1Wins == 3 else "PLAYER 2"
    drawLabel(f'{winner} WINS!!!', app.width//2, app.height//2, size = 80,
            fill = "orange", border = "white")
    drawLabel("Rotate Towards Yourself to Restart!", app.width//2, 
            6*app.height//10, size = 30, fill = "orange") 
    
def drawGameboard(app):
    drawImage(app.raceTrack, 0, 0, width=app.width, height=app.height)
    drawImage(app.spaceShipOptions[app.chosenShipIndex1], app.p1Position, 
                3*app.height//8, width=app.width//6, height = app.height//3, 
                align="center", rotateAngle = 90)
    drawImage(app.spaceShipOptions[app.chosenShipIndex2], app.p2Position, 
                5*app.height//8, width=app.width//6, height = app.height//3, 
                align="center", rotateAngle = 90)
    
def drawGame(app):
    if app.paused:
        drawRect(0, 0, app.width, app.height, fill='white', opacity=30)
        drawLabel("Instructions: Rotate to Move Player",
                    app.width // 2, 2*app.height // 8, size = 30, bold=True)
        drawLabel("Press Buttons to Shoot",
                    app.width // 2, 3*app.height // 8, size = 30, bold=True)
        drawLabel("First to 3 wins, WINS!", app.width // 2, 
                    4*app.height // 8, size = 30, bold=True)
        drawLabel("GAME PAUSED", app.width // 2, 5*app.height // 8, 
                    size = 30, bold=True)
        drawLabel("Pause/Unpause by Rotating Towards Yourself", 
                    app.width // 2, 6*app.height // 8, size = 30, bold=True)
    else:
        #SpaceShip
        for spaceShip in app.spaceShipList:
            spaceShip.drawSpaceShip()

        #Asteroids
        for asteroid in app.asteroids:
            asteroid.drawAsteroid()

        for bullet in app.bullets:
            bullet.drawBullet(app)

        #PowerUps
        for powerUp in app.powerUps:
            powerUp.drawPowerUp()
        #beam
        for beam in app.beams:
            beam.drawBeam()

def onStep(app):
    #Changing Characters for Connecting Screen Based on Rotation
    if app.screen == "Connecting":
        app.movementDelay -=1
        if playerRotation["p1"] > 6 and app.movementDelay < 0:
            options = len(app.spaceShipOptions)
            app.chosenShipIndex1 = (app.chosenShipIndex1 + 1) % options
            app.spaceShip1.index = app.chosenShipIndex1
            app.spaceShip1.link = app.spaceShipOptions[app.spaceShip1.index]
            app.movementDelay = 10
        
        if playerRotation["p2"] > 6  and app.movementDelay == 0:
            options = len(app.spaceShipOptions)
            app.chosenShipIndex2 = (app.chosenShipIndex2 + 1) % options
            app.spaceShip2.index = app.chosenShipIndex2
            app.spaceShip2.link = app.spaceShipOptions[app.spaceShip2.index]
            app.movementDelay = 10
        
        #Starting Game Based on Rotation
        if playerStart["p1"] > 10:
            app.screen = "Game"
    
    #Gameboard Player that Wins Moves Logic
    if app.screen == "GameBoard":
        gameBoard(app)
            
    #Reset App
    if app.screen == "Winning":
        if playerStart["p1"] > 10:
            reset(app)
    
    #GamePlay
    if app.screen == "Game":
        gamePlay(app)
        move(app)
        moveAsteroids(app)
        spawn(app)
        collsion(app)
        beam(app)

def gameBoard(app):
    app.showingWinsDelay -=1
    if app.showingWinsDelay == 0:
        app.showingWinsDelay = 100
        app.screen = "Game"
        resetGame(app)

    if app.p1FinalPosition >= app.p1Position:
        app.p1Position +=10
    if app.p2FinalPosition >= app.p2Position:
        app.p2Position +=10
    
    if ((app.p1Position >= app.p1FinalPosition) and
        (app.p2Position >= app.p2FinalPosition) and
        (app.p1Wins == 3 or app.p2Wins == 3) and 
        (app.showingWinsDelay == 100)): 
        app.screen = "Winning"


def gamePlay(app):
    app.movementDelay -=1
    if playerStart["p1"] > 6 and app.movementDelay <= 0:
        app.paused = not app.paused
        app.movementDelay = 10

    if not app.paused and app.winAdded == False:
        for i in range(len(app.spaceShipList)):
            spaceShip = app.spaceShipList[i]
            if spaceShip.health < 0:
                app.winAdded = True
                if i == 1: 
                    app.p1Wins += 1
                    finalPosAdjust = ((app.width - 200) // 3)
                    app.p1FinalPosition = finalPosAdjust * app.p1Wins + 100
                    app.screen = "GameBoard" 
                    
                if i == 0:
                    app.p2Wins += 1
                    finalPosAdjust = ((app.width - 200) // 3)
                    app.p2FinalPosition = finalPosAdjust * app.p2Wins + 100  
                    app.screen = "GameBoard"

        # Update explosions and score
        for asteroid in app.asteroids:
            asteroid.updateExplosion(app)
            if asteroid.isDestroyed:
                app.asteroids.remove(asteroid)
                app.asteroidsDestroyed += 1  

def moveAsteroids(app):
    # Move asteroids and detect collisions with ship
    for asteroid in app.asteroids:
        arbritraryLargeValue = 10000000
        smallestDistance = arbritraryLargeValue
        closestShip = None
        for spaceShip in app.spaceShipList:
            d = distance(asteroid.x, asteroid.y, 
                            spaceShip.x, spaceShip.y)
            if d < smallestDistance:
                smallestDistance = d
                closestShip = spaceShip
        if closestShip is not None:
            asteroid.moveTowardSpaceship(closestShip) 

        if checkCollsion(asteroid.x, asteroid.y, asteroid.r, 
                            closestShip.x, closestShip.y, closestShip.r):
            closestShip.health -= 2
            app.asteroids.remove(asteroid)
        if ((asteroid.x > app.width) or (asteroid.x < 0) or 
            (asteroid.y > app.height) or (asteroid.y < 0)):
            app.asteroids.remove(asteroid) 

def move(app):
    #Moving the Spaceships and Shoot Bullets
    for spaceShip in app.spaceShipList:
        spaceShip.moveSpaceShip(app)
        currentShootButtonState = shootButtonPressedDict[spaceShip.id]

        if currentShootButtonState:
            spaceShip.shoot(app)
        if spaceShip.fireCooldown > 0:
            spaceShip.fireCooldown -= 1

        currentSpecState = specialAttackButtonPressedDict[spaceShip.id]
        if currentSpecState:
            spaceShip.shootSpecial(app)
        if spaceShip.fireCooldown > 0:
            spaceShip.fireCooldown -= 1

    # Move bullets and detect collisions
    for bullet in app.bullets:
        bullet.move()
        for asteroid in app.asteroids:
            if checkCollsion(bullet.x, bullet.y, bullet.r, asteroid.x, 
                                asteroid.y, asteroid.r):
                asteroid.isExploding = True
                if app.bullets != []:
                    app.bullets.remove(bullet)
                    break
        if ((bullet.x > app.width) or (bullet.x < 0) or 
        (bullet.y > app.height) or (bullet.y < 0)):
            if app.bullets != []:
                app.bullets.remove(bullet)   

           
def spawn(app):          
    # Spawn next wave if clear
    if  app.asteroids == []:
        for _ in range(app.level // 2):
            if app.level <= 50:
                asteroidX = random_module.randint(0, app.width)
                asteroidY = random_module.randint(0, app.height)
                asteroidR = random_module.randint(50, 150)
                distanceToShip = distance(app.spaceShip1.x, 
                                            app.spaceShip1.y, 
                                            asteroidX, asteroidY)
                minDistanceToShip = 50
                if distanceToShip > minDistanceToShip:
                    app.asteroids.append(Asteroid(asteroidX, 
                                                    asteroidY,
                                                    asteroidR, 
                                                    app))
        app.level += 1


     #Check Powerup Collision
    for powerUp in app.powerUps:
        for spaceShip in app.spaceShipList:
            if checkCollsion(powerUp.x, powerUp.y, 
                                powerUp.r, spaceShip.x, 
                            spaceShip.y, spaceShip.r):
                powerUp.apply(app, spaceShip)
                app.powerUpSound.play()
                break

def collsion(app): 
    #Random powerUp Spawn
    if app.asteroidsDestroyed % 2 == 0:
        powerUpX = random_module.randint(0, app.width)
        powerUpY = random_module.randint(0, app.height)
        powerUpType = random_module.choice([HealthPowerUp, 
                                            BulletPowerUp, 
                                            ShipSpeedPowerUp, 
                                            SpecialAttackPowerUp])
        app.powerUps.append(powerUpType(powerUpX, powerUpY, app))
        app.asteroidsDestroyed += 1
    #Check SpaceShip1 and SpaceShip2 Collisions
    for bullet in app.bullets:
        for spaceShip in app.spaceShipList:
            if checkCollsion(bullet.x, bullet.y, bullet.r, 
                                spaceShip.x, spaceShip.y, 
                                spaceShip.r):
                if bullet.id != spaceShip.id:
                    spaceShip.health -=2
                    app.bulletHitSound.play()
                    if app.bullets != []:
                        app.bullets.remove(bullet)

    
def beam(app):
    #Beam and asteroids collision
    for beam in app.beams:
        beam.update()
        app.beamSound.play()
        if not beam.active:
            app.beams.remove(beam)
        else:
            for asteroid in app.asteroids:
                if checkCollsion(beam.x, beam.y, 100, 
                                    asteroid.x, asteroid.y, asteroid.r):
                    asteroid.isExploding = True

    #Beam and ships collision
    for beam in app.beams:
        beam.update()
        if not beam.active:
            app.beams.remove(beam)
        else:
            for spaceShip in app.spaceShipList:
                if checkCollsion(beam.x, beam.y, 100, 
                                    spaceShip.x, spaceShip.y, spaceShip.r):
                    spaceShip.health -= .8


def onMousePress(app, mouseX, mouseY):
    #Start Button
    if app.screen == "Start":
        if app.startButton.isClicked(mouseX, mouseY):
            app.screen = "Connecting"
        if app.instructionsButton.isClicked(mouseX, mouseY):
            app.instructions = not app.instructions

def main():
    runApp(width=800, height=800)
main()

