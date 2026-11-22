import pygame
import random
import sys

pygame.init()

#Настройки экрана
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("FNaF 3")
clock = pygame.time.Clock()

#Цвета
BLACK = (5, 5, 8)
GREEN = (40, 230, 80)
DARK_GREEN = (15, 70, 25)
RED = (230, 40, 40)
YELLOW = (240, 200, 40)
WHITE = (230, 230, 230)
GREY = (70, 75, 70)
DARK_GREY = (25, 28, 25)

#Шрифты
font_sm = pygame.font.SysFont("Consolas", 16, bold=True)
font_md = pygame.font.SysFont("Consolas", 22, bold=True)
font_lg = pygame.font.SysFont("Consolas", 48, bold=True)


def reset_game():
    return {
        #Позиции Спрингтрапа:
        #Обычные камеры: 1 (дальняя), 2 (коридор), 3 (у окна офиса), 4 (дверь офиса)
        #Вентиляция: "V1" (вход), "V2" (середина), "V3" (выход в офис)
        "in_menu": True,  #Игра начинается с главного меню
        "springtrap_pos": 1,
        "in_vent": False,
        "sealed_vent": None,  #Какая вентиляция заблокирована: 1 или 2

        #Интерфейс и экраны: "OFFICE", "CAMERAS", "MAINTENANCE"
        "view": "OFFICE",
        "cam_mode": "FLOOR",  #"FLOOR" или "VENT"
        "current_cam": 1,
        "current_vent": 1,

        #Состояние систем
        "audio_broken": False,
        "cam_broken": False,
        "vent_broken": False,
        "audio_uses": 0,
        "rebooting": None,  #Какая система сейчас чинится ("AUDIO", "CAM", "VENT", "ALL")
        "reboot_timer": 0.0,

        #Таймеры
        "time_elapsed": 0.0,
        "night_duration": 180.0,  # 180 секунд = 6 часов
        "ai_timer": 0.0,
        "ai_interval": 5.5,
        "stun_timer": 2.0,
        "audio_cooldown": 0.0,
        "cam_glitch_timer": 18.0,
        "vent_glitch_timer": 28.0,

        #Финал и скример
        "game_over": False,
        "victory": False,
        "jumpscare_timer": 0.0,
    }


state = reset_game()

def draw_scanlines_and_static(intensity=25):
    """Эффект старого монитора и помех"""
    for _ in range(intensity):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        w = random.randint(10, 90)
        color = random.choice([(40, 40, 40), (90, 90, 90), (20, 50, 20)])
        pygame.draw.line(screen, color, (x, y), (x + w, y), 1)
    for y in range(0, HEIGHT, 4):
        pygame.draw.line(screen, (0, 0, 0), (0, y), (WIDTH, y), 1)


def draw_springtrap_silhouette(cx, cy, scale=1.0, angry=False):
    """Рисуем узнаваемый силуэт Спрингтрапа с заячьими ушами (на время)"""
    color = RED if angry else (110, 130, 60)
    eye_color = WHITE if angry else YELLOW

    #Голова
    pygame.draw.ellipse(screen, color, (cx - 30 * scale, cy - 35 * scale, 60 * scale, 70 * scale))
    #Левое ухо
    pygame.draw.rect(screen, color, (cx - 22 * scale, cy - 85 * scale, 14 * scale, 52 * scale), border_radius=4)
    #Правое ухо (надломленное, как в игре)
    pygame.draw.rect(screen, color, (cx + 8 * scale, cy - 75 * scale, 14 * scale, 42 * scale), border_radius=4)
    pygame.draw.rect(screen, color, (cx + 12 * scale, cy - 90 * scale, 14 * scale, 20 * scale), border_radius=3)
    #Светящиеся глаза
    pygame.draw.circle(screen, eye_color, (int(cx - 12 * scale), int(cy - 8 * scale)), int(6 * scale))
    pygame.draw.circle(screen, eye_color, (int(cx + 12 * scale), int(cy - 8 * scale)), int(6 * scale))
    #Зубы / оскал
    pygame.draw.rect(screen, BLACK, (cx - 16 * scale, cy + 10 * scale, 32 * scale, 12 * scale))


