from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# ── Window size ──────────────────────────────────────────────
W, H = 500, 500

# ── Paddle ───────────────────────────────────────────────────
paddle_x   = 0.0
paddle_y   = -0.85
paddle_w   = 0.30
paddle_h   = 0.04
paddle_spd = 0.06

# ── Ball ─────────────────────────────────────────────────────
ball_x  = 0.0
ball_y  = -0.70
ball_r  = 0.035
ball_dx = 0.008
ball_dy = 0.010

# ── Game state ───────────────────────────────────────────────
score    = 0
lives    = 3
running  = True
won      = False
launched = False   # ball waits until Space is pressed

# ── Bricks ───────────────────────────────────────────────────
ROWS, COLS = 5, 7
brick_w = 0.24
brick_h = 0.07
gap     = 0.02

row_colors = [
    (0.95, 0.55, 0.55),
    (0.95, 0.75, 0.45),
    (0.65, 0.88, 0.60),
    (0.50, 0.78, 0.95),
    (0.80, 0.65, 0.95),
]

def make_bricks():
    bricks = []
    start_x = -(0.5 * COLS * (brick_w + gap) - gap / 2)
    start_y = 0.30
    for r in range(ROWS):
        for c in range(COLS):
            cx = start_x + c * (brick_w + gap) + brick_w / 2
            cy = start_y - r * (brick_h + gap)
            bricks.append([cx, cy, True])
    return bricks

bricks = make_bricks()

# ── Draw helpers ─────────────────────────────────────────────
def draw_rect(cx, cy, w, h, color):
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(cx - w/2, cy - h/2)
    glVertex2f(cx + w/2, cy - h/2)
    glVertex2f(cx + w/2, cy + h/2)
    glVertex2f(cx - w/2, cy + h/2)
    glEnd()

def draw_circle(cx, cy, r, color, segs=40):
    glColor3f(*color)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for i in range(segs + 1):
        angle = 2.0 * math.pi * i / segs
        glVertex2f(cx + r * math.cos(angle), cy + r * math.sin(angle))
    glEnd()

def draw_text(x, y, text):
    glColor3f(0.3, 0.3, 0.3)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

# ── Reset ball to sit on paddle ───────────────────────────────
def reset_ball():
    global ball_x, ball_y, ball_dx, ball_dy, launched
    ball_x   = paddle_x
    ball_y   = paddle_y + paddle_h / 2 + ball_r + 0.005
    ball_dx  = 0.008
    ball_dy  = 0.010
    launched = False

# ── Main draw ────────────────────────────────────────────────
def main():
    for i, (bx, by, alive) in enumerate(bricks):
        if alive:
            row = i // COLS
            draw_rect(bx, by, brick_w - 0.01, brick_h - 0.01, row_colors[row])

    draw_rect(paddle_x, paddle_y, paddle_w, paddle_h, (0.35, 0.55, 0.90))
    draw_circle(ball_x, ball_y, ball_r, (0.20, 0.20, 0.80))

    draw_text(-0.98, 0.91, f"Score: {score}")
    draw_text( 0.55, 0.91, f"Lives: {lives}")

    if not running:
        msg = "YOU WIN!  Press R" if won else "GAME OVER  Press R"
        draw_text(-0.28, 0.0, msg)
    elif not launched:
        draw_text(-0.38, -0.60, "Press SPACE to launch")

# ── Physics update ───────────────────────────────────────────
def update(value):
    global ball_x, ball_y, ball_dx, ball_dy
    global score, lives, running, won

    if not running or not launched:
        # Ball sits on top of paddle when not launched
        if not launched and running:
            ball_x = paddle_x
            ball_y = paddle_y + paddle_h / 2 + ball_r + 0.005
        glutPostRedisplay()
        glutTimerFunc(16, update, 0)
        return

    ball_x += ball_dx
    ball_y += ball_dy

    # Wall bounces
    if ball_x + ball_r >= 1.0 or ball_x - ball_r <= -1.0:
        ball_dx = -ball_dx
    if ball_y + ball_r >= 1.0:
        ball_dy = -ball_dy

    # Paddle collision
    if (paddle_y - paddle_h/2 <= ball_y - ball_r <= paddle_y + paddle_h/2
            and paddle_x - paddle_w/2 <= ball_x <= paddle_x + paddle_w/2):
        ball_dy = abs(ball_dy)
        offset = (ball_x - paddle_x) / (paddle_w / 2)
        ball_dx = offset * 0.020

    # Ball falls off bottom
    if ball_y - ball_r < -1.05:
        lives -= 1
        if lives <= 0:
            running = False
            won = False
        else:
            reset_ball()

    # Brick collision
    for i, (bx, by, alive) in enumerate(bricks):
        if not alive:
            continue
        hw, hh = brick_w / 2, brick_h / 2
        if (bx - hw <= ball_x <= bx + hw and
                by - hh - ball_r <= ball_y <= by + hh + ball_r):
            bricks[i][2] = False
            ball_dy = -ball_dy
            score += 10
            break

    # Win check
    if all(not b[2] for b in bricks):
        running = False
        won = True

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

# ── Input handlers ───────────────────────────────────────────
def arrowkey(key, a, b):
    global paddle_x
    if key == GLUT_KEY_LEFT:
        paddle_x = max(-1.0 + paddle_w/2, paddle_x - paddle_spd)
    elif key == GLUT_KEY_RIGHT:
        paddle_x = min(1.0  - paddle_w/2, paddle_x + paddle_spd)
    glutPostRedisplay()

def normalkey(key, x, y):
    global bricks, ball_x, ball_y, ball_dx, ball_dy
    global score, lives, running, won, paddle_x, launched

    if key == b' ' and running and not launched:
        launched = True

    elif key == b'r' or key == b'R':
        bricks = make_bricks()
        paddle_x = 0.0
        score, lives = 0, 3
        running = True
        won = False
        reset_ball()

    elif key == b'\x1b':
        glutLeaveMainLoop()

    glutPostRedisplay()

def mouse(button, state, x, y):
    global paddle_x
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        paddle_x = (x / 250.0) - 1.0
        paddle_x = max(-1.0 + paddle_w/2, min(1.0 - paddle_w/2, paddle_x))
    glutPostRedisplay()

# ── Display callback ─────────────────────────────────────────
def showScreen():
    glClearColor(0.96, 0.96, 0.98, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    main()
    glFlush()

# ── GLUT setup ───────────────────────────────────────────────
glutInit()
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
glutInitWindowSize(W, H)
glutInitWindowPosition(20, 200)
glutCreateWindow(b"Brick Breaker")
glutDisplayFunc(showScreen)
glutSpecialFunc(arrowkey)
glutKeyboardFunc(normalkey)
glutMouseFunc(mouse)
glutTimerFunc(16, update, 0)
glutMainLoop()
