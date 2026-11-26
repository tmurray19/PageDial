import os
from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.ActionCore import ActionCore
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport
from src.backend.PluginManager.EventAssigner import EventAssigner
from src.backend.DeckManagement.InputIdentifier import Input
import globals as gl


class PageCycle(ActionCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.has_configuration = False   # no config rows needed

        # Register event assigners so the UI rows aren't "None"
        self.add_event_assigner(EventAssigner(
            id="Next Page",
            ui_label="Next Page",
            default_events=[Input.Dial.Events.TURN_CW],
            callback=lambda data: self._step(+1),
        ))
        self.add_event_assigner(EventAssigner(
            id="Previous Page",
            ui_label="Previous Page",
            default_events=[Input.Dial.Events.TURN_CCW],
            callback=lambda data: self._step(-1),
        ))

    def _get_page_paths(self):
        return sorted(gl.page_manager.get_pages())

    def _current_index(self, pages):
        current = self.deck_controller.active_page
        if current is None:
            return -1
        try:
            return pages.index(current.json_path)
        except ValueError:
            return -1

    def _step(self, direction: int):
        pages = self._get_page_paths()
        if not pages:
            return
        idx = self._current_index(pages)
        next_idx = 0 if idx < 0 else (idx + direction) % len(pages)

        target_path = pages[next_idx]
        target_page = gl.page_manager.get_page(target_path, self.deck_controller)
        self.deck_controller.load_page(target_page)
        self.set_bottom_label(target_page.get_name())


class PageDialPlugin(PluginBase):
    def __init__(self):
        super().__init__()

        self.page_cycle_holder = ActionHolder(
            plugin_base=self,
            action_base=PageCycle,
            action_id_suffix="PageCycle",
            action_name="Page Cycle",
            action_support={
                Input.Key: ActionInputSupport.UNSUPPORTED,
                Input.Dial: ActionInputSupport.SUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.page_cycle_holder)

        self.register(
            plugin_name="Page Dial",
            github_repo="https://github.com/you/page-dial",
            plugin_version="1.0.0",
            app_version="1.5.0-beta.16",
        )
