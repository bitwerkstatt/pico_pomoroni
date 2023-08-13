import math
import utime
import urandom as random
import machine
from picounicorn import PicoUnicorn

unicorn = PicoUnicorn()
clock = machine.RTC()
BUTTON_IDLE_TIME = 250

def clrscr():
    for x in range(16):
        for y in range(7):
            unicorn.set_pixel(x, y, 0, 0, 0)
        

def wait(cycles):
    for i in range(cycles):
        if not unicorn.is_pressed(unicorn.BUTTON_Y):
            utime.sleep(0.1)
        else:
            break
        
        
def pomodoro():
    colors = [(255,69,0),(0, 255, 0)]
    cycles = [134, 27]
    phase = 0 # 0 = work, 1 = rest
    
    while not unicorn.is_pressed(unicorn.BUTTON_Y):
        column = 15
        row = 6
        for x in range(16):
            for y in range(7):
                unicorn.set_pixel(x, y, colors[phase][0],colors[phase][1],colors[phase][2])
                
        while column > -1:
            while row > -1:
                wait(cycles[phase])
                unicorn.set_pixel(column, row, 0, 0, 0)
                row -= 1
            row = 6
            column -= 1
        column = 15
         
        phase = not phase
        

@micropython.native  # noqa: F821
def supercomputer():
    width = 16
    height = 7
    color = (230, 150, 0)
    
    # setup
    lifetime = [[0.0 for y in range(height)] for x in range(width)]
    age = [[0.0 for y in range(height)] for x in range(width)]
    for y in range(height):
        for x in range(width):
            lifetime[x][y] = 1.0 + random.uniform(0.0, 0.1)
            age[x][y] = random.uniform(0.0, 1.0) * lifetime[x][y]

    while not unicorn.is_pressed(unicorn.BUTTON_Y):
        # update
        for y in range(height):
            for x in range(width):
                if age[x][y] >= lifetime[x][y]:
                    age[x][y] = 0.0
                    lifetime[x][y] = 1.0 + random.uniform(0.0, 0.1)

                age[x][y] += 0.025
        
        # draw
        for y in range(height):
            for x in range(width):
                if age[x][y] < lifetime[x][y] * 0.3:
                    pixel_color = (color[0], color[1], color[2])
                elif age[x][y] < lifetime[x][y] * 0.5:
                    decay = (lifetime[x][y] * 0.5 - age[x][y]) * 5.0
                    pixel_color = (int(decay * color[0]), int(decay * color[1]), int(decay * color[2]))
                else:
                    pixel_color = (0, 0, 0)
                unicorn.set_pixel(x, y, pixel_color[0], pixel_color[1], pixel_color[2])


@micropython.native  # noqa: F821
def flames():
    fire_colours = [(0, 0, 0),
                (20, 20, 20),
                (180, 30, 0),
                (220, 160, 0),
                (255, 255, 180)]
    
    width = 16 + 2
    height = 7 + 1
    heat = [[0.0 for y in range(height)] for x in range(width)]
    fire_spawns = 5
    damping_factor = 0.8
    
    while not unicorn.is_pressed(unicorn.BUTTON_Y):
        
        # update
        for x in range(width):
            heat[x][height - 1] = 0.0
            heat[x][height - 2] = 0.0

        for c in range(fire_spawns):
            x = random.randint(0, width - 4) + 2
            heat[x + 0][height - 1] = 1.0
            heat[x + 1][height - 1] = 1.0
            heat[x - 1][height - 1] = 1.0
            heat[x + 0][height - 2] = 1.0
            heat[x + 1][height - 2] = 1.0
            heat[x - 1][height - 2] = 1.0

        factor = damping_factor / 5.0
        for y in range(0, height - 2):
            for x in range(1, width - 1):
                heat[x][y] += heat[x][y + 1] + heat[x][y + 2] + heat[x - 1][y + 1] + heat[x + 1][y + 1]
                heat[x][y] *= factor
        
        # draw

        for y in range(7):
            for x in range(16):
                value = heat[x + 1][y]
                if value < 0.15:
                    pixel_color = fire_colours[0]
                elif value < 0.25:
                    pixel_color = fire_colours[1]
                elif value < 0.35:
                    pixel_color = fire_colours[2]
                elif value < 0.45:
                    pixel_color = fire_colours[3]
                else:
                    pixel_color = fire_colours[4]
                unicorn.set_pixel(x, y, pixel_color[0], pixel_color[1], pixel_color[2])
        
        utime.sleep(0.05)

