import pyautogui
import time
import json
import math
import os
import shutil
import subprocess

main_path = "C:/Personal File/"
img_path = "C:/Personal File/code/project/gcode_for_batik/camotics_img/"
img_path_inkscape = "C:/Personal File/code/project/gcode_for_batik/inkscape_img/"

time.sleep(5)

# transform svg file to gcode with inkscape

print("Open Inkscape")

# to inkscape icon
to_ink_icon = pyautogui.locateOnScreen(img_path_inkscape + "1_ink_icon.PNG")
pyautogui.moveTo(to_ink_icon)
time.sleep(3)
pyautogui.click()

# to file
time.sleep(3)
to_file = pyautogui.locateOnScreen(img_path_inkscape + "2_file.PNG")
pyautogui.moveTo(to_file)
time.sleep(3)
pyautogui.click()

# import
time.sleep(3)
to_import = pyautogui.locateOnScreen(img_path_inkscape + "3_import.png")
pyautogui.moveTo(to_import)
time.sleep(3)
pyautogui.click()

# to svg file
time.sleep(3)
to_svg_file = pyautogui.locateOnScreen(img_path_inkscape + "4_svg_file.PNG")
pyautogui.moveTo(to_svg_file)
time.sleep(3)
pyautogui.doubleClick()

# to layer 
time.sleep(3)
to_layer = pyautogui.locateOnScreen(img_path_inkscape + "5_layer.PNG")
pyautogui.moveTo(to_layer)
time.sleep(3)
pyautogui.click()

# to add layer
time.sleep(3)
to_add_layer = pyautogui.locateOnScreen(img_path_inkscape + "6_add_layer.png")
pyautogui.moveTo(to_add_layer)
time.sleep(3)
pyautogui.click()

# to add btn
time.sleep(3)
to_add_btn = pyautogui.locateOnScreen(img_path_inkscape + "7_add_btn.PNG")
pyautogui.moveTo(to_add_btn)
time.sleep(3)
pyautogui.click()

# click object
time.sleep(3)
pyautogui.click()

# detect axis button
to_axis_btn = pyautogui.locateOnScreen(img_path_inkscape + "8_axis_dd.png")

while to_axis_btn == None:
	pyautogui.move(-10, 0)
	time.sleep(3)
	pyautogui.click()
	time.sleep(3)
	to_axis_btn = pyautogui.locateOnScreen(img_path_inkscape + "8_axis_dd.png")

# to axis button X
pyautogui.moveTo(to_axis_btn)
time.sleep(2)
pyautogui.move(-20, 0)
time.sleep(3)
pyautogui.click()

time.sleep(3)
pyautogui.hotkey('ctrl', 'a')
pyautogui.write('0') # change X to 0
pyautogui.press('enter')


#to axis button Y
y_axis_btn = pyautogui.locateOnScreen(img_path_inkscape + "9_y_axis.png")
pyautogui.moveTo(y_axis_btn)
pyautogui.move(20, 0)
time.sleep(2)
pyautogui.click()
time.sleep(3)
pyautogui.hotkey('ctrl', 'a')
pyautogui.write('0')
pyautogui.press('enter')

#to extensions

extensions = pyautogui.locateOnScreen(img_path_inkscape + "10_extensions.PNG")
pyautogui.moveTo(extensions)
time.sleep(3)
pyautogui.click()

# to gcode_tools
time.sleep(3)
gcode_tools = pyautogui.locateOnScreen(img_path_inkscape + "11_gcode_tools.png")
pyautogui.moveTo(gcode_tools)

# to path to gcode
time.sleep(3)
path_to_gcode = pyautogui.locateOnScreen(img_path_inkscape + "12_path_to_gcode.png")
pyautogui.moveTo(path_to_gcode)
time.sleep(3)
pyautogui.click()

# INSIDE PATH TO GCODE BOX

# Path to path tab
# to dropdown Cutting Order
time.sleep(3)
dd_path_to_gcode = pyautogui.locateOnScreen(img_path_inkscape + "13_dd_path_to_gcode.PNG")
pyautogui.moveTo(dd_path_to_gcode)
time.sleep(2)
pyautogui.click()

# to path by path

path_by_path = pyautogui.locateOnScreen(img_path_inkscape + "14_path_by_path.png")
if path_by_path == None:
	path_by_path = pyautogui.locateOnScreen(img_path_inkscape + "14_path_by_path_act.png")

pyautogui.moveTo(path_by_path)
time.sleep(2)
pyautogui.click()

