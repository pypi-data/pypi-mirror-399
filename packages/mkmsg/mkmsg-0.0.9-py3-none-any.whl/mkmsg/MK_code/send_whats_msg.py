import webbrowser
import pyautogui
import time
class Send_whats_msg:
    def __init__(self, number: str, message: str, sleep=15):
        self.number = number
        self.message = message
        self.sleep = sleep
        """
        Send a WhatsApp message via WhatsApp Web.

        Args:
            number (str): Phone number in international format, without '+'
            message (str): Text message to send
        """
        try:
            message = message.replace(" ", "%20")
            webbrowser.open(f"https://web.whatsapp.com/send?phone={number}&text={message}")
            print("WhatsApp Web has opened... Wait a moment for the download to complete")
            time.sleep(sleep)
            pyautogui.press("enter")
            print("Successfully send.")
        
        except Exception as e:
            print(f"Error: {e}")