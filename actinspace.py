import math
import pygame
import io
import copy
import thread
import sys
from urllib2 import urlopen

def gps_to_tiles(lat_deg, lon_deg, zoom):
  """
  Transforms latitude and longitude to tile coordinates
  """
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.log(math.tan(lat_rad) +
                              (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
  return (xtile, ytile)

def tiles_to_gps(xtile, ytile, zoom):
  """
  Transforms tile coordinates to latitude and longitude
  """
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)

def colors_dict(pixels_grid):
  """
  Creates a dict where keys = colors and values = occurences of the color
  """
  color_dict = {}
  for pixels in pixels_grid:
    for pixel in pixels:
      if pixel in color_dict:
        color_dict[pixel] += 1
      else:
        color_dict[pixel] = 1

def color_max(colors_dict):
  """
  Return the color with the max occurences in the dict
  """
  return max(color_dict.iteritems(), key=operator.itemgetter(1))[0]

def rgb_pixel(pixel):
  """
  Returns a r, g or b pixel for a given pixel
  """
  rgb = [0,0,0]
  ind = pixel.index(max(pixel))
  rgb[ind] = 255
  return rgb

def rgb_grid(pixels_grid):
  """
  Creates an grid containing only r, g or b color from pixelsGrid
  """
  return [[rgb_pixel(c) for c in l] for l in pixels_grid]

def load_images(zoom, i, files, ind, images):
  """
  Load all images for a line of the matrice for the multi threading
  """
  line = []
  DL11, DR11 = 747, 748
  for j in range(DL11 * (2**(zoom - 11)), (DR11 * (2**(zoom - 11)) + 2**(zoom - 11)) + 1):
    url = "http://sandbox.youmapps.com/tiles/{}/{}/{}/{}".format(images[ind],zoom, i, j)
    image_str = urlopen(url).read()
    image_file = io.BytesIO(image_str)
    try:
      image = pygame.image.load(image_file)
    except:
      url = "http://sandbox.youmapps.com/tiles/DS_PHR1A_201307091049344_FR1_PX_E001N43_0615_01654/16/33023/23907"
      image_str = urlopen(url).read()
      image_file = io.BytesIO(image_str)
      image = pygame.image.load(image_file)
    line.append(image)
  files.append([line,i])

def create_photo_mat(zoom, ind, images):
  """
  Creates a matrice of images when given a zoom
  """
  files = []
  UL11, UR11  = 1031, 1032
  for i in range(UL11 * (2**(zoom - 11)), (UL11 * (2**(zoom - 11)) + 2**(zoom - 10)) + 1):
    # Start a new thread for each line
    thread.start_new_thread(load_images, (zoom,i,files,ind,images))
  return files

def start_and_sort_mat(zoom, ind, images):
  """
  Start the creation of the photo matrice and sort it
  """
  print("Loading with zoom {}. Please wait...").format(zoom)
  files = create_photo_mat(zoom, ind, images)
  while len(files) < ((1032 * (2**(zoom - 11)) + 2**(zoom - 11)) + 1) - \
        (1031 * (2**(zoom - 11))):
    pass
  print("DONE")
  files.sort(key=lambda x: x[-1])
  list_tiles = []
  for i in range(len(files)):
    line = []
    for j in range(len(files)):
      line.append(files[i][0][j])
    list_tiles.append(line)
  return list_tiles
 
def distance(list_dots, zoom, meters_by_pixels):
  """
  Distance between two dots
  """
  total_distance = 0
  if len(list_dots) > 1:
    for i in range(1, len(list_dots)):
      total_distance += math.sqrt((list_dots[i-1][0] - list_dots[i][0])**2 +
                                  (list_dots[i-1][1] - list_dots[i][1])**2)
  dist = total_distance * (meters_by_pixels * 2**(11 - zoom))
  print("")
  print("Distance between the dots : {} meters.".format(dist))
  print("")

#####################
### MAIN FUNCTION ###
#####################

# Init  
pygame.init()
screen = pygame.display.set_mode((800,600))
pygame.key.set_repeat(1, 30)

# Usage
print("""Usage:
r : red pixels
g : green pixels
b : blue pixels
s : satellite view
+ : zoom in
- : zoom out
n : next image
p : previous image
left clic : put a dot
right clic : remove a dot
enter : calculate distance between dots
""")

# Variables
pressed = False
move_x = 0
move_y = 0
zoom = 11
meters_by_pixels = 76.4370
list_dots = []
images = ["DS_PHR1A_201604111052119_FR1_PX_E001N43_0615_01712",
"DS_PHR1A_201603301044531_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201603231048389_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201602051100204_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201601241052449_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201601171056299_FR1_PX_E001N43_0615_01768",
"DS_PHR1A_201512171045376_FR1_PX_E001N43_0615_01768",
"DS_PHR1A_201512031053291_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201510311057099_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201510171104376_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201509281100580_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201509161053246_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201509091057175_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201508261104571_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201506231056554_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201506041053076_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201506021108203_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201504181104116_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201504131053028_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201503111056545_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201503061045268_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201502131056503_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201411011057160_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201409171053053_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201409101057246_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201409031100531_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201408101046059_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201408011104559_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201406191045299_FR1_PX_E001N43_0615_01711",
"DS_PHR1A_201406051053135_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201405221100463_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201405151104243_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201404141052385_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201404071056123_FR1_PX_E001N43_0615_01712",
"DS_PHR1A_201403121056043_FR1_PX_E001N43_0615_01654",
"DS_PHR1A_201312311053160_FR1_PX_E001N43_0615_01754",
"DS_PHR1A_201312121049254_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201312101104326_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201311281056201_FR1_PX_E001N43_0615_01654",
"DS_PHR1A_201310141052561_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201310071056401_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201309231104180_FR1_PX_E001N43_0615_01728",
"DS_PHR1A_201307091049344_FR1_PX_E001N43_0615_01654"]
ind_image = 0
list_tiles = start_and_sort_mat(zoom, ind_image, images)

# Pygame loop
while 1:
  screen.fill((255,255,255))
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()
    # Mouse events
    if event.type == pygame.MOUSEBUTTONDOWN:
      if event.button == 1:
        list_dots.append([pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]])
      if event.button == 3:
        if len(list_dots) > 0:
          del list_dots[-1]
    # Keyboard events
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_RETURN:
        if not pressed and len(list_dots) > 1:
          distance(list_dots, zoom, meters_by_pixels)
          pressed = True
      if event.key == pygame.K_UP:
        for dot in list_dots:
          dot[1] += 5 * (zoom - 10)
        move_y += 5 * (zoom - 10)
      if event.key == pygame.K_DOWN:
        for dot in list_dots:
          dot[1] -= 5 * (zoom - 10)
        move_y -= 5 * (zoom - 10)
      if event.key == pygame.K_LEFT:
        for dot in list_dots:
          dot[0] += 5 * (zoom - 10)
        move_x += 5 * (zoom - 10)
      if event.key == pygame.K_RIGHT:
        for dot in list_dots:
          dot[0] -= 5 * (zoom - 10)
        move_x -= 5 * (zoom - 10)
      if event.key == pygame.K_KP_PLUS:
        if zoom < 18:
          zoom += 1
          list_tiles = start_and_sort_mat(zoom, ind_image, images)
          list_dots = []
      if event.key == pygame.K_KP_MINUS:
        if zoom > 11:
          zoom -= 1
          list_tiles = start_and_sort_mat(zoom, ind_image, images)
          list_dots = []
      if event.key == pygame.K_r:
        list_tiles = start_and_sort_mat(zoom, ind_image, images)
        for i in range(len(list_tiles)):
          for j in range(len(list_tiles[i])):
            try:
              list_tiles[i][j] = pygame.surfarray.make_surface(pygame.surfarray.pixels_red(list_tiles[i][j]))
            except:
              pass
      if event.key == pygame.K_g:
        list_tiles = start_and_sort_mat(zoom, ind_image, images)
        for i in range(len(list_tiles)):
          for j in range(len(list_tiles[i])):
            try:
              list_tiles[i][j] = pygame.surfarray.make_surface(pygame.surfarray.pixels_green(list_tiles[i][j]))
            except:
              pass
      if event.key == pygame.K_b:
        list_tiles = start_and_sort_mat(zoom, ind_image, images)
        for i in range(len(list_tiles)):
          for j in range(len(list_tiles[i])):
            try:
              list_tiles[i][j] = pygame.surfarray.make_surface(pygame.surfarray.pixels_blue(list_tiles[i][j]))
            except:
              pass
      if event.key == pygame.K_s:
        list_tiles = start_and_sort_mat(zoom, ind_image, images)
      if event.key == pygame.K_n:
        if ind_image < len(images):
          ind_image += 1
          list_tiles = start_and_sort_mat(zoom, ind_image, images)
          list_dots = []
      if event.key == pygame.K_p:
        if ind_image > 0:
          ind_image -= 1
          list_tiles = start_and_sort_mat(zoom, ind_image, images)
          list_dots = []
          
    if event.type == pygame.KEYUP:
      if event.key == pygame.K_RETURN:
        pressed = False
  # Display
  for i in range(len(list_tiles)):
    for j in range(len(list_tiles[i])):
      img_rect = list_tiles[i][j].get_rect()
      img_rect.x = i * 256 + move_x
      img_rect.y = j * 256 + move_y
      screen.blit(list_tiles[i][j], img_rect)  
  if len(list_dots) > 1:
    pygame.draw.circle(screen, (255,255,0), list_dots[0], 3, 0)
    for i in range(1, len(list_dots)):
      pygame.draw.circle(screen, (255,255,0), list_dots[i], 3, 0)
      pygame.draw.line(screen, (255,255,0), list_dots[i-1], list_dots[i], 1)
  elif len(list_dots) == 1:
    pygame.draw.circle(screen, (255,255,0), list_dots[0], 3, 0)
    
  pygame.display.flip()