def get_hour_text(elapsed, total):
    hour = int((elapsed / total) * 6)
    return "12 AM" if hour == 0 else f"{hour} AM"


#Главный цикл
while True:
    dt = clock.tick(30) / 1000.0
    #НАЧАЛЬНЫЙ ЭКРАН (МЕНЮ)
    if state["in_menu"]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                #Кнопка "NEW GAME"
                if 80 <= mx <= 340 and 300 <= my <= 355:
                    state = reset_game()
                    state["in_menu"] = False
                #Кнопка "EXIT"
                elif 80 <= mx <= 340 and 380 <= my <= 435:
                    pygame.quit()
                    sys.exit()

        screen.fill(BLACK)

        #Заголовок в стиле FNaF 3
        screen.blit(font_lg.render("FIVE NIGHTS", True, WHITE), (80, 70))
        screen.blit(font_lg.render("AT FREDDY'S 3", True, GREEN), (80, 130))
        screen.blit(font_sm.render("FAZBEAR'S FRIGHT PROTOTYPE", True, GREY), (82, 195))

        #Кнопка "NEW GAME"
        pygame.draw.rect(screen, GREEN, (80, 300, 260, 55), 2)
        screen.blit(font_md.render(">> NEW GAME", True, GREEN), (105, 316))

        #Кнопка "EXIT"
        pygame.draw.rect(screen, RED, (80, 380, 260, 55), 2)
        screen.blit(font_md.render(">> EXIT", True, RED), (105, 396))

        #Спрингтрап справа на фоне (иногда дёргается, как в оригинале!)
        twitch_x = random.randint(-15, 15) if random.random() < 0.15 else 0
        twitch_y = random.randint(-10, 10) if random.random() < 0.15 else 0
        draw_springtrap_silhouette(650 + twitch_x, 350 + twitch_y, scale=2.4, angry=(twitch_x != 0))

        draw_scanlines_and_static(30)
        pygame.display.flip()
        continue  #Пока мы в меню, основной игровой код ниже не выполняется


    #Обновление логики
    if not state["game_over"] and not state["victory"]:
        state["time_elapsed"] += dt
        if state["time_elapsed"] >= state["night_duration"]:
            state["victory"] = True

        if state["audio_cooldown"] > 0:
            state["audio_cooldown"] -= dt

        #Случайная поломка камер со временем
        state["cam_glitch_timer"] -= dt
        if state["cam_glitch_timer"] <= 0:
            state["cam_broken"] = True
            state["cam_glitch_timer"] = random.uniform(22.0, 35.0)
        #Случайная поломка вентиляции со временем
        state["vent_glitch_timer"] -= dt
        if state["vent_glitch_timer"] <= 0:
            state["vent_broken"] = True
            state["vent_glitch_timer"] = random.uniform(25.0, 40.0)

        #Процесс починки систем
        if state["rebooting"]:
            state["reboot_timer"] -= dt
            if state["reboot_timer"] <= 0:
                target = state["rebooting"]
                if target in ("AUDIO", "ALL"):
                    state["audio_broken"] = False
                    state["audio_uses"] = 0
                if target in ("CAM", "ALL"):
                    state["cam_broken"] = False
                if target in ("VENT", "ALL"):
                    state["vent_broken"] = False
                state["rebooting"] = None

        #ИИ Спрингтрапа
        if state["stun_timer"] > 0:
            state["stun_timer"] -= dt
        else:
            state["ai_timer"] += dt
            if state["ai_timer"] >= state["ai_interval"]:
                state["ai_timer"] = 0

                if state["in_vent"]:
                    #Движение по вентиляции (1 -> 2 -> Офис)
                    if state["springtrap_pos"] == 1:
                        if state["sealed_vent"] == 1:
                            #Люк закрыт! Он разворачивается обратно в камеру 2
                            state["in_vent"] = False
                            state["springtrap_pos"] = 2
                        else:
                            state["springtrap_pos"] = 2
                    elif state["springtrap_pos"] == 2:
                        if state["sealed_vent"] == 2:
                            state["in_vent"] = False
                            state["springtrap_pos"] = 3
                        else:
                            state["game_over"] = True
                else:
                    #Движение по обычным камерам
                    roll = random.random()
                    #На камере 2 или 3 он может нырнуть в вентиляцию
                    if state["springtrap_pos"] in (2, 3) and roll < 0.28:
                        state["in_vent"] = True
                        state["springtrap_pos"] = 1 if state["springtrap_pos"] == 2 else 2
                    elif roll < 0.75:
                        if state["springtrap_pos"] < 4:
                            state["springtrap_pos"] += 1
                        else:
                            state["game_over"] = True
                    elif state["springtrap_pos"] > 1:
                        state["springtrap_pos"] -= 1

    #Обработка кликов и клавиш
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_r and (state["game_over"] or state["victory"]):
                state = reset_game()
                state["in_menu"] = False
            if event.key == pygame.K_m and (state["game_over"] or state["victory"]):
                state = reset_game()  # Вернёт в главное меню, так как in_menu=True

        if event.type == pygame.MOUSEBUTTONDOWN and not state["game_over"] and not state["victory"]:
            mx, my = pygame.mouse.get_pos()

            #Нижняя правая кнопка: Монитор камер
            if 520 <= mx <= 860 and 585 <= my <= 635:
                state["view"] = "OFFICE" if state["view"] == "CAMERAS" else "CAMERAS"

            #Нижняя левая кнопка: Панель починки (Maintenance)
            if 40 <= mx <= 360 and 585 <= my <= 635:
                state["view"] = "OFFICE" if state["view"] == "MAINTENANCE" else "MAINTENANCE"

            #Клики внутри ПАНЕЛИ ПОЧИНКИ
            if state["view"] == "MAINTENANCE" and not state["rebooting"]:
                if 120 <= mx <= 480:
                    if 170 <= my <= 215 and state["audio_broken"]:
                        state["rebooting"] = "AUDIO"
                        state["reboot_timer"] = 3.0
                    elif 230 <= my <= 275 and state["cam_broken"]:
                        state["rebooting"] = "CAM"
                        state["reboot_timer"] = 3.0
                    elif 290 <= my <= 335 and state["vent_broken"]:
                        state["rebooting"] = "VENT"
                        state["reboot_timer"] = 3.0
                    elif 370 <= my <= 420:
                        state["rebooting"] = "ALL"
                        state["reboot_timer"] = 5.0

            #Клики внутри МОНИТОРА КАМЕР
            if state["view"] == "CAMERAS":
                #Переключение Этаж / Вентиляция
                if 620 <= mx <= 830 and 95 <= my <= 135:
                    state["cam_mode"] = "VENT" if state["cam_mode"] == "FLOOR" else "FLOOR"

                if state["cam_mode"] == "FLOOR":
                    #Выбор камер CAM 01 - CAM 04
                    for i in range(1, 5):
                        bx = 620 + ((i - 1) % 2) * 110
                        by = 160 + ((i - 1) // 2) * 60
                        if bx <= mx <= bx + 95 and by <= my <= by + 45:
                            state["current_cam"] = i

                    #Кнопка PLAY AUDIO
                    if 620 <= mx <= 830 and 310 <= my <= 365:
                        if not state["audio_broken"] and state["audio_cooldown"] <= 0:
                            state["audio_uses"] += 1
                            state["audio_cooldown"] = 4.5
                            #После 3 использований аудио ломается
                            if state["audio_uses"] >= 3:
                                state["audio_broken"] = True

                            #Приманиваем, если он в обычной зоне и находится на той же или соседней камере
                            if not state["in_vent"] and abs(state["springtrap_pos"] - state["current_cam"]) <= 1:
                                if random.random() < 0.50:  #Шанс 50%, что он поведётся на звук
                                    if state["current_cam"] < state["springtrap_pos"]:
                                        #Звук дальше от офиса — уходит назад
                                        state["springtrap_pos"] -= 1
                                    elif state["current_cam"] > state["springtrap_pos"]:
                                        #Звук ближе к офису — подходит ближе!
                                        state["springtrap_pos"] += 1

                                    state["stun_timer"] = 4.5
                                    state["ai_timer"] = 0


                else:  #Режим VENT
                    for v in (1, 2):
                        bx = 620 + (v - 1) * 110
                        if bx <= mx <= bx + 95 and 160 <= my <= 205:
                            state["current_vent"] = v
                        #Кнопка Seal Vent (заблокировать вентиляцию)
                    if 620 <= mx <= 830 and 310 <= my <= 365:
                        if state["sealed_vent"] == state["current_vent"]:
                            state["sealed_vent"] = None
                        else:
                            state["sealed_vent"] = state["current_vent"]

    #ОТРИСОВКА
    screen.fill(BLACK)

    if state["game_over"]:
        #Анимация скримера
        shake_x = random.randint(-12, 12)
        shake_y = random.randint(-12, 12)
        draw_springtrap_silhouette(WIDTH // 2 + shake_x, HEIGHT // 2 + 20 + shake_y, scale=2.6,
                                   angry=True)
        txt = font_lg.render("GAME OVER", True, RED)
        sub = font_md.render("[R] - начать ночь заново  |  [M] - в главное меню", True, WHITE)
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 60))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT - 80))

    elif state["victory"]:
        txt = font_lg.render("6:00 AM", True, GREEN)
        sub = font_md.render("Вы пережили смену в Fazbear's Fright! [R] - начать ночь заново  |  [M] - в главное меню", True, WHITE)
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 40))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 30))

    else:
        # 1. ВИД ИЗ ОФИСА
        if state["view"] == "OFFICE":
            #Стены и большое стекло офиса
            pygame.draw.rect(screen, DARK_GREY, (40, 70, 820, 490))
            pygame.draw.rect(screen, (15, 22, 18), (180, 110, 440, 260))
            pygame.draw.rect(screen, GREY, (180, 110, 440, 260), 4)

            #Коробка с масками старых аниматроников (деталь из FNaF 3)
            pygame.draw.rect(screen, (65, 50, 35), (660, 340, 120, 110))
            screen.blit(font_sm.render("TOYS", True, BLACK), (695, 385))

            #Если Спрингтрап на CAM 03 — он смотрит прямо через стекло!
            if not state["in_vent"] and state["springtrap_pos"] == 3:
                draw_springtrap_silhouette(400, 260, scale=1.25, angry=True)
                warn = font_md.render("! ОН СМОТРИТ В ОКНО !", True, RED)
                screen.blit(warn, (275, 385))
            #Если он на CAM 04 — он стоит в дверном проёме слева!
            elif not state["in_vent"] and state["springtrap_pos"] == 4:
                draw_springtrap_silhouette(110, 310, scale=1.5, angry=True)
                warn = font_md.render("! ОН У ДВЕРИ ! ОТМАНИ ЕГО АУДИО !", True, RED)
                screen.blit(warn, (230, 385))
            else:
                lbl = font_sm.render("Коридор за окном пуст...", True, (100, 120, 100))
                screen.blit(lbl, (300, 230))

            #Предупреждение о поломках в углу экрана
            err_y = 85
            if state["audio_broken"]:
                screen.blit(font_sm.render("ERR: AUDIO DEVICE", True, RED), (55, err_y))
                err_y += 22
            if state["cam_broken"]:
                screen.blit(font_sm.render("ERR: CAMERA SYSTEM", True, RED), (55, err_y))

        # 2. ПАНЕЛЬ ПОЧИНКИ (MAINTENANCE PANEL)
        elif state["view"] == "MAINTENANCE":
            pygame.draw.rect(screen, (10, 20, 12), (60, 70, 780, 490))
            pygame.draw.rect(screen, GREEN, (60, 70, 780, 490), 2)
            screen.blit(font_md.render("SYSTEM RESTART // MAINTENANCE PANEL", True, GREEN), (120, 100))

            systems = [
                ("Audio Devices", state["audio_broken"], 170),
                ("Camera System", state["cam_broken"], 230),
                ("Ventilation", state["vent_broken"], 290),
            ]
            for name, is_err, y_pos in systems:
                status = "ERROR!" if is_err else "OK"
                col = RED if is_err else GREEN
                pygame.draw.rect(screen, col, (120, y_pos, 360, 45), 2)
                screen.blit(font_md.render(f"{name:<16} [{status}]", True, col), (135, y_pos + 10))

            # Кнопка Reboot All
            pygame.draw.rect(screen, YELLOW, (120, 370, 360, 50), 2)
            screen.blit(font_md.render("REBOOT ALL SYSTEMS (5s)", True, YELLOW), (145, 383))

            if state["rebooting"]:
                dots = "." * (int(pygame.time.get_ticks() / 300) % 4)
                prog = font_md.render(
                    f"Перезагрузка {state['rebooting']}{dots} ({state['reboot_timer']:.1f}s)", True,
                    WHITE)
                screen.blit(prog, (120, 450))

        # 3. МОНИТОР КАМЕР
        elif state["view"] == "CAMERAS":
            pygame.draw.rect(screen, (12, 18, 14), (40, 70, 820, 490))
            pygame.draw.rect(screen, GREEN, (40, 70, 820, 490), 2)

            #Окно видеопотока
            pygame.draw.rect(screen, (18, 25, 20), (65, 95, 530, 430))
            pygame.draw.rect(screen, DARK_GREEN, (65, 95, 530, 430), 2)

            if state["cam_broken"]:
                err_txt = font_lg.render("VIDEO ERROR", True, RED)
                sub_txt = font_sm.render("Требуется перезагрузка в панели SYSTEMS", True, WHITE)
                screen.blit(err_txt, (180, 260))
                screen.blit(sub_txt, (165, 320))
            else:
                if state["cam_mode"] == "FLOOR":
                    cam_id = state["current_cam"]
                    names = {
                        1: "CAM 01 - Дальний зал",
                        2: "CAM 02 - Главный коридор",
                        3: "CAM 03 - Окно офиса",
                        4: "CAM 04 - Дверь офиса",
                    }
                    screen.blit(font_md.render(names[cam_id], True, GREEN), (85, 110))

                    if not state["in_vent"] and state["springtrap_pos"] == cam_id:
                        draw_springtrap_silhouette(330, 330, scale=1.4)
                        st = "ОГЛУШЁН АУДИО" if state["stun_timer"] > 0 else "ОБНАРУЖЕНО ДВИЖЕНИЕ"
                        screen.blit(font_sm.render(st, True, YELLOW), (220, 470))
                    else:
                        screen.blit(font_sm.render("[ Сигнал стабилен. Никого нет ]", True, DARK_GREEN),
                                    (195, 300))
                else:
                    v_id = state["current_vent"]
                    screen.blit(font_md.render(f"VENT CAM 0{v_id} (Труба вентиляции)", True, GREEN),
                                (85, 110))
                    if state["sealed_vent"] == v_id:
                        pygame.draw.rect(screen, RED, (140, 180, 380, 240), 4)
                        screen.blit(font_md.render("ЛЮК ЗАБЛОКИРОВАН (SEALED)", True, RED), (175, 150))

                    if state["in_vent"] and state["springtrap_pos"] == v_id:
                        draw_springtrap_silhouette(330, 330, scale=1.2, angry=True)
                        screen.blit(font_sm.render("! ОН ПОЛЗЁТ ПО ВЕНТИЛЯЦИИ !", True, RED),
                                    (200, 470))

            #Правая панель управления камерами
            mode_label = "РЕЖИМ: ВЕНТИЛЯЦИЯ" if state["cam_mode"] == "VENT" else "РЕЖИМ: ЭТАЖ"
            pygame.draw.rect(screen, WHITE, (620, 95, 210, 40), 2)
            screen.blit(font_sm.render(mode_label, True, WHITE), (635, 107))

            if state["cam_mode"] == "FLOOR":
                for i in range(1, 5):
                    bx = 620 + ((i - 1) % 2) * 110
                    by = 160 + ((i - 1) // 2) * 60
                    col = GREEN if state["current_cam"] == i else GREY
                    pygame.draw.rect(screen, col, (bx, by, 95, 45), 2)
                    screen.blit(font_sm.render(f"CAM 0{i}", True, col), (bx + 20, by + 14))

                #Кнопка Play Audio
                if state["audio_broken"]:
                    a_col, a_txt = RED, "AUDIO ERROR"
                elif state["audio_cooldown"] > 0:
                    a_col, a_txt = GREY, f"WAIT {state['audio_cooldown']:.1f}s"
                else:
                    a_col, a_txt = GREEN, "PLAY AUDIO"
                pygame.draw.rect(screen, a_col, (620, 310, 210, 55), 2)
                screen.blit(font_md.render(a_txt, True, a_col), (655, 326))
                screen.blit(font_sm.render(f"Износ: {state['audio_uses']}/3", True, GREY), (620, 375))

            else:
                for v in (1, 2):
                    bx = 620 + (v - 1) * 110
                    col = GREEN if state["current_vent"] == v else GREY
                    pygame.draw.rect(screen, col, (bx, 160, 95, 45), 2)
                    screen.blit(font_sm.render(f"VENT 0{v}", True, col), (bx + 15, 174))

                s_col = RED if state["sealed_vent"] == state["current_vent"] else YELLOW
                s_txt = "UNSEAL VENT" if state["sealed_vent"] == state["current_vent"] else "SEAL VENT"
                pygame.draw.rect(screen, s_col, (620, 310, 210, 55), 2)
                screen.blit(font_md.render(s_txt, True, s_col), (650, 326))

        #Верхняя панель (Время и Ночь)
        hour_str = get_hour_text(state["time_elapsed"], state["night_duration"])
        screen.blit(font_md.render(hour_str, True, WHITE), (WIDTH - 120, 20))
        screen.blit(font_sm.render("Night 3", True, GREY), (WIDTH - 120, 46))

        #Нижние планки открытия планшетов (как в оригинале)
        pygame.draw.rect(screen, YELLOW, (40, 585, 320, 50), 2)
        screen.blit(font_md.render("[ SYSTEMS / REBOOT ]", True, YELLOW), (75, 598))

        pygame.draw.rect(screen, GREEN, (520, 585, 340, 50), 2)
        screen.blit(font_md.render("[ CAMERA MONITOR ]", True, GREEN), (575, 598))

        #Эффект поломки вентиляции (красный мигающий экран)
        if state["vent_broken"] and not state["game_over"] and not state["victory"]:
            pulse = int(abs(pygame.time.get_ticks() % 1000 - 500) / 500 * 90)
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(pulse)
            overlay.fill(RED)
            screen.blit(overlay, (0, 0))
            screen.blit(font_sm.render("ERR: VENTILATION", True, RED), (55, 129))

    #Поверх всего накладываем помехи и полосы монитора
    draw_scanlines_and_static(35 if state["view"] == "CAMERAS" else 12)
    
    pygame.display.flip()