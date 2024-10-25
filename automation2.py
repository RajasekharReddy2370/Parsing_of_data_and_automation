import time
import pytesseract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from PIL import Image
from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor
from surya.ocr import run_ocr
import pyautogui


class Pdf:
    def __init__(self):
        self.driver = self.setup_driver()

    def setup_driver(self):
        # Set up the Chrome WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")  # Start maximized
        service = Service('/usr/bin/chromedriver')  # Update the path to your chromedriver
        return webdriver.Chrome(service=service, options=chrome_options)

    def download(self):
        self.driver.get("https://ceotserms2.telangana.gov.in/MLC_ROLLS_TS/TEACHERS/Rolls.aspx")
        time.sleep(3)  # Wait for the page to load

        drp = self.driver.find_element(By.XPATH, "//select[@id='ddlAC']")
        drp.click()
        time.sleep(1)  # Short wait after clicking dropdown

        select = Select(drp)
        select.select_by_visible_text("2-Medak-Nizamabad-Adilabad-Karimnagar")
        time.sleep(1)  # Wait after selecting the option

        self.driver.find_element(By.XPATH, "//input[@type='submit']").click()
        time.sleep(3)  # Wait for the next page to load

        # view_links = self.driver.find_elements(By.XPATH, "//a[contains(@id, 'lnkEnglish')]")
        # print("Total records found:", len(view_links))
        #
        # for i in range(len(view_links)):
        #     view_links = self.driver.find_elements(By.XPATH, "//a[contains(@id, 'lnkEnglish')]")
        #     view_links[i].click()
        #     print("Clicked View for record", i + 1)
        #     time.sleep(3)  # Wait for the new page to load
        #
        #     stored_elements = []  # Move inside the loop to reset for each record
        #     elements = self.driver.find_elements(By.XPATH, "//table[@id='GridView1']/tbody/tr/td[2]")
        view_links = self.driver.find_elements(By.XPATH, "//a[contains(@id, 'lnkEnglish')]")
        print("Total records found:", len(view_links))

        for i in range(len(view_links)):
            view_links = self.driver.find_elements(By.XPATH, "//a[contains(@id, 'lnkEnglish')]")
            view_links[i].click()
            print("Clicked View for record", i + 1)
            time.sleep(3)  # Wait for the new page to load

            # Find the specific element for the clicked record
            elements = self.driver.find_elements(By.XPATH, "//table[@id='GridView1']/tbody/tr/td[2]")

            # Check if the list has enough elements to access the one needed
            if len(elements) > i:  # Ensure there are enough elements to access the desired one
                specific_element_text = elements[i].text  # Get the text of the i-th element
                print(f"Record {i + 1}: Element text: {specific_element_text}")
                Name = f"{specific_element_text}_{i+1}.pdf"# Print the element text
            else:
                print(f"Record {i + 1}: Not enough elements found.")

            # Find all the view links
            original_tab = self.driver.current_window_handle
            all_tabs = self.driver.window_handles

            new_tab = next(tab for tab in all_tabs if tab != original_tab)
            self.driver.switch_to.window(new_tab)
            time.sleep(3)  # Wait for the new tab to load

            # Wait for the verification code image to load
            wait = WebDriverWait(self.driver, 10)
            verification_code_element = wait.until(
                EC.visibility_of_element_located((By.XPATH, "//img[@id='Image2']"))
            )

            verification_code_element.screenshot("verification_code.png")

            # Load the image for OCR
            image_path = "verification_code.png"  # Path to the screenshot taken
            image = Image.open(image_path)

            # Load detection and recognition models
            langs = ["en"]  # Define the language for OCR
            det_processor, det_model = load_det_processor(), load_det_model()
            rec_model, rec_processor = load_rec_model(), load_rec_processor()

            # Run OCR on the image
            predictions = run_ocr([image], [langs], det_model, det_processor, rec_model, rec_processor)

            # Process and get the verification code
            verification_code = ""
            for prediction in predictions:
                for text_line in prediction.text_lines:
                    print("Text:", text_line.text)
                    # You may want to validate or format the verification code if needed
                    verification_code = text_line.text.strip()  # Use the last detected text line

            if verification_code:
                # Enter verification code in the input field
                verification_code_input = self.driver.find_element(By.ID, "txtVerificationCode")
                verification_code_input.send_keys(verification_code)
                time.sleep(2)  # Optional: wait for a short time to see the input

                submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit' and @value='Submit']")
                submit_button.click()

                # Maximize the window
                self.driver.maximize_window()

                # Wait for the page to load (adjust time as needed)
                time.sleep(10)

                # Switch to the newly opened tab
                self.driver.switch_to.window(self.driver.window_handles[-1])

                # Wait for the new tab to fully load if necessary
                time.sleep(10)

                # Trigger Ctrl + P (to open the print dialog)
                pyautogui.hotkey('ctrl', 'p')
                time.sleep(5)
                # Move the mouse to the Save button's coordinates and click (replace X, Y with the actual coordinates)
                pyautogui.click(x=1564, y=878)  # save button in pop up
                time.sleep(3)
                pyautogui.click(x=599, y=471)  # click desktop button
                time.sleep(2)
                pyautogui.doubleClick(x=755, y=524)  ## double click teacher folder button
                time.sleep(2)
                pyautogui.doubleClick(x=817, y=503)  ## double click M_N_A_K folder button
                time.sleep(2)
                # pyautogui.doubleClick(x=888, y=390)  ## double click to change name folder button
                pyautogui.click(x=904, y=390, clicks=3, interval=0.1)  # Adjust interval as needed
                time.sleep(2)
                pyautogui.press('backspace')  # To remove the name
                time.sleep(2)
                pyautogui.typewrite(Name)  # pasting the polling station name and location

                pyautogui.click(x=1418, y=390)  ## click save button
                time.sleep(5)

            # Switch back to the original tab
            self.driver.switch_to.window(original_tab)
            time.sleep(1)  # Wait before going back to the original tab

        # Close the driver
        self.driver.quit()


if __name__ == "__main__":
    pdf = Pdf()
    pdf.download()

##########################################################################################################
# import time
# import pytesseract
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import Select, WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from PIL import Image
# from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
# from surya.model.recognition.model import load_model as load_rec_model
# from surya.model.recognition.processor import load_processor as load_rec_processor
# from surya.ocr import run_ocr
# import pyautogui
#
# class Pdf:
#     def __init__(self):
#         self.driver = self.setup_driver()
#
#     def setup_driver(self):
#         # Set up the Chrome WebDriver
#         chrome_options = Options()
#         chrome_options.add_argument("--start-maximized")  # Start maximized
#         service = Service('/usr/bin/chromedriver')  # Update the path to your chromedriver
#         return webdriver.Chrome(service=service, options=chrome_options)
#
#     def download(self):
#         self.driver.get("https://ceotserms2.telangana.gov.in/MLC_ROLLS_TS/graduates/Rolls.aspx")
#         time.sleep(3)  # Wait for the page to load
#
#         drp = self.driver.find_element(By.XPATH, "//select[@id='ddlAC']")
#         drp.click()
#         time.sleep(1)  # Short wait after clicking dropdown
#
#         select = Select(drp)
#         select.select_by_visible_text("2-Medak-Nizamabad-Adilabad-Karimnagar")
#         time.sleep(1)  # Wait after selecting the option
#
#         self.driver.find_element(By.XPATH, "//input[@type='submit']").click()
#         time.sleep(3)  # Wait for the next page to load
#
#         view_links = self.driver.find_elements(By.XPATH, "//a[contains(@id, 'lnkEnglish')]")
#         print("Total records found:", len(view_links))
#
#         for i in range(len(view_links)):
#             view_links = self.driver.find_elements(By.XPATH, "//a[contains(@id, 'lnkEnglish')]")
#             view_links[i].click()
#             print("Clicked View for record", i + 1)
#             time.sleep(3)  # Wait for the new page to load
#         stored_elements = []
#         elements = self.driver.find_elements(By.XPATH, "//table[@id='GridView1']/tbody/tr/td[2]")
#
#         # Iterate through the found elements
#         for i in range(len(elements)):  # Loop over the indices of the elements
#             # Store the text of the element for the current iteration
#             if elements:  # Ensure elements exist
#                 element_text = elements[i].text  # Get the text of the current element
#                 stored_elements.append(element_text)  # Store the corresponding element text
#                 print(f"Iteration {i + 1}: Stored element text: {element_text}")  # Print iteration and element
#             else:
#                 stored_elements.append(None)  # In case no element is found
#                 print(f"Iteration {i + 1}: No element found")
#
#         # Find all the view links
#
#             original_tab = self.driver.current_window_handle
#             all_tabs = self.driver.window_handles
#
#             new_tab = next(tab for tab in all_tabs if tab != original_tab)
#             self.driver.switch_to.window(new_tab)
#             time.sleep(3)  # Wait for the new tab to load
#
#             # Wait for the verification code image to load
#             wait = WebDriverWait(self.driver, 10)
#             verification_code_element = wait.until(
#                 EC.visibility_of_element_located((By.XPATH, "//img[@id='Image2']"))
#             )
#
#             verification_code_element.screenshot("verification_code.png")
#
#             # Load the image for OCR
#             image_path = "verification_code.png"  # Path to the screenshot taken
#             image = Image.open(image_path)
#
#             # Load detection and recognition models
#             langs = ["en"]  # Define the language for OCR
#             det_processor, det_model = load_det_processor(), load_det_model()
#             rec_model, rec_processor = load_rec_model(), load_rec_processor()
#
#             # Run OCR on the image
#             predictions = run_ocr([image], [langs], det_model, det_processor, rec_model, rec_processor)
#
#             # Process and get the verification code
#             verification_code = ""
#             for prediction in predictions:
#                 for text_line in prediction.text_lines:
#                     print("Text:", text_line.text)
#                     # You may want to validate or format the verification code if needed
#                     verification_code = text_line.text.strip()  # Use the last detected text line
#
#             if verification_code:
#                 # Enter verification code in the input field
#                 verification_code_input = self.driver.find_element(By.ID, "txtVerificationCode")
#                 verification_code_input.send_keys(verification_code)
#                 time.sleep(2)  # Optional: wait for a short time to see the input
#
#                 submit_button = self.driver.find_element(By.XPATH, "//input[@type='submit' and @value='Submit']")
#                 submit_button.click()
#
#                 # # Maximize the window
#                 # self.driver.maximize_window()
#                 #
#                 # # Wait for the page to load (adjust time as needed)
#                 # time.sleep(10)
#                 #
#                 # # Switch to the newly opened tab
#                 # self.driver.switch_to.window(self.driver.window_handles[-1])
#                 #
#                 # # Wait for the new tab to fully load if necessary
#                 # time.sleep(10)
#                 #
#                 # # Trigger Ctrl + P (to open the print dialog)
#                 # pyautogui.hotkey('ctrl', 'p')
#                 # time.sleep(5)
#                 # # Move the mouse to the Save button's coordinates and click (replace X, Y with the actual coordinates)
#                 # pyautogui.click(x=1564, y=878)  # save button in pop up
#                 # time.sleep(3)
#                 # pyautogui.click(x=599, y=471)  # click desktop button9_Medak_Nizamabad_Adilabad_Karimnagar.pdf
#                 # time.sleep(2)
#                 # pyautogui.doubleClick(x=743, y=535)  ## double click teacher folder button
#                 # time.sleep(2)
#                 # pyautogui.doubleClick(x=836, y=502)  ## double click M_N_A_K folder button
#                 # time.sleep(2)
#                 # # pyautogui.doubleClick(x=888, y=390)  ## double click to change name folder button
#                 # pyautogui.click(x=888, y=390, clicks=3, interval=0.1)  # Adjust interval as needed
#                 # time.sleep(2)
#                 # pyautogui.press('backspace') # To remove the name
#                 # time.sleep(2)
#                 # pyautogui.typewrite(combined_string) # pasting the polling station name and location
#                 #
#                 # pyautogui.click(x=1415, y=393)  ## click save button
#                 # time.sleep(5)
#
#             # Switch back to the original tab
#             self.driver.switch_to.window(original_tab)
#             time.sleep(1)  # Wait before going back to the original tab
#
#         # Close the driver
#         self.driver.quit()
#
#
# if __name__ == "__main__":
#     pdf = Pdf()
#     pdf.download()