@micropython.native  # noqa: F821
def berlin_clock():
    
    MODE_SETTIME = 1
    MODE_RUNCLOCK = 2
    
    handling_a_ts = utime.ticks_ms()
    handling_b_ts = utime.ticks_ms()
    handling_x_ts = utime.ticks_ms()
    
    mode = MODE_RUNCLOCK
    
    # inner function to draw a lamp
    def draw_lamp(xs, ys, w, h, r, g, b):
        for x in range(xs, xs+w):
            for y in range(ys, ys+h):
                unicorn.set_pixel(x, y, r, g, b)
            
    def render_time(hours, minutes, seconds):
    
        # Top hour lamps
        for i in range(4):
            if i < hours//5:
                draw_lamp(i*4,1,3,1,255,153,0)
            else:
                draw_lamp(i*4,1,3,1,20,20,20)
        
        # Bottom hour lamps
        for i in range(4):
            if i < hours%5:
                draw_lamp(i*4,2,3,1,255,153,102)
            else:
                draw_lamp(i*4,2,3,1,20,20,20)
        
        
        # Top minute lamps
        for i in range(11):
            if i < minutes//5:
                if i>0 and (i+1)%3 == 0:
                    draw_lamp(i,4,1,1,0,17,238)
                else:
                    draw_lamp(i,4,1,1,58,75,126)                
            else:
                draw_lamp(i,4,1,1,20,20,20)
        
        # Bottom minute lamps
        for i in range(4):
            if i < minutes%5:
                draw_lamp(i*4,5,3,1,51,102,255)
            else:
                draw_lamp(i*4,5,3,1,20,20,20)
                
        # Seconds blinker
        for i in range(14):
            if seconds == 255: # Hack for settime
                draw_lamp(1+i,3,1,1,0,0,255)
            else:
                if seconds % 2:
                    draw_lamp(1+i,3,1,1,204,102,153)
                else:
                    draw_lamp(1+i,3,1,1,20,20,20)            

    
    while not unicorn.is_pressed(unicorn.BUTTON_Y):
        current_tick = utime.ticks_ms()
        handling_button_a = unicorn.is_pressed(unicorn.BUTTON_A) and not (current_tick - handling_a_ts) < BUTTON_IDLE_TIME 
        handling_button_b = unicorn.is_pressed(unicorn.BUTTON_B) and not (current_tick - handling_b_ts) < BUTTON_IDLE_TIME
        handling_button_x = unicorn.is_pressed(unicorn.BUTTON_X) and not (current_tick - handling_x_ts) < BUTTON_IDLE_TIME

        if handling_button_x:
            if mode == MODE_SETTIME:
                clock.datetime((2023,7,15,0,hours_to_set, minutes_to_set,0,0))
                mode = MODE_RUNCLOCK
            else:
                hours_to_set = clock.datetime()[4]
                minutes_to_set = clock.datetime()[5]
                mode = MODE_SETTIME
            handling_x_ts = current_tick
        
              
        if mode == MODE_SETTIME:
                    
            if handling_button_a:
                hours_to_set = (hours_to_set+1)%24
                handling_a_ts = current_tick 
            
            if handling_button_b:
                minutes_to_set = (minutes_to_set+1)%60
                handling_b_ts = current_tick
            
            render_time(hours_to_set, minutes_to_set, 255)
        
        else:
            current_time = clock.datetime()
            render_time(current_time[4], current_time[5], current_time[6])
        

while True:
    while unicorn.is_pressed(unicorn.BUTTON_X):
        pomodoro()
    while unicorn.is_pressed(unicorn.BUTTON_A):
        supercomputer()
    while unicorn.is_pressed(unicorn.BUTTON_B):
        berlin_clock()
    while unicorn.is_pressed(unicorn.BUTTON_Y):
        clrscr()