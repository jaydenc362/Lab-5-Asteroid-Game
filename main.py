import pygame
import random
import math
import asyncio

async def main():
    # Pygame Setup
    pygame.init()
    WIDTH = 640
    HEIGHT = 360
    screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync = 1)
    pygame.display.set_caption("Jayden Chan Period 5: Crazy Asteroids")
    clock = pygame.time.Clock()
    running = True
    dt = 0

    # Game Setup
    numberAsteroids = 9

    class Player:
        def __init__(self):
            self.position = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
            self.velocity = pygame.Vector2(0, 0)
            self.acceleration = 5
            self.drag = 0.95
            self.maxVelocity = 5
            self.rotationSpeed = 3.5
            self.angle = math.pi / 2
            self.direction = pygame.Vector2(math.cos(self.angle), math.sin(self.angle))
            self.radius = 20
        def fireMissile(self):
            normalDirection = self.direction.normalize()
            missile = Missile(self.position, normalDirection)
        def update(self):
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_w] or keys[pygame.K_UP]) and not (keys[pygame.K_s] or keys[pygame.K_DOWN]):
                self.velocity -= self.direction * self.acceleration * dt
            elif (keys[pygame.K_s] or keys[pygame.K_DOWN]) and not (keys[pygame.K_w] or keys[pygame.K_UP]):
                self.velocity += self.direction * self.acceleration * dt
            else:
                self.velocity *= self.drag
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and not (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
                self.angle -= self.rotationSpeed * dt
                self.direction = pygame.Vector2(math.cos(self.angle), math.sin(self.angle))            
            elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and not (keys[pygame.K_a] or keys[pygame.K_LEFT]):
                self.angle += self.rotationSpeed * dt
                self.direction = pygame.Vector2(math.cos(self.angle), math.sin(self.angle))
            if self.velocity.length() > self.maxVelocity:
                self.velocity.scale_to_length(self.maxVelocity)
            self.position += self.velocity
            self.wrapAroundWall()
        def wrapAroundWall(self):
            if self.position.x < -self.radius:
                self.position.x = self.radius + WIDTH
            elif self.position.x > self.radius + WIDTH:
                self.position.x = -self.radius
            if self.position.y < -self.radius:
                self.position.y = self.radius + HEIGHT
            elif self.position.y > self.radius + HEIGHT:
                self.position.y = -self.radius
        def draw(self):
            forward = -self.direction.copy()
            left = forward.rotate(140)
            right = forward.rotate(-140)
            p1 = self.position + forward * 22
            p2 = self.position + left * 16
            p3 = self.position + right * 16
            pygame.draw.polygon(screen, "brown2", [p1, p2, p3])

    class Enemy:
        def __init__(self):
            self.DETECTION_RANGE = 130
            self.FOV_THRESHOLD = 0.7
            self.radius = 30
            self.position = pygame.Vector2(WIDTH / 4, HEIGHT / 2)
            self.enemy_angle = 0
            self.enemy_forward = pygame.Vector2(1, 0)
            self.detected = False
            self.cooldownTime = 0.2
            self.cooldownTracker = 0
            self.velocity = pygame.Vector2(
                random.uniform(-50, 50),
                random.uniform(-50, 50))
        def fireMissile(self):
            direction = self.position - player.position
            normalDirection = direction.normalize()
            enemyMissile = EnemyMissile(self.position, normalDirection)
        def wrapAroundWall(self):
            if self.position.x < -self.radius:
                self.position.x = self.radius + WIDTH
            elif self.position.x > self.radius + WIDTH:
                self.position.x = -self.radius
            if self.position.y < -self.radius:
                self.position.y = self.radius + HEIGHT
            elif self.position.y > self.radius + HEIGHT:
                self.position.y = -self.radius
        def update(self, player):
            # Detecting and turning
            radians = math.radians(self.enemy_angle)
            self.enemy_forward = pygame.Vector2(math.cos(radians), -math.sin(radians))
            to_player = (player.position - self.position)
            if to_player.length() > 0:
                to_player = to_player.normalize()
            distance = self.position.distance_to(player.position)
            dot = self.enemy_forward.dot(to_player)
            if self.cooldownTracker > 0:
                self.cooldownTracker -= dt
            if (distance < self.DETECTION_RANGE and dot > self.FOV_THRESHOLD):
                self.detected = True
                self.enemy_angle = math.degrees(math.atan2(-to_player.y, to_player.x))
                if self.cooldownTracker <= 0:
                    self.fireMissile()
                    self.cooldownTracker = self.cooldownTime
            else:
                self.detected = False
            # Movement
            self.position += self.velocity * dt
            self.wrapAroundWall()
        def draw(self):
            enemy_color = "red" if self.detected else "white"
            pygame.draw.circle(
                screen, enemy_color,
                self.position, self.radius)
            pygame.draw.circle(
                screen, "gray",
                self.position,
                self.DETECTION_RANGE, 1)
            pygame.draw.line(
                screen, "red", self.position,
                self.position + self.enemy_forward * 50, 3)

    class Missile:
        allMissiles = []
        def __init__(self, playerPosition, normalDirection):
            self.speed = 300
            self.radius = 7.5
            self.position = playerPosition.copy()
            self.velocity = normalDirection * self.speed
            Missile.allMissiles.append(self)
        def outsideScreen(self):
            return (
                self.position.x < -self.radius
                or self.position.x > WIDTH + self.radius
                or self.position.y < -self.radius
                or self.position.y > HEIGHT + self.radius)
        def collideWithAsteroid(self, asteroid):
            distance = self.position.distance_to(asteroid.position)
            return distance < self.radius + asteroid.radius
        def update(self):
            self.position -= self.velocity * dt
            if self.outsideScreen():
                Missile.allMissiles.remove(self)
        def draw(self):
            pygame.draw.circle(screen, "dodgerblue4", self.position, self.radius)

    class EnemyMissile:
        allEnemyMissiles = []
        def __init__(self, enemyPosition, normalDirection):
            self.speed = 250
            self.radius = 7
            self.position = enemyPosition.copy()
            self.velocity = normalDirection * self.speed
            EnemyMissile.allEnemyMissiles.append(self)
        def outsideScreen(self):
            return (
                self.position.x < -self.radius
                or self.position.x > WIDTH + self.radius
                or self.position.y < -self.radius
                or self.position.y > HEIGHT + self.radius
            )
        def collideWithAsteroid(self, asteroid):
            distance = self.position.distance_to(asteroid.position)
            return distance < self.radius + asteroid.radius
        def update(self):
            self.position -= self.velocity * dt
            if self.outsideScreen():
                EnemyMissile.allEnemyMissiles.remove(self)
        def draw(self):
            pygame.draw.circle(screen, "green", self.position, self.radius)

    class Asteroid:
        def __init__(self):
            self.position = pygame.Vector2(
                random.uniform(0, WIDTH),
                random.uniform(0, HEIGHT)
            )
            self.velocity = pygame.Vector2(
                random.uniform(-100, 100),
                random.uniform(-100, 100)
            )
            self.radius = random.uniform(10, 50)
            self.mass = self.radius ** 2
            self.elasticity = 0.5
            self.colorValue = random.randint(50, 200)
            self.font = pygame.font.Font(None, round(self.radius) * 2)
        def wrapAroundWall(self):
            if self.position.x < -self.radius:
                self.position.x = self.radius + WIDTH
            elif self.position.x > self.radius + WIDTH:
                self.position.x = -self.radius
            if self.position.y < -self.radius:
                self.position.y = self.radius + HEIGHT
            elif self.position.y > self.radius + HEIGHT:
                self.position.y = -self.radius
        def collideWithAsteroid(self, other):
            offset = other.position - self.position
            # Account for screen wrapping
            if offset.x > WIDTH / 2:
                offset.x -= WIDTH
            elif offset.x < -WIDTH / 2:
                offset.x += WIDTH
            if offset.y > HEIGHT / 2:
                offset.y -= HEIGHT
            elif offset.y < -HEIGHT / 2:
                offset.y += HEIGHT
            distance = offset.length()
            minimumDistance = self.radius + other.radius
            if distance >= minimumDistance: return
            if distance == 0:
                normal = pygame.Vector2(1, 0)
            else:
                normal = offset / distance
            # Relative velocity
            relativeVelocity = other.velocity - self.velocity
            velocityAlongNormal = relativeVelocity.dot(normal)
            # Already moving apart
            if velocityAlongNormal >= 0: return
            # Separate overlapping asteroids
            overlap = minimumDistance - distance
            totalMass = self.mass + other.mass
            self.position -= normal * overlap * (other.mass / totalMass)
            other.position += normal * overlap * (self.mass / totalMass)
            # Elastic collision
            elasticity = min(self.elasticity, other.elasticity)
            impulseMagnitude = (
                -(1 + elasticity) * velocityAlongNormal
                / (1 / self.mass + 1 / other.mass))
            impulse = normal * impulseMagnitude
            self.velocity -= impulse / self.mass
            other.velocity += impulse / other.mass
        def collideWithMissile(self, allAsteroids, missile):
            Missile.allMissiles.remove(missile)
            allAsteroids.remove(self)
        def update(self, dt):
            self.position += self.velocity * dt
            self.wrapAroundWall()
        def draw(self, screen, tag):
            pygame.draw.circle(
                screen,
                (self.colorValue, self.colorValue, self.colorValue),
                self.position,
                self.radius)
            textSurface = self.font.render(tag, True, "white")
            textRect = textSurface.get_rect(center = self.position)
            screen.blit(textSurface, textRect)

    # Player
    player = Player()
    enemy = Enemy()

    # Astroids
    allAsteroids = []
    for i in range(numberAsteroids):
        allAsteroids.append(Asteroid())

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                player.fireMissile()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.fireMissile()

        # FPS
        dt = min(clock.tick(60) / 1000, 0.06)

        # Background
        screen.fill("black")

        # Update Player
        player.update()

        # Update Enemy
        enemy.update(player)

        # Update Missiles
        for missile in Missile.allMissiles[:]:
            missile.update()
        for missile in Missile.allMissiles[:]:
            for asteroid in allAsteroids[:]:
                if missile.collideWithAsteroid(asteroid):
                    Missile.allMissiles.remove(missile) # Destroy Asteroid
                    allAsteroids.remove(asteroid) # Destroy Asteroid
                    allAsteroids.append(Asteroid()) # New Asteroid
                    break
        for enemyMissile in EnemyMissile.allEnemyMissiles[:]:
            enemyMissile.update()
        for enemyMissile in EnemyMissile.allEnemyMissiles[:]:
            for asteroid in allAsteroids[:]:
                if enemyMissile.collideWithAsteroid(asteroid):
                    EnemyMissile.allEnemyMissiles.remove(enemyMissile) # Destroy Asteroid
                    allAsteroids.remove(asteroid) # Destroy Asteroid
                    allAsteroids.append(Asteroid()) # New Asteroid
                    break

        # Update Asteroids
        for i in range(len(allAsteroids)):
            for j in range(i + 1, len(allAsteroids)):
                allAsteroids[i].collideWithAsteroid(allAsteroids[j])
        for asteroid in allAsteroids:
            asteroid.update(dt)
    
        # Draw Missiles
        for missile in Missile.allMissiles:
            missile.draw()
        for enemyMissile in EnemyMissile.allEnemyMissiles:
            enemyMissile.draw()

        # Draw Player
        player.draw()

        # Draw Enemy
        enemy.draw()

        # Draw Asteroids
        tag = 0
        for asteroid in allAsteroids:
            asteroid.draw(screen, str(tag))
            tag += 1

        # Display
        pygame.display.flip()
        await asyncio.sleep(0)

asyncio.run(main())