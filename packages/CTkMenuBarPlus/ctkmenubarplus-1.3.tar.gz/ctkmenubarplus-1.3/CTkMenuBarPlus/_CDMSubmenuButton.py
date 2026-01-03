import warnings
from typing import TYPE_CHECKING
from .custom_exception_classes import MenuOptionError
from ._CDMOptionButton import _CDMOptionButton
if TYPE_CHECKING:
    from .dropdown_menu import CustomDropdownMenu


class _CDMSubmenuButton(_CDMOptionButton):
    """Specialized button for submenu items that can hold child menus.

    This class extends _CDMOptionButton to provide submenu functionality,
    allowing menu items to open child dropdown menus when hovered or clicked.
    """

    def setSubmenu(self, submenu: "CustomDropdownMenu"):
        """Assign a submenu to this button.

        Args:
            submenu: The CustomDropdownMenu instance to assign as child menu
        """
        self.submenu = submenu

    def cget(self, param):
        if param == "submenu_name":
            return getattr(self, "_option_text", super().cget("text"))
        return super().cget(param)

    def configure(self, **kwargs):
        checkable, checked = kwargs.pop("checkable", None), kwargs.pop("checked", None)
        if checkable or checked:
            warnings.warn("Submenu button CAN'T be checkable, so you can't "
                          "configure checkable or checked params")
        if "submenu_name" in kwargs:
            kwargs["option"] = kwargs.pop("submenu_name", self.cget("submenu_name"))
        super().configure(**kwargs)

    def _activate_submenu_accelerator(self) -> None:
        """Open all parent menus and show this submenu when accelerator is used."""
        if not getattr(self, "enabled", True):
            return

        try:
            # Build chain of ancestor submenu buttons (from immediate parent up)
            chain_buttons = []  # from rootmost to just above self
            # Walk up via parent menus: if a parent menu's seed is a submenu button,
            # it means that menu is itself a submenu of a higher menu.
            btn = self
            top_menu = self.parent_menu
            while True:
                parent_menu = btn.parent_menu
                seed = getattr(parent_menu, 'menu_seed_object', None)
                if isinstance(seed, _CDMSubmenuButton):
                    chain_buttons.append(seed)
                    btn = seed
                else:
                    top_menu = parent_menu
                    break

            # Show the top-level menu first
            try:
                # Hide siblings at the bar level to avoid overlap
                if hasattr(top_menu, '_hide_sibling_menus'):
                    top_menu._hide_sibling_menus()
                top_menu._show()
                top_menu.lift()
                top_menu.focus()
                # Ensure geometry for proper child placement
                try:
                    top_menu.update_idletasks()
                    if not top_menu.winfo_ismapped():
                        top_menu.update()
                except Exception:
                    pass
            except Exception:
                pass

            # Then, for each ancestor submenu button from top to bottom, show its submenu
            for ancestor_btn in reversed(chain_buttons):
                try:
                    parent = ancestor_btn.parent_menu
                    if hasattr(parent, '_collapseSiblingSubmenus'):
                        parent._collapseSiblingSubmenus(ancestor_btn)
                    # Ensure geometry is up-to-date before placing submenu
                    try:
                        parent.update_idletasks()
                        if not parent.winfo_ismapped():
                            parent.update()
                        ancestor_btn.update_idletasks()
                    except Exception:
                        pass
                    ancestor_btn.submenu._show()
                    ancestor_btn.submenu.lift()
                except Exception:
                    continue

            # Finally, collapse siblings in our parent and show our submenu
            try:
                parent = self.parent_menu
                if hasattr(parent, '_collapseSiblingSubmenus'):
                    parent._collapseSiblingSubmenus(self)
                try:
                    parent.update_idletasks()
                    if not parent.winfo_ismapped():
                        parent.update()
                    self.update_idletasks()
                except Exception:
                    pass
                self.submenu._show()
                self.submenu.lift()
            except Exception:
                pass

        except Exception:
            # Silently ignore activation errors to avoid breaking global key handling
            return

__all__ = ["_CDMSubmenuButton"]
