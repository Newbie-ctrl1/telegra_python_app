import flet as ft
import asyncio
import logging
from lib.screens.home_screen import HomeScreen
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main(page: ft.Page):
    try:
        # Configure page
        page.title = "Telegram App"
        page.padding = 0
        page.spacing = 0
        page.bgcolor = '#F8F9FE'
        
        # Set window properties using new API
        page.window.width = 400
        page.window.height = 800
        page.window.resizable = True
        page.window.maximizable = True
        page.window.minimizable = True
        
        # Create and show home screen
        home_screen = HomeScreen(page)
        page.controls.append(home_screen.build())
        page.update()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    try:
        load_dotenv()
        ft.app(target=main, view=ft.AppView.FLET_APP)
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise 