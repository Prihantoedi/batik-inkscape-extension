import pyautogui
import time


img_path = "C:/Personal File/code/project/gcode_for_batik/camotics_img/"


time.sleep(5)

#open File
to_file = pyautogui.locateOnScreen(img_path + "1_file.PNG")

# pyautogui.moveTo(to_file)

# time.sleep(3)
# pyautogui.click()

# #open project
# time.sleep(3)
# to_open_project = pyautogui.locateOnScreen(img_path + "2_open_project.png")

# pyautogui.moveTo(to_open_project)
# time.sleep(3)
# pyautogui.click()

# #select directory target
# time.sleep(3)
# to_program_files = pyautogui.locateOnScreen(img_path + "3_program_files.png")
# pyautogui.moveTo(to_program_files)
# time.sleep(3)
# pyautogui.click()

# # to c directory
# time.sleep(3)
# to_c = pyautogui.locateOnScreen(img_path + "4_to_c.png")
# pyautogui.moveTo(to_c)
# time.sleep(3)
# pyautogui.click() 

# # to personal file
# time.sleep(3)
# to_personal_file = pyautogui.locateOnScreen(img_path + "5_personal_file.png")
# pyautogui.moveTo(to_personal_file)
# time.sleep(3)
# pyautogui.doubleClick()

# # to svg_to_gcode folder
# time.sleep(3)
# to_svg_to_gcode = pyautogui.locateOnScreen(img_path + "6_svg_to_gcode.png")
# pyautogui.moveTo(to_svg_to_gcode)
# time.sleep(3)
# pyautogui.doubleClick()

# # to output file
# time.sleep(3)
# to_output = pyautogui.locateOnScreen(img_path + "7_output.png")
# pyautogui.moveTo(to_output)
# time.sleep(3)
# pyautogui.doubleClick()

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

# press backspace to remove the filename
time.sleep(2)
pyautogui.press('backspace')

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