# to preferences tab
time.sleep(2)
preferences_tab = pyautogui.locateOnScreen(img_path_inkscape + "15_preferences.PNG")
pyautogui.moveTo(preferences_tab)
time.sleep(2)
pyautogui.click()

# to file input, to change filename
time.sleep(3)
file_in_pref = pyautogui.locateOnScreen(img_path_inkscape + "16_file_inside_pref.PNG")
pyautogui.moveTo(file_in_pref)
pyautogui.move(30, 0)
pyautogui.click()
pyautogui.hotkey('ctrl', 'a')
pyautogui.write('output.ngc')

#to directory, to change path to save file
time.sleep(2)
dir_inside_pref = pyautogui.locateOnScreen(img_path_inkscape + "17_dir_inside_pref.PNG")
pyautogui.moveTo(dir_inside_pref)
time.sleep(2)
pyautogui.move(80, 0)	
time.sleep(2)
pyautogui.click()
pyautogui.hotkey('ctrl', 'a')
pyautogui.write('C:\Personal File\svg_to_gcode')


# to z safe input
time.sleep(2)
zsafe = pyautogui.locateCenterOnScreen(img_path_inkscape + "18_z_safe.PNG")
pyautogui.moveTo(zsafe)
pyautogui.move(300, 0)
time.sleep(2)
pyautogui.click()
pyautogui.hotkey('ctrl', 'a')
pyautogui.write('10')
pyautogui.press('enter')

#to path to gcode tab
time.sleep(2)
path_to_gcode_tab = pyautogui.moveTo(img_path_inkscape + "21_ptg_tab.PNG")
pyautogui.moveTo(path_to_gcode_tab)
time.sleep(2)
pyautogui.click()


# to apply btn
time.sleep(2)
apply_btn = pyautogui.moveTo(img_path_inkscape + "19_apply_path_to_gcode.PNG")
pyautogui.moveTo(apply_btn)
time.sleep(3)
pyautogui.click()

print("Converting svg to code")
# ok after apply
# time.sleep(3)
# ok_after_apply = pyautogui.moveTo(img_path_inkscape + "20_ok_after_apply.PNG")
# pyautogui.moveTo(ok_after_apply)
# time.sleep(3)
# pyautogui.click()


# checking the ngc / gcode file if it has filled with data ( bigger than 0MB)
# if bigger, than close inkscape
gcode_file_path = main_path + "/svg_to_gcode/output_0001.ngc"
print("converting svg to gcode...")
while True:
	try:
		file_size = os.path.getsize(gcode_file_path)
		if file_size > 0:break

	except:
		c = True
		# print("output_0001.ngc not found")

subprocess.call('TASKKILL /F /IM inkscape.exe', shell=True)

######################### IN CAMOTICS #########################


time.sleep(5)

print("Open Camotics...")

#open camotics
open_camotics = pyautogui.locateOnScreen(img_path + "0_cam_icon.PNG")
pyautogui.moveTo(open_camotics)
time.sleep(3)
pyautogui.click()

time.sleep(3)

print("Calculate estimate time...")

#open File
to_file = pyautogui.locateOnScreen(img_path + "1_file.PNG")

pyautogui.moveTo(to_file)

time.sleep(3)
pyautogui.click()

#open project
time.sleep(3)
to_open_project = pyautogui.locateOnScreen(img_path + "2_open_project.png")

pyautogui.moveTo(to_open_project)
time.sleep(3)
pyautogui.click()

#select directory target
time.sleep(3)
to_program_files = pyautogui.locateOnScreen(img_path + "3_program_files.png")
pyautogui.moveTo(to_program_files)
time.sleep(3)
pyautogui.click()

# to c directory
time.sleep(3)
to_c = pyautogui.locateOnScreen(img_path + "4_to_c.png")
pyautogui.moveTo(to_c)
time.sleep(3)
pyautogui.click() 

# to personal file
time.sleep(3)
to_personal_file = pyautogui.locateOnScreen(img_path + "5_personal_file.png")
pyautogui.moveTo(to_personal_file)
time.sleep(3)
pyautogui.doubleClick()

# to svg_to_gcode folder
time.sleep(3)
to_svg_to_gcode = pyautogui.locateOnScreen(img_path + "6_svg_to_gcode.png")
pyautogui.moveTo(to_svg_to_gcode)
time.sleep(3)
pyautogui.doubleClick()

