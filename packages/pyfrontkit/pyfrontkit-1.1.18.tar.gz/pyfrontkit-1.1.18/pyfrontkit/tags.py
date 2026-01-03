# Copyright (c) 2025 Eduardo Antonio Ferrera Rodríguez
# SPDX-License-Identifier: MIT
# pyfrontkit/tags.py

from .block import Block

# ============================================================
#            BLOCK SUBCLASSES
# ============================================================

class Div(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("div", *children, **kwargs)

class Section(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("section", *children, **kwargs)

class Article(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("article", *children, **kwargs)

class Header(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("header", *children, **kwargs)

class Footer(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("footer", *children, **kwargs)

class Nav(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("nav", *children, **kwargs)

class Main(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("main", *children, **kwargs)

class Aside(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("aside", *children, **kwargs)

class Button(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("button", *children, **kwargs)

class Form(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("form", *children, **kwargs)

class Ul(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("ul", *children, **kwargs)

class Li(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("li", *children, **kwargs)

class A(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("a", *children, **kwargs)        

class Video(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("video", *children, **kwargs)

class Audio(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("audio", *children, **kwargs)

class Picture(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("picture", *children, **kwargs)

class Object(Block):
    def __init__(self, *children, **kwargs):
        super().__init__("object", *children, **kwargs)


# ============================================================
#            TRANSPARENT TEXT BLOCK
# ============================================================

class T(Block):
    """
    Transparent block for textual content.
    Compatible with ctn_* kwargs and DOM.
    Does not generate its own tag.
    """

    def __init__(self, *children, **kwargs):
        super().__init__(tag="", *children, **kwargs)

        from .content import ContentFactory
        self.content_items = ContentFactory.create_from_kwargs(**kwargs)

        # Ignore children
        self.children = []

    def _render_opening_tag(self, indent: int) -> str:
        return ""

    def _render_closing_tag(self, indent: int) -> str:
        return ""


class Label(Block):
    def __init__(self, *children, **kwargs):
        """
        Label component that abstracts the HTML <label> tag.
        Normalizes 'for_' attribute to 'for'.
        """
        if "for_" in kwargs:
            kwargs["for"] = kwargs.pop("for_")
        super().__init__("label", *children, **kwargs)

    def reveal(self, target_id, direction="top", duration="0.4s", mode="overlay"):
        """
        Reveal a target element using a checkbox-based CSS toggle.

        Rule:
        - label, checkbox and target MUST share the same parent
        """

        # 1. Setup IDs and accessibility
        check_id = f"chk_{target_id}"
        self.attrs["for"] = check_id

        if not self.attrs.get("id"):
            self.attrs["id"] = f"lbl_{target_id}"

        self.attrs.setdefault("role", "button")
        self.attrs.setdefault("tabindex", "0")

        # 2. Resolve parent (CRITICAL FIX)
        parent = self._parent
        if parent is None:
            raise RuntimeError("reveal() requires the label to have a parent container")

        # 3. Create checkbox
        from .void_element import Input

        checkbox = Input(
            type="checkbox",
            id=check_id,
            **{"aria-controls": target_id}
        )

        # 4. Insert checkbox into SAME parent as label
        #    Insert BEFORE label to preserve natural DOM flow
        try:
            idx = parent.children.index(self)
            parent.children.insert(idx, checkbox)
        except ValueError:
            parent.add_child(checkbox)

        # Ensure parent reference
        checkbox._parent = parent

        # 5. Motion presets
        moves = {
            "top": "translateY(-20px)",
            "bottom": "translateY(20px)",
            "left": "translateX(-20px)",
            "right": "translateX(20px)",
            "fade": "scale(0.95)"
        }
        transform_hidden = moves.get(direction, "none")

        # 6. CSS rules
        from .style_manager import CSS_RULES_STYLE

        target_selector = f"#{target_id}"
        checked_selector = f"#{check_id}:checked ~ {target_selector}"

        if mode == "overlay":
            hidden_css = (
                f"opacity: 0; transform: {transform_hidden}; "
                f"pointer-events: none; transition: opacity {duration} ease, "
                f"transform {duration} ease;"
            )
            visible_css = "opacity: 1; transform: translate(0,0); pointer-events: auto;"
        elif mode == "collapse":
            hidden_css = (
                f"max-height: 0; overflow: hidden; "
                f"transition: max-height {duration} ease;"
            )
            visible_css = "max-height: 1000px;"
        else:
            raise ValueError(f"Invalid reveal mode: {mode}")

        CSS_RULES_STYLE.append({target_selector: {"css": hidden_css}})
        CSS_RULES_STYLE.append({checked_selector: {"css": visible_css}})

        # 7. Hide checkbox visually (accessible)
        CSS_RULES_STYLE.append({
            f"#{check_id}": {
                "css": (
                    "position: absolute; opacity: 0; width: 0; height: 0; "
                    "pointer-events: none;"
                )
            }
        })

        # 8. Focus style for keyboard users
        CSS_RULES_STYLE.append({
            f"#{self.attrs['id']}:focus": {
                "css": "outline: 2px solid currentColor; outline-offset: 2px;"
            }
        })

        return self

# ============================================================
#            FUNCTION ALIASES FOR FREE SYNTAX
# ============================================================

def div(*children, **kwargs):
    return Div(*children, **kwargs)

def section(*children, **kwargs):
    return Section(*children, **kwargs)

def article(*children, **kwargs):
    return Article(*children, **kwargs)

def header(*children, **kwargs):
    return Header(*children, **kwargs)

def footer(*children, **kwargs):
    return Footer(*children, **kwargs)

def nav(*children, **kwargs):
    return Nav(*children, **kwargs)

def main(*children, **kwargs):
    return Main(*children, **kwargs)

def aside(*children, **kwargs):
    return Aside(*children, **kwargs)

def button(*children, **kwargs):
    return Button(*children, **kwargs)

def form(*children, **kwargs):
    return Form(*children, **kwargs)

def ul(*children, **kwargs):
    return Ul(*children, **kwargs)

def li(*children, **kwargs):
    return Li(*children, **kwargs)

def a(*children, **kwargs):
    return A(*children, **kwargs)

def video(*children, **kwargs):
    return Video(*children, **kwargs)

def audio(*children, **kwargs):
    return Audio(*children, **kwargs)

def picture(*children, **kwargs):
    return Picture(*children, **kwargs)

def object(*children, **kwargs):
    return Object(*children, **kwargs)

def t(*children, **kwargs):
    return T(*children, **kwargs)

def label(*children, **kwargs):
    return Label(*children, **kwargs)
