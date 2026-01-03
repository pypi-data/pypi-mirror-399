class CTkMenuBarError(Exception):
    """Base exception class for CTkMenuBar dropdown menu errors."""
    pass


class MenuWidgetBindingError(CTkMenuBarError):
    """Raised when menu widget binding fails."""
    pass


class MenuCommandExecutionError(CTkMenuBarError):
    """Raised when menu command execution fails."""
    pass


class MenuToggleError(CTkMenuBarError):
    """Raised when menu show/hide toggle fails."""
    pass


class MenuOptionError(CTkMenuBarError):
    """Raised when menu option operations fail."""
    pass


class MenuIconError(CTkMenuBarError):
    """Raised when menu icon loading or processing fails."""
    pass


class MenuPositioningError(CTkMenuBarError):
    """Raised when menu positioning calculations fail."""
    pass


class MenuScrollError(CTkMenuBarError):
    """Raised when scrollable menu operations fail."""
    pass
