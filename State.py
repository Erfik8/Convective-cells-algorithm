from Screen import Screen
from Entitie import EntitiesStoreMemento, EntitiesStore
from PIL import Image

class StateCollection:
    def __init__(self) -> None:
        self.states: list[tuple[Screen,EntitiesStoreMemento]] = []
        self.screen_width: int = 0
        self.screen_height: int = 0
        self.current_screen_index: int = 0  # Added to keep track of the current screen index

    def add_state(self,screen: Screen, entities: EntitiesStoreMemento):
        if(self.screen_height != 0 or self.screen_width != 0):
            img = Image.open(screen.path)
            if(img.width != self.screen_width or img.height != self.screen_height):
                print("Images have different dimensions")
                exit(1)
            else:
                self.states.append((screen,entities))
        else:
            self.states.append((screen,entities))
            img = Image.open(screen.path)
            self.screen_height = img.height
            self.screen_width = img.width
    def is_empty(self) -> bool:
        if not self.states:
            return True
        
        return False
    def clear(self):
        self.states = []
        self.screen_height = 0
        self.screen_width = 0
        self.current_screen_index = 0
    def get_current_screen(self):
        return self.states[self.current_screen_index][0]
    
    def get_current_entities(self) -> EntitiesStore:
        return self.states[self.current_screen_index][1].rester_to_new()

    def switch_to_next_screen(self):
        self.current_screen_index = (self.current_screen_index + 1) % len(self.states)

    