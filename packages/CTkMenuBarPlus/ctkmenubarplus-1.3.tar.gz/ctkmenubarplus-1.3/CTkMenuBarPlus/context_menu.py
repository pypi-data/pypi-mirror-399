import customtkinter
import warnings
from .dropdown_menu import CustomDropdownMenu


class ContextMenu(CustomDropdownMenu):
    """A right-click context menu with full dropdown menu functionality.

    This class extends CustomDropdownMenu to provide context menu behavior that appears
    when the user right-clicks on a widget. It supports all enhanced features including:
    - Keyboard accelerators and shortcuts
    - Icons and checkable menu items
    - Submenus and hierarchical organization
    - Scrollable menus for large option lists
    - Automatic positioning at cursor location

    The context menu automatically binds to the target widget and its children,
    providing consistent right-click behavior throughout the widget hierarchy.

    Example:
        context_menu = ContextMenu(my_widget)
        context_menu.add_option("Copy", copy_function, accelerator="Ctrl+C")
        context_menu.add_option("Paste", paste_function, accelerator="Ctrl+V")
        context_menu.add_separator()
        context_menu.add_option("Delete", delete_function, accelerator="Delete")
    """

    def __init__(self, widget: customtkinter.CTkBaseClass, **kwargs):
        """Initialize a context menu.

        Args:
            widget: The widget to attach the context menu to
            **kwargs: Additional arguments passed to CustomDropdownMenu
        """
        # Create a dummy button to serve as the menu seed
        self._dummy_button = customtkinter.CTkButton(widget.master, text="", width=0, height=0)
        self._dummy_button.place_forget()  # Hide the dummy button

        super().__init__(widget=self._dummy_button, **kwargs)

        self.target_widget = widget
        self._bind_context_menu()

    def _bind_context_menu(self):
        """Bind right-click event to show context menu."""
        self.target_widget.bind("<Button-3>", self._show_context_menu, add="+")
        # Also bind to child widgets if it's a container
        try:
            for child in self.target_widget.winfo_children():
                child.bind("<Button-3>", self._show_context_menu, add="+")
        except:
            pass

    def _show_context_menu(self, event):
        """Show the context menu at the current cursor position.

        This method handles the right-click event by positioning the context menu
        at the cursor location with a small offset for better visibility. It:
        - Calculates cursor position relative to the target widget
        - Applies a small offset to prevent menu from appearing under cursor
        - Stores coordinates for potential repositioning
        - Shows the menu with proper focus and layering

        Args:
            event: The mouse event containing cursor coordinates

        Note:
            Includes error handling to gracefully handle coordinate calculation
            issues or widget state problems during menu display.
        """
        try:
            # Get cursor position in screen coordinates
            cursor_x = event.x_root - self.target_widget.winfo_rootx() + 30
            cursor_y = event.y_root - self.target_widget.winfo_rooty() + 30

            # Store the cursor position
            self._context_x = cursor_x
            self._context_y = cursor_y

            # Show the menu at cursor position using screen coordinates
            # Place it relative to the screen, not a parent widget
            self.place(x=cursor_x, y=cursor_y)
            self.lift()
            self.focus()

        except Exception as e:
            warnings.warn(f"Failed to show context menu: {e}")

    def _show(self):
        """Override _show to use stored cursor position."""
        if hasattr(self, '_context_x') and hasattr(self, '_context_y'):
            self.place(x=self._context_x, y=self._context_y)
        else:
            super()._show()
        self.lift()
        self.focus()

__all__ = ["ContextMenu"]