# to output file
time.sleep(3)
to_output = pyautogui.locateOnScreen(img_path + "7_output.png")
pyautogui.moveTo(to_output)
time.sleep(3)
pyautogui.doubleClick()

# to file again
time.sleep(3)
pyautogui.moveTo(to_file)
time.sleep(3)
pyautogui.click()

# to export
time.sleep(3)
to_export = pyautogui.locateOnScreen(img_path + "8_export.png")
pyautogui.moveTo(to_export)
time.sleep(3)
pyautogui.click()

# to simulation_data
time.sleep(3)
to_simulation_data = pyautogui.locateOnScreen(img_path + "9_simulation_data.PNG")
pyautogui.moveTo(to_simulation_data)
time.sleep(3)
pyautogui.click()


# to ok
time.sleep(3)
to_oke = pyautogui.locateOnScreen(img_path + "10_ok.PNG")
pyautogui.moveTo(to_oke)
time.sleep(3)
pyautogui.click()

# to input box filename
time.sleep(3)
to_json_filename = pyautogui.locateOnScreen(img_path + "11_json_filename.PNG")
pyautogui.moveTo(to_json_filename)
time.sleep(3)
pyautogui.click()

# highlight / block all the filename
time.sleep(3)
pyautogui.hotkey('ctrl', 'a')

##press backspace to remove the filename
# time.sleep(2)
# pyautogui.press('backspace')

# write the json filename "result.json" in interval 0.25 second
pyautogui.write('result.json')

time.sleep(3)

# to program files after filling json name
to_pr_after_json = pyautogui.locateCenterOnScreen(img_path + "13_to_pf_after_json.PNG")
pyautogui.moveTo(to_pr_after_json)
time.sleep(3)
pyautogui.click()


# to c directory
time.sleep(3)
to_c_2 = pyautogui.locateOnScreen(img_path + "14_to_c_2.png")
pyautogui.moveTo(to_c_2)
time.sleep(3)
pyautogui.click()

# to personal file again
time.sleep(3)
to_personal_file_2 = pyautogui.locateOnScreen(img_path + "15_personal_file_2.PNG")
pyautogui.moveTo(to_personal_file_2)
time.sleep(3)
pyautogui.doubleClick()

# to estimation time folder
time.sleep(3)
to_est_time = pyautogui.locateOnScreen(img_path + "16_estimation_time.PNG")
pyautogui.moveTo(to_est_time)
time.sleep(3)
pyautogui.doubleClick()

# to save json
time.sleep(3)
to_save_json = pyautogui.locateOnScreen(img_path + "12_save_json.PNG")
pyautogui.moveTo(to_save_json)
time.sleep(3)
pyautogui.click()

time.sleep(20)

simulation_data = open(main_path + "estimation_time/result.json")

# return JSON object as dictionary
sim_data = json.load(simulation_data)

get_proc_time = sim_data["time"] #in seconds
proc_time_to_hours = get_proc_time / 3600
pch_to_str = str(proc_time_to_hours)
pchts_splitter = pch_to_str.split(".")
first_dec = "0"
second_dec = "0"

if len(pchts_splitter) > 0:
	first_dec = pchts_splitter[1][0]
	if len(pchts_splitter) > 1:
		second_dec = pchts_splitter[1][1]
join_pcths = pchts_splitter[0] + "." + first_dec + second_dec

proc_time_to_hours = float(join_pcths)
print(str(proc_time_to_hours) + " hours")
price = int(proc_time_to_hours * 17500)
print("price is ", price)

simulation_data.close()

# close Camotics

time.sleep(3)
close_btn = pyautogui.locateOnScreen(img_path + "17_close.PNG")
pyautogui.moveTo(close_btn)
time.sleep(3)
pyautogui.click()


# move gcode file to trash folder

src_folder = r"C:/Personal File/svg_to_gcode/"
dst_folder = r"C:/Personal File/svg_to_gcode/trash/"
filename = "output_0001.ngc"
timestamp = int(time.time())
new_name = str(timestamp) + ".ngc"
file_with_dest = os.path.join(dst_folder, new_name)

shutil.move(src_folder + filename, file_with_dest)

# move json file to trash folder
src_folder_json = r"C:/Personal File/estimation_time/"
dst_folder_json = r"C:/Personal File/estimation_time/trash/"
filename_json = "result.json"
new_name_json = str(timestamp) + ".json"
file_json_with_dest = os.path.join(dst_folder_json, new_name_json)

shutil.move(src_folder_json + filename_json, file_json_with_dest)

print("Estimation time finished")



