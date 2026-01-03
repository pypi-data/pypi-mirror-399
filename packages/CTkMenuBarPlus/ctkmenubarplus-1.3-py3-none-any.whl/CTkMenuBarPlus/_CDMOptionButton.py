import customtkinter
import sys
from PIL.Image import Image
import PIL
from typing import Union, TYPE_CHECKING, Any
from .accelerators import _register_accelerator, _unregister_accelerator
from .constants import DEFAULT_ICON_SIZE
from .custom_exception_classes import *
if TYPE_CHECKING:
    from .dropdown_menu import CustomDropdownMenu


class _CDMOptionButton(customtkinter.CTkButton):
    """Enhanced option button for dropdown menus with accelerator, icon, and state support."""

    def __init__(self, *args, **kwargs):
        """Initialize option button with enhanced features.

        Args:
            accelerator: Keyboard shortcut (e.g., "Ctrl+O")
            icon: Path to icon file or PIL Image object
            icon_size: Size (px) to render icon at; defaults to menu's scaled icon size
            checkable: Whether this item can be checked/unchecked
            checked: Initial checked state
            enabled: Whether the item is initially enabled
            **kwargs: Additional arguments passed to CTkButton
        """
        # Extract and store custom parameters
        self.accelerator = kwargs.pop('accelerator', None)
        self.icon = kwargs.pop('icon', None)
        self.icon_size = kwargs.pop('icon_size', DEFAULT_ICON_SIZE)
        self.base_icon_size = self.icon_size
        self.checkable = kwargs.pop('checkable', False)
        self.checked = kwargs.pop('checked', False)
        self.enabled = kwargs.pop('enabled', True)

        # Capture logical text before parent init so we can preserve it
        self._option_text = kwargs.get("text", "")

        # Initialize parent button
        super().__init__(*args, **kwargs)

        # Setup initial configuration
        self._configure_initial_state()
        self._setup_features()

    def _configure_initial_state(self) -> None:
        """Configure the initial state of the button."""
        if not self.enabled:
            self.configure(state="disabled")

    def _setup_features(self) -> None:
        """Setup all enhanced features (icon, accelerator, checkable state)."""
        if self.accelerator:
            self._setup_accelerator_display()
        if self.checkable:
            self.set_checked(self.checked)

    def _setup_icon(self) -> None:
        """Setup icon for the menu item."""
        try:
            # Load image from file or use provided PIL image
            if isinstance(self.icon, str):
                image = PIL.Image.open(self.icon)
            else:
                image = self.icon
            self.icon_size = max(8, round(self.base_icon_size * self.parent_menu.cget("scale")))
            # Resize to configured icon size
            size = self.icon_size
            image = image.resize((size, size), PIL.Image.Resampling.LANCZOS)
            self.icon_image = customtkinter.CTkImage(
                light_image=image,
                dark_image=image,
                size=(size, size)
            )
            self.configure(image=self.icon_image)

        except Exception as e:
            raise MenuIconError(f"Error loading icon: {e}") from e

    def _setup_accelerator_display(self) -> None:
        """Ensure accelerator is reflected in display string."""
        self._refresh_display()

    def _get_accel_targets(self):
        """Return a list of windows to bind accelerators to.

        For title_menu overlay (transient toplevel), we bind to BOTH the
        overlay and its transient master so that shortcuts work regardless of
        where the focus currently is (overlay or main window).
        """
        tl = self.parent_menu.winfo_toplevel()
        targets = [tl]
        try:
            trans_path = tl.tk.call('wm', 'transient', tl._w)
            if trans_path:
                master_widget = tl.nametowidget(trans_path)
                if hasattr(master_widget, 'winfo_toplevel'):
                    master_tl = master_widget.winfo_toplevel()
                    if master_tl not in targets:
                        targets.append(master_tl)
        except Exception:
            pass
        return targets

    def setParentMenu(self, menu: "CustomDropdownMenu") -> None:
        """Set the parent menu and bind accelerator if provided.

        Args:
            menu: The parent dropdown menu
        """
        self.parent_menu = menu

        if self.icon:
            self._setup_icon()
        if self.accelerator:
            self._bind_accelerator()

    def _bind_accelerator(self) -> None:
        """Bind keyboard accelerator to the command with error handling."""
        try:
            targets = self._get_accel_targets()
            target_ids = {t.winfo_id() for t in targets}
            command = getattr(self, "_activate_submenu_accelerator", self._execute_if_enabled)

            # If already bound with same key and same targets, skip
            if (getattr(self, "_accel_bound", False)
                    and getattr(self, "_accel_key", None) == self.accelerator
                    and getattr(self, "_accel_target_ids", None) == target_ids):
                return

            # Unregister old bindings if key or targets changed
            if (getattr(self, "_accel_bound", False)
                    and (getattr(self, "_accel_key", None) != self.accelerator
                         or getattr(self, "_accel_target_ids", None) != target_ids)):
                prev_targets = getattr(self, "_accel_targets", []) or []
                for pt in prev_targets:
                    try:
                        _unregister_accelerator(pt, getattr(self, "_accel_key", None), command)
                    except Exception:
                        pass

            # Register on all targets
            for t in targets:
                _register_accelerator(t, self.accelerator, command)

            # Mark as bound
            self._accel_bound = True
            self._accel_key = self.accelerator
            self._accel_targets = targets
            self._accel_target_ids = target_ids

        except Exception as e:
            raise MenuWidgetBindingError(f"Error binding accelerator {self.accelerator}: {e}") from e

    def _execute_if_enabled(self) -> None:
        """Execute button command only if enabled."""
        if self.enabled:
            self.invoke()

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the menu item.

        Args:
            enabled: Whether the item should be enabled
        """
        self.enabled = enabled
        self.configure(state="normal" if enabled else "disabled")

    def enable(self, enabled: bool = True) -> None:
        """Enable or disable the menu item (alias for set_enabled).

        Args:
            enabled: Whether the item should be enabled (default: True)
        """
        self.set_enabled(enabled)

    def set_checked(self, checked: bool) -> None:
        """Set the checked state for checkable items.

        Args:
            checked: Whether the item should be checked
        """
        if not self.checkable:
            return

        self.checked = checked
        self._refresh_display()

    def _refresh_display(self) -> None:
        """Compose and set the display text from logical text, checkmark, and accelerator."""
        base = self._option_text or ""
        # Apply checkmark prefix if checkable
        if self.checkable:
            prefix = "✅ " if getattr(self, "checked", False) else "❌  "
            base = f"{prefix}{base}"
        # Apply accelerator suffix with spacing
        if self.accelerator:
            accel_display = self.accelerator
            # Normalize CmdOrCtrl pseudo-modifier for platform display
            try:
                if sys.platform == 'darwin':
                    accel_display = accel_display.replace('CmdOrCtrl', 'Cmd')
                else:
                    accel_display = accel_display.replace('CmdOrCtrl', 'Ctrl')
            except Exception:
                # Fallback: leave as-is if platform check fails
                pass
            base = f"{base}    {accel_display}"
        super().configure(text=base)

    def toggle_checked(self) -> None:
        """Toggle the checked state for checkable items."""
        if self.checkable:
            self.set_checked(not self.checked)

    # Enhanced cget and configure methods
    def cget(self, param: str) -> Any:
        """Get configuration parameter value with support for custom parameters.

        Args:
            param: Parameter name to retrieve

        Returns:
            Parameter value
        """
        custom_params = {
            "option": lambda: self._option_text,
            "accelerator": lambda: self.accelerator,
            "enabled": lambda: self.enabled,
            "checked": lambda: self.checked,
            "checkable": lambda: self.checkable,
            "icon": lambda: self.icon,
            "scaled_icon_size": lambda: self.icon_size,
            "icon_size": lambda: self.base_icon_size
        }

        if param in custom_params:
            return custom_params[param]()

        return super().cget(param)

    def configure(self, **kwargs) -> None:
        """Configure button with support for custom parameters.

        Args:
            **kwargs: Configuration parameters
        """
        # Handle custom parameters
        custom_handlers = {
            "option": self._handle_option_config,
            "accelerator": self._handle_accelerator_config,
            "enabled": self.set_enabled,
            "checked": self.set_checked,
            "checkable": self._handle_checkable_config,
            "icon": self._handle_icon_config,
            "icon_size": self._handle_icon_size_config,
        }

        # Treat plain text updates as logical text updates to preserve decorations
        if "text" in kwargs and "option" not in kwargs:
            kwargs["option"] = kwargs.pop("text")

        for param, value in list(kwargs.items()):
            if param in custom_handlers:
                custom_handlers[param](value)
                kwargs.pop(param)

        # Configure remaining standard parameters
        if kwargs:
            super().configure(**kwargs)

    def _handle_option_config(self, value: str) -> None:
        """Handle logical option text change and refresh display."""
        self._option_text = value
        self._refresh_display()

    def _handle_accelerator_config(self, value: str) -> None:
        """Handle accelerator configuration change."""
        self.accelerator = value
        self._refresh_display()
        if hasattr(self, 'parent_menu'):
            self._bind_accelerator()

    def _handle_checkable_config(self, value: bool) -> None:
        """Handle checkable configuration change."""
        self.checkable = value
        self._refresh_display()

    def _handle_icon_config(self, value: Union[str, PIL.Image.Image]) -> None:
        """Handle icon configuration change."""
        self.icon = value
        if value:
            self._setup_icon()

    def _handle_icon_size_config(self, value: int) -> None:
        """Handle icon configuration change."""
        self.base_icon_size = value
        if value:
            self._setup_icon()

__all__ = ["_CDMOptionButton"]
