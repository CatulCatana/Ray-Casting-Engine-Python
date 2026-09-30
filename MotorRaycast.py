import pygame
import math

pygame.init()

ancho_pantalla = 640
altura_pantalla = 480
ventana = pygame.display.set_mode((ancho_pantalla, altura_pantalla))
pygame.display.set_caption("Motor Raycast")

mapa = [
    "################",
    "#..............#",
    "#.......####...#",
    "#...#......#...#",
    "#...#......#...#",
    "#####......#...#",
    "#......##......#",
    "#...........##.#",
    "#...######.....#",
    "#..........##..#",
    "#...##.........#",
    "#......##......#",
    "#..............#",
    "#..##......##..#",
    "#......####....#",
    "################"
]

ancho_mapa = len(mapa[0])
altura_mapa = len(mapa)

pos_x = 2.0
pos_y = 2.0
angulo_jugador = math.pi / 2.0
fov = math.pi / 3.0
profundidad = 12.0  
velocidad = 0.06
velocidad_rotacion = 0.04

reloj = pygame.time.Clock()
estado_juego = "inicio"

texturas_pared_brillo = []
textura_piso_brillo = []
texturas_generadas = False

def dibujar_texto(superficie, texto, tamano, color, centro, sombra=True):
    fuente = pygame.font.Font(None, tamano)
    if sombra:
        texto_sombra = fuente.render(texto, True, (0, 0, 0))
        superficie.blit(texto_sombra, (centro[0] - texto_sombra.get_width() // 2 + 2, centro[1] - texto_sombra.get_height() // 2 + 2))
    texto_real = fuente.render(texto, True, color)
    superficie.blit(texto_real, (centro[0] - texto_real.get_width() // 2, centro[1] - texto_real.get_height() // 2))

def fract(n): return n - math.floor(n)

def hash12(x, y):
    d = x * 12.9898 + y * 78.233
    return fract(math.sin(d) * 43758.5453)

def mix(a, b, t): return a + (b - a) * t

def smoothstep(e0, e1, x):
    if x <= e0: return 0.0
    if x >= e1: return 1.0
    t = (x - e0) / (e1 - e0)
    return t * t * (3.0 - 2.0 * t)

def noise(x, y):
    ix = math.floor(x); iy = math.floor(y)
    fx = fract(x); fy = fract(y)
    ux = fx*fx*(3.0 - 2.0*fx); uy = fy*fy*(3.0 - 2.0*fy)
    return mix(mix(hash12(ix, iy), hash12(ix+1, iy), ux),
               mix(hash12(ix, iy+1), hash12(ix+1, iy+1), ux), uy)

def fbm(x, y):
    f = 0.0
    f += 0.5000 * noise(x, y); x *= 2.02; y *= 2.03
    f += 0.2500 * noise(x, y); x *= 2.03; y *= 2.01
    f += 0.1250 * noise(x, y); x *= 2.01; y *= 2.02
    f += 0.0625 * noise(x, y)
    return f

def generar_todas_las_texturas():
    global texturas_pared_brillo, textura_piso_brillo, texturas_generadas
    size = 64
    tex_pared_base = pygame.Surface((size, size))
    tex_piso_base = pygame.Surface((size, size))
    
    for y in range(size):
        for x in range(size):
            ux = (x/size)*6.0; uy = (y/size)*6.0
            ux += fbm(ux*1.5, uy*1.5) * 0.5; uy += fbm(ux*1.5+10.0, uy*1.5+10.0) * 0.5
            ss = smoothstep(0.2, 0.8, fbm(ux*2.0, uy*2.0))
            br = mix(0.12, 0.28, ss); bg = mix(0.09, 0.22, ss); bb = mix(0.07, 0.16, ss)
            m_f = fbm(ux*8.0, uy*8.0) * 0.4
            br = mix(br, 0.40, m_f); bg = mix(bg, 0.32, m_f); bb = mix(bb, 0.24, m_f)
            bf = 0.8 + 0.4 * fbm(ux*15.0, uy*15.0)
            br *= bf; bg *= bf; bb *= bf
            af = 0.5 + 0.5 * fbm(ux*0.8, uy*0.8)
            br *= af; bg *= af; bb *= af
            tex_piso_base.set_at((x, y), (int(min(255, max(0, br*255))), int(min(255, max(0, bg*255))), int(min(255, max(0, bb*255)))))

    for y in range(size):
        for x in range(size):
            ux = (x/size)*4.0; uy = (y/size)*4.0
            ux += fbm(ux*3.0, uy*3.0) * 0.12; uy += fbm(ux*3.0+10.0, uy*3.0+10.0) * 0.12
            bx = ux; by = uy * 2.5
            if int(math.floor(by)) % 2 == 1: bx += 0.5
            bl_x = fract(bx); bl_y = fract(by)
            d_edge = min(min(bl_x, 1.0 - bl_x), min(bl_y, 1.0 - bl_y) * 2.5)
            rb = hash12(math.floor(bx), math.floor(by))
            br = mix(0.42, 0.55, rb*0.6); bg = mix(0.43, 0.56, rb*0.6); bb = mix(0.45, 0.58, rb*0.6)
            det = 0.85 + 0.3 * fbm(ux*12.0, uy*12.0)
            br *= det; bg *= det; bb *= det
            sh = smoothstep(0.0, 0.2, d_edge) * 0.5 + 0.5
            br *= sh; bg *= sh; bb *= sh
            mx = smoothstep(0.02, 0.05, d_edge)
            fr = mix(0.12, br, mx); fg = mix(0.12, bg, mx); fb = mix(0.13, bb, mx)
            f_dirt = 0.45 + 0.55 * fbm(ux*1.5, uy*1.5)
            fr *= f_dirt; fg *= f_dirt; fb *= f_dirt
            tex_pared_base.set_at((x, y), (int(min(255, max(0, fr*255))), int(min(255, max(0, fg*255))), int(min(255, max(0, fb*255)))))

    color_niebla = (0, 0, 0)
    for b in range(10):
        intensidad_sombra = (b / 9.0)**2.0 
        tex_cara0 = pygame.Surface((size, size))
        tex_cara1 = pygame.Surface((size, size))
        matriz_piso = []
        
        for ty in range(size):
            fila_p = []
            for tx in range(size):
                cp = tex_pared_base.get_at((tx, ty))
                r1 = int(cp.r * (1-intensidad_sombra) + color_niebla[0] * intensidad_sombra)
                g1 = int(cp.g * (1-intensidad_sombra) + color_niebla[1] * intensidad_sombra)
                b1 = int(cp.b * (1-intensidad_sombra) + color_niebla[2] * intensidad_sombra)
                tex_cara1.set_at((tx, ty), (r1, g1, b1))
                
                r0 = int((cp.r * 0.65) * (1-intensidad_sombra) + color_niebla[0] * intensidad_sombra)
                g0 = int((cp.g * 0.65) * (1-intensidad_sombra) + color_niebla[1] * intensidad_sombra)
                b0 = int((cp.b * 0.65) * (1-intensidad_sombra) + color_niebla[2] * intensidad_sombra)
                tex_cara0.set_at((tx, ty), (r0, g0, b0))
                
                cpi = tex_piso_base.get_at((tx, ty))
                rpi = int(cpi.r * (1-intensidad_sombra) + color_niebla[0] * intensidad_sombra)
                gpi = int(cpi.g * (1-intensidad_sombra) + color_niebla[1] * intensidad_sombra)
                bpi = int(cpi.b * (1-intensidad_sombra) + color_niebla[2] * intensidad_sombra)
                fila_p.append((rpi, gpi, bpi))
                
            matriz_piso.append(fila_p)
            
        texturas_pared_brillo.append((tex_cara0, tex_cara1))
        textura_piso_brillo.append(matriz_piso)
        
    texturas_generadas = True

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit(); exit()

    teclas = pygame.key.get_pressed()

    if estado_juego == "inicio":
        ventana.fill((0, 0, 0))
        dibujar_texto(ventana, "MOTOR RAYCAST", 64, (200, 200, 200), (ancho_pantalla // 2, altura_pantalla // 2 - 20))
        dibujar_texto(ventana, "Presiona ESPACIO para iniciar", 28, (150, 150, 150), (ancho_pantalla // 2, altura_pantalla // 2 + 40))
        pygame.display.flip()

        if teclas[pygame.K_SPACE]: estado_juego = "generando"
            
    elif estado_juego == "generando":
        ventana.fill((0, 0, 0))
        dibujar_texto(ventana, "COMPILANDO SHADERS Y TEXTURAS...", 32, (200, 200, 200), (ancho_pantalla // 2, altura_pantalla // 2))
        pygame.display.flip()
        
        if not texturas_generadas: generar_todas_las_texturas()
        estado_juego = "jugando"

    elif estado_juego == "jugando":
        mov_x = 0.0; mov_y = 0.0

        if teclas[pygame.K_w]:
            mov_x += math.cos(angulo_jugador) * velocidad
            mov_y += math.sin(angulo_jugador) * velocidad
        if teclas[pygame.K_s]:
            mov_x -= math.cos(angulo_jugador) * velocidad
            mov_y -= math.sin(angulo_jugador) * velocidad
        if teclas[pygame.K_a]: angulo_jugador -= velocidad_rotacion
        if teclas[pygame.K_d]: angulo_jugador += velocidad_rotacion

        margen = 0.2
        dir_x = 1 if mov_x > 0 else -1; dir_y = 1 if mov_y > 0 else -1

        nuevo_x = pos_x + mov_x
        if mapa[int(pos_y)][int(nuevo_x + margen * dir_x)] != "#": pos_x = nuevo_x
        nuevo_y = pos_y + mov_y
        if mapa[int(nuevo_y + margen * dir_y)][int(pos_x)] != "#": pos_y = nuevo_y

        ventana.fill((0, 0, 0))

        mitad_w = ancho_pantalla // 2
        mitad_h = altura_pantalla // 2
        surf_piso = pygame.Surface((mitad_w, mitad_h // 2))
        arr_piso = pygame.PixelArray(surf_piso)
        
        for y in range(mitad_h // 2):
            y_real = (y + mitad_h // 2) * 2
            p = y_real - (altura_pantalla / 2.0)
            pos_z = altura_pantalla * 0.5
            
            row_distance = pos_z / p if p > 0 else 1e30
            idx_brillo = min(9, int((row_distance / profundidad) * 10))
            
            ray_dir_x0 = math.cos(angulo_jugador - fov / 2.0); ray_dir_y0 = math.sin(angulo_jugador - fov / 2.0)
            ray_dir_x1 = math.cos(angulo_jugador + fov / 2.0); ray_dir_y1 = math.sin(angulo_jugador + fov / 2.0)
            
            floor_step_x = row_distance * (ray_dir_x1 - ray_dir_x0) / mitad_w
            floor_step_y = row_distance * (ray_dir_y1 - ray_dir_y0) / mitad_w
            
            floor_x = pos_x + row_distance * ray_dir_x0
            floor_y = pos_y + row_distance * ray_dir_y0
            tex_p = textura_piso_brillo[idx_brillo]
            
            for x in range(mitad_w):
                cx = int(floor_x * 64.0) & 63; cy = int(floor_y * 64.0) & 63
                floor_x += floor_step_x; floor_y += floor_step_y
                arr_piso[x, y] = tex_p[cy][cx]
                
        del arr_piso 
        
        surf_piso_escalado = pygame.transform.smoothscale(surf_piso, (ancho_pantalla, altura_pantalla // 2))
        ventana.blit(surf_piso_escalado, (0, altura_pantalla // 2))

        for i in range(ancho_pantalla):
            angulo_rayo = (angulo_jugador - fov / 2.0) + (i / ancho_pantalla) * fov
            vec_x = math.cos(angulo_rayo); vec_y = math.sin(angulo_rayo)
            
            map_x = int(pos_x); map_y = int(pos_y)
            delta_dist_x = abs(1.0 / vec_x) if vec_x != 0 else 1e30
            delta_dist_y = abs(1.0 / vec_y) if vec_y != 0 else 1e30

            if vec_x < 0:
                step_x = -1; side_dist_x = (pos_x - map_x) * delta_dist_x
            else:
                step_x = 1; side_dist_x = (map_x + 1.0 - pos_x) * delta_dist_x

            if vec_y < 0:
                step_y = -1; side_dist_y = (pos_y - map_y) * delta_dist_y
            else:
                step_y = 1; side_dist_y = (map_y + 1.0 - pos_y) * delta_dist_y

            hit = False; cara_impacto = 0 

            while not hit:
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x; map_x += step_x; cara_impacto = 0
                else:
                    side_dist_y += delta_dist_y; map_y += step_y; cara_impacto = 1

                if map_x < 0 or map_x >= ancho_mapa or map_y < 0 or map_y >= altura_mapa:
                    hit = True; distancia_pared = profundidad
                elif mapa[map_y][map_x] == "#": hit = True

            if cara_impacto == 0:
                distancia_pared = side_dist_x - delta_dist_x; hit_coord = pos_y + distancia_pared * vec_y
            else:
                distancia_pared = side_dist_y - delta_dist_y; hit_coord = pos_x + distancia_pared * vec_x

            distancia_corregida = distancia_pared * math.cos(angulo_rayo - angulo_jugador)
            if distancia_corregida < 0.1: distancia_corregida = 0.1

            altura_pared = int(altura_pantalla / distancia_corregida)
            inicio_pared = max(0, (altura_pantalla // 2) - (altura_pared // 2))
            fin_pared = min(altura_pantalla, (altura_pantalla // 2) + (altura_pared // 2))

            tex_x = int((hit_coord - math.floor(hit_coord)) * 64.0)
            if cara_impacto == 0 and vec_x > 0: tex_x = 63 - tex_x
            if cara_impacto == 1 and vec_y < 0: tex_x = 63 - tex_x

            idx_brillo = min(9, int((distancia_pared / profundidad) * 10))
            tex_muro = texturas_pared_brillo[idx_brillo][cara_impacto]

            if inicio_pared < fin_pared:
                tira = tex_muro.subsurface((tex_x, 0, 1, 64))
                try:
                    tira_escalada = pygame.transform.smoothscale(tira, (1, fin_pared - inicio_pared))
                except ValueError:
                    tira_escalada = pygame.transform.scale(tira, (1, fin_pared - inicio_pared))
                ventana.blit(tira_escalada, (i, inicio_pared))

        tam_celda = 6
        mapa_ancho_px = ancho_mapa * tam_celda
        mapa_alto_px = altura_mapa * tam_celda
        
        surf_mapa = pygame.Surface((mapa_ancho_px, mapa_alto_px), pygame.SRCALPHA)
        surf_mapa.fill((0, 0, 0, 150))
        
        for y_m in range(altura_mapa):
            for x_m in range(ancho_mapa):
                if mapa[y_m][x_m] == "#":
                    pygame.draw.rect(surf_mapa, (120, 120, 120), (x_m * tam_celda, y_m * tam_celda, tam_celda, tam_celda))
        
        px_mapa = pos_x * tam_celda; py_mapa = pos_y * tam_celda
        pygame.draw.circle(surf_mapa, (255, 50, 50), (int(px_mapa), int(py_mapa)), 2)
        
        line_length = 8
        dx = math.cos(angulo_jugador) * line_length; dy = math.sin(angulo_jugador) * line_length
        pygame.draw.line(surf_mapa, (255, 255, 0), (px_mapa, py_mapa), (px_mapa + dx, py_mapa + dy))
        ventana.blit(surf_mapa, (10, 10))

        pygame.display.flip()
        reloj.tick(60)
