import logging
import datetime
import typing as t
from io import StringIO
from markupsafe import Markup
from numbers import Number as _Number
from inspect import isfunction, ismethod
from starlette.responses import HTMLResponse
from typing_extensions import Self, is_typeddict
from types import BuiltinFunctionType, BuiltinMethodType, FunctionType, MethodType

log = logging.getLogger("starlette_templates.hypertext")


# Protocol for objects with _repr_html_ method (like Jupyter displayable objects)
# Protocol is structural typing ("duck typing" at the type level) to define a contract that
# specifies what methods or attributes an object must have, without requiring inheritance.
class _ReprHtml(t.Protocol):
    def _repr_html_(self) -> str: ...


# Protocol for objects with get_element method (custom renderable objects)
class _GetElement(t.Protocol):
    def get_element(self) -> "Element": ...


# Protocol for Pydantic models (objects with model_dump method)
class _PydanticModel(t.Protocol):
    def model_dump(self) -> t.Dict[str, t.Any]: ...


# Type for element children - covers all supported child types
ElementChild = t.Union[
    str,  # String content
    bytes,  # Bytes (decoded to UTF-8)
    _Number,  # Numbers (int, float, etc.)
    datetime.date,  # Date objects
    datetime.datetime,  # Datetime objects
    datetime.timedelta,  # Timedelta objects
    t.Callable[[], "ElementChild"],  # Functions/methods (evaluated lazily)
    "Element",  # Other Element instances
    t.Dict[str, t.Any],  # Attribute dictionaries (including TypedDict)
    _PydanticModel,  # Pydantic models with model_dump() method
    _ReprHtml,  # Objects with _repr_html_ method
    _GetElement,  # Objects with get_element method
    t.Iterable["ElementChild"],  # Iterables of children
    t.Any,  # Fallback: any object that can be coerced to string
    None,  # None values (ignored)
]

# fmt: off
SELF_CLOSING_TAGS = set(["meta", "link", "img", "br", "hr", "input", "area", "base", "col", "embed", "command", 
    "keygen", "param", "source", "track", "wbr", "menuitem", "basefont", "bgsound", "frame", "isindex", "nextid",
    "spacer", "acronym", "applet", "big", "blink", "center", "content", "dir", "element",
    "font", "frameset", "image", "listing", "marquee", "multicol", "nobr",
])
# fmt: on


def _is_function(x: object) -> bool:
    """Return True if x is a function or method."""
    return (
        isinstance(x, (FunctionType, MethodType, BuiltinFunctionType, BuiltinMethodType))
        or ismethod(x)
        or isfunction(x)
    )


def _listify(obj: t.Any) -> t.List[t.Any]:
    """Convert an object to a list."""
    if obj is None:
        return []
    if isinstance(obj, list):
        return obj
    if isinstance(obj, tuple):
        return list(obj)
    if isinstance(obj, dict):
        return list(obj.values())
    if isinstance(obj, set):
        return list(obj)
    return [obj]


def _stringify(value: t.Any, sep: str = " ") -> str:
    """Turn a value or list of values into a string."""
    if isinstance(value, list):
        return sep.join(str(v) for v in _flatten(value))
    return str(value)


def _flatten(lst: t.List[t.Any]) -> t.List[t.Any]:
    """Flatten a list of lists."""
    if lst is None:
        return []
    if isinstance(lst, str):
        return [lst]
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(_flatten(item))
        else:
            if item is not None:
                result.append(item)
    return result


def _flatten_and_dedupe(lst: t.List[t.Any]) -> t.List[str]:
    """Flatten a list of lists and remove duplicates efficiently using iterative approach with set."""
    if lst is None:
        return []
    if isinstance(lst, str):
        return [lst]

    seen = set()
    result = []
    stack = [lst]

    while stack:
        current = stack.pop()
        if isinstance(current, str):
            if current not in seen and current is not None:
                seen.add(current)
                result.append(current)
        elif isinstance(current, (list, tuple)):
            # Add items in reverse order to maintain original order
            for item in reversed(current):
                stack.append(item)
        else:
            if current is not None and current not in seen:
                current_str = str(current)
                if current_str not in seen:
                    seen.add(current_str)
                    result.append(current_str)

    return result


# Attribute compilation cache - use regular dict with size limit to prevent memory leaks
_attr_cache: t.Dict[t.Tuple, str] = {}
_CACHE_SIZE_LIMIT = 1000


def _compile_attribute(key: str, value: t.Any) -> str:
    """
    Compile a single attribute key-value pair into an HTML attribute string.

    Args:
        key: Attribute name
        value: Attribute value

    Returns:
        Compiled attribute string (without leading space)
    """
    # Handle special attribute name transformations
    if key == "for_":
        key = "for"

    # Convert underscores to dashes
    key = key.replace("_", "-")

    # Handle boolean attributes
    if isinstance(value, bool):
        return key if value else ""

    # Skip None values
    if value is None:
        return ""

    # Convert value to string
    if isinstance(value, (list, tuple)):
        value = _stringify(value)
    elif not isinstance(value, str):
        value = str(value)

    # Handle quote selection
    if '"' in value:
        return f"{key}='{value}'"
    else:
        return f'{key}="{value}"'


def _compile_attributes_fast(attrs: t.Mapping, element_id: t.Optional[int] = None) -> str:
    """
    Fast attribute compilation with caching for immutable attributes.

    Args:
        attrs: Attribute dictionary
        element_id: Optional element ID for caching

    Returns:
        Compiled attribute string with leading space if non-empty
    """
    if not attrs:
        return ""

    # Check cache first if element_id provided
    cache_key = None
    if element_id is not None:
        # Create a cache key from immutable attributes
        immutable_attrs = {}
        has_functions = False

        for k, v in attrs.items():
            if k == "classes":
                continue  # Classes handled separately
            # Skip private attributes
            if k.startswith("_"):
                continue
            if _is_function(v):
                has_functions = True
                break
            # Only cache simple hashable types to avoid cache key issues
            if isinstance(v, (str, int, float, bool, type(None))):
                immutable_attrs[k] = v

        if not has_functions and immutable_attrs:
            cache_key = tuple(sorted(immutable_attrs.items()))
            if cache_key in _attr_cache:
                cached_result = _attr_cache[cache_key]
                # Still need to handle classes separately
                if "classes" in attrs:
                    class_attr = _compile_class_attribute(attrs["classes"])
                    if class_attr:
                        if cached_result:
                            return f" {class_attr} {cached_result}"
                        else:
                            return f" {class_attr}"
                return f" {cached_result}" if cached_result else ""

    # Fast compilation using list join
    compiled_parts = []

    # Handle classes first
    if "classes" in attrs:
        class_attr = _compile_class_attribute(attrs["classes"])
        if class_attr:
            compiled_parts.append(class_attr)

    # Handle other attributes
    for k, v in attrs.items():
        if k == "classes":
            continue  # Already handled

        # Skip private attributes (those starting with underscore)
        if k.startswith("_"):
            continue

        # Handle style dict specially
        if k == "style" and isinstance(v, dict):
            v = "; ".join([f"{k}: {_stringify(v)}" for k, v in v.items()])

        # Evaluate functions
        if _is_function(v):
            try:
                v = v()  # type: ignore
            except Exception:
                log.error("Error evaluating function: %r" % v, exc_info=True)
                continue

        compiled_attr = _compile_attribute(k, v)
        if compiled_attr:
            compiled_parts.append(compiled_attr)

    result = " ".join(compiled_parts)

    # Cache immutable result if possible
    if cache_key is not None and "classes" not in attrs:
        # Implement simple cache size limit to prevent memory leaks
        if len(_attr_cache) >= _CACHE_SIZE_LIMIT:
            # Clear oldest entries (simple strategy)
            _attr_cache.clear()
        _attr_cache[cache_key] = result

    return f" {result}" if result else ""


def _compile_class_attribute(classes) -> str:
    """Compile class attribute value into HTML class string."""
    if not classes:
        return ""

    klass = [classes]
    if _is_function(klass[0]):
        klass[0] = klass[0]()

    if len(klass) > 0:
        class_value = " ".join(_flatten_and_dedupe(klass))
        if class_value:
            return f'class="{class_value}"'

    return ""


def _merge_dicts(*dicts: dict) -> dict:
    result = {}
    for d in dicts:
        for k, v in d.items():
            if k in result:  # found pre-existing key
                if isinstance(v, dict):
                    result[k] = _merge_dicts(result[k], v)
                else:
                    # new value is a list so convert the existing value to a list if it isn't already
                    if not isinstance(result[k], list):
                        result[k] = _listify(result[k])
                    # then extend the list with the new value
                    result[k].extend(_listify(v))
            else:
                result[k] = v
    return result


def _classes_ensure_list(classes: t.Union[str, t.Callable, t.List[str]]) -> t.List[str]:
    """
    Users can pass a string, a list of strings, or a function that returns a string or list of strings. This function
    ensures that the classes attribute is always a list of strings.
    """
    value = classes
    if _is_function(value):
        value = value()  # type: ignore
    if isinstance(value, str):
        return value.split()
    if isinstance(value, list):
        return value
    return _listify(value)


class Element:
    """
    Base class for all elements.

    Attributes:
        tag (str): The tag name of the element.
        children (list): List of child elements.
        attributes (dict): Dictionary of attributes for the element.
    """

    def __init__(self, *args, **kwargs) -> None:
        self.tag: str = "div"
        """The tag name of the element."""
        self.children = []
        """List of children elements."""
        self.attributes = {}
        """Dictionary of attributes."""
        # Add children
        if args:
            self.__add__(args)
        # Add attributes
        if kwargs:
            if "classes" in kwargs:
                classes = kwargs.pop("classes")
                self.attributes["classes"] = _classes_ensure_list(classes)
            self.attributes.update(kwargs)

    def __add__(self, other: ElementChild) -> Self:
        """Add children or attributes to the element using the + operator."""
        if isinstance(other, dict):
            self.set_attrs(**other)  # type: ignore
            return self
        other = _listify(other)
        num_t = (_Number, datetime.date, datetime.datetime, datetime.timedelta)
        for obj in other:
            # None
            if obj is None:
                continue
            # Number, Date, Datetime, timedelta
            if isinstance(obj, num_t):
                obj = str(obj)
            # String
            if isinstance(obj, str):
                self.children.append(obj)
            # bytes
            elif isinstance(obj, bytes):
                self.children.append(obj.decode("utf-8"))
            # Dict and TypeDict are treated as attributes
            # note: is_typeddict(obj) is available in Python 3.10+
            elif isinstance(obj, dict) or is_typeddict(obj):
                self.set_attrs(**obj)
            # Element
            elif isinstance(obj, Element):
                self.children.append(obj)
            # Renderable as an element-like object, e.g. Element, str, etc. This
            # is usually a class with a get_element method
            elif hasattr(obj, "get_element"):
                self.children.append(obj)
            # Pydantic model (check AFTER get_element, since some models have get_element)
            elif hasattr(obj, "model_dump"):
                self.set_attrs(**obj.model_dump())
            # Rich display: https://ipython.readthedocs.io/en/stable/config/integrating.html#rich-display
            elif hasattr(obj, "_repr_html_"):
                self.children.append(obj._repr_html_())
            # Iterable
            elif hasattr(obj, "__iter__"):
                for subobj in obj:
                    self.__add__(subobj)
            # Function or method
            elif _is_function(obj):
                # function is evaluated when rendered
                self.children.append(obj)
            # Unknown
            else:
                log.debug(
                    "%r not an `Element` or string (type %s). Coercing to string." % (obj, type(obj)),
                )
                try:
                    # try to coerce to string
                    self.children.append(str(obj))
                except Exception:
                    raise TypeError(
                        f"Failed to add type {type(obj)} as a child. "
                        "Only `Element`, str, and iterables of these are allowed."
                    )
        return self

    def __iadd__(self, other: ElementChild) -> Self:
        """
        Add children to this element with += operator. Returns the left element.

        Args:
            other: The children to add to the element. Can be a string, number, list, tuple, dict, Element,
                or any class that defines a get_element method.

        Examples:

            Add children to an element using the += operator.

            ```python
            form = ht.form()
            form += ht.input(type="text", name="name")
            form += ht.button(type="submit")
            ```
        """
        self.__add__(other)
        return self

    def set_attrs(self, **kwargs) -> Self:
        """
        Set attributes for the element. If there are duplicate keys, use the last value. `classes` key is merged into
        a single classes list.

        Args:
            **kwargs: Attributes to set for the element.
        """
        if "classes" in kwargs:
            classes = kwargs.pop("classes")
            self.add_classes(classes)
        self.attributes.update(kwargs)
        return self

    def merge_attrs(self, **kwargs) -> Self:
        """
        Merge attributes with the existing attributes. If there are duplicate keys, combine them into a list.

        Args:
            **kwargs: Attributes to merge with the existing attributes.

        Examples:

            Merge attributes with an element.

            ```python
            ht.div(classes=["container"]).merge_attrs(id="my-div", classes=["content"])
            ```
        """
        if "classes" in kwargs:
            classes = kwargs.pop("classes")
            self.add_classes(classes)
        self.attributes = _merge_dicts(self.attributes, kwargs)
        return self

    def has_classes(self, *classes: str) -> bool:
        """
        Check if the element has all of the given classes.

        Args:
            *classes (str): The classes to check for.

        Returns:
            bool: True if the element has all of the given classes, False otherwise.
        """
        element_classes = self.attributes.get("classes", [])
        if _is_function(element_classes):
            element_classes = element_classes()
        element_classes = _flatten(element_classes)
        element_classes = [str(c) for c in element_classes]
        return all(str(c) in element_classes for c in classes)

    def add_classes(self, *classes: str) -> Self:
        """
        Add classes to the element.

        Args:
            *classes (str): The classes to add to the element.

        Returns:
            Element: The element with the added classes.

        Examples:

            Add classes to an element.

            ```python
            ht.div().add_classes("container", "row")
            ```
        """
        current_classes = self.attributes.get("classes", [])
        current_classes = _classes_ensure_list(current_classes)
        new_classes = current_classes + list(classes)
        self.attributes["classes"] = _flatten_and_dedupe(new_classes)
        return self

    def remove_classes(self, *classes: str) -> Self:
        """
        Remove classes from the element.

        Args:
            *classes (str): The classes to remove from the element.

        Returns:
            Element: The element with the removed classes.

        Examples:

            Remove classes from an element.

            ```python
            ht.div().remove_classes("container", "row")
            ```
        """
        current_classes = self.attributes.get("classes", [])
        current_classes = _classes_ensure_list(current_classes)
        # Convert to set for efficient removal, then back to list preserving order
        classes_to_remove = set(classes)
        filtered_classes = [c for c in _flatten(current_classes) if c not in classes_to_remove]
        # Use set to deduplicate while preserving order
        seen = set()
        dedupe_classes = []
        for c in filtered_classes:
            if c not in seen:
                seen.add(c)
                dedupe_classes.append(c)
        self.attributes["classes"] = dedupe_classes
        return self

    def __call__(self, *args: ElementChild, **kwargs) -> Self:
        """
        Add children or attributes to the element.

        Args:
            *args: Children elements.
            **kwargs: Attributes.

        Returns:
            Element: The element with the added children and attributes.

        Examples:

            Add children and attributes to an element.

            ```python
            ht.div("Hello")("World", style="color: red;")
            ```
        """
        self.__add__(args)
        self.set_attrs(**kwargs)
        return self

    def append(self, *args: ElementChild) -> Self:
        """
        Add children to the element.

        Args:
            *args: Children elements.

        Returns:
            Element: The element with the added children.

        Examples:

            Add children to an element.

            ```python
            ht.div().append("Hello world")
            ```
        """
        self.__add__(args)
        return self

    def extend(self, *args: ElementChild) -> Self:
        """
        Add children to the element.

        Args:
            *args: Children elements.

        Returns:
            Element: The element with the added children.

        Examples:

            Add children to an element.

            ```python
            ht.div().extend("Hello", "world")
            ```
        """
        for arg in args:
            self.__add__(arg)
        return self

    def insert(self, index: int, *args: ElementChild) -> Self:
        """
        Insert children at the given index.

        Args:
            index (int): The index at which to insert the
            *args: Children elements.

        Returns:
            Element: The element with the inserted children

        Examples:

            Insert children at a specific index.

            ```python
            ht.div("World").insert(0, "Hello")
            ```
        """
        self.children.insert(index, *args)
        return self

    def to_string(self) -> str:
        """
        Return the HTML element as a string.

        Returns:
            (str): The HTML element as a string.

        Examples:

            Convert an element to a string.

            ```python
            ht.div("Hello world").to_string()
            # '<div>Hello world</div>'
            ```
        """
        return ht.render_element(self)

    def render(self) -> Markup:
        """
        Return the HTML element as a string.

        Returns:
            (Markup): The HTML element as a Markup string.
        """
        return Markup(self.to_string())

    def pipe(self, function: t.Callable, *args, **kwargs) -> Self:
        """
        A structured way to apply a sequence of user-defined functions.

        Args:
            function (Callable): The function to apply to the element.
            *args: Positional arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            The result of the function.

        Examples:

            Apply a function to an element.

            ```python
            def add_classes(element, prefix: str):
                elment.add_classes(f"{prefix}-class")
                return element

            ht.div("Hello world").pipe(add_classes, "my-prefix")
            ```
        """
        return function(self, *args, **kwargs)

    def __str__(self) -> str:
        """
        Return the HTML element as a string.

        Returns:
            (str): The HTML element as a string.
        """
        return self.to_string()

    def _repr_html_(self) -> str:
        """
        Return the HTML element as a string for Jupyter notebooks.
        https://ipython.readthedocs.io/en/stable/config/integrating.html#rich-display
        """
        return self.to_string()


class _MetaTagType(type):
    def __getattr__(self, __name: str) -> Element:
        """Return a new instance of ht with the given tag name."""
        el = Element()
        el.tag = __name
        return el


class ht(metaclass=_MetaTagType):
    """
    HTML factory class.

    This class is used to create HTML elements in a Pythonic way. It is a factory class that returns an Element, so you
    can call it with the tag name and any attributes or children you want to add to the element and it will return an
    Element instance.

    Examples:

        Generate HTML elements using the ht class:

        ```python
        ht.div(id="my-div", classes=["container", "content"], style={"color": "red"})
        ht.button(type="submit", classes=["btn", "btn-primary"])
        ht.h1("Hello World")
        ```
    """

    def __call__(self, tag, *args: ElementChild, **kwds: t.Any) -> Element:
        el = Element(*args, **kwds)
        el.tag = tag
        return el

    @classmethod
    def render_element(cls, element: t.Union[Element, str, None]) -> str:
        """
        Return the HTML element as a string.
        """
        if _is_function(element):
            element = element()  # type: ignore

        # In the event that the returned value is a function, method, or coroutine
        # then recursively call ht.render_element until we get a string
        if _is_function(element):
            element = ht.render_element(element)

        # `get_element` is a special method that can be implemented by classes and
        # should return an Element
        if hasattr(element, "get_element"):
            if _is_function(element.get_element):  # type: ignore
                element = element.get_element()  # type: ignore

        if element is None:
            return ""

        if isinstance(element, (str, _Number, bool)):
            return str(element)

        if not isinstance(element, Element):
            raise TypeError(
                f"element must be an instance of `Element` or str or have a `get_element` method that returns an instance of `Element`, got type {type(element)}: {element}"
            )

        tag: str = element.tag
        attrs: t.Mapping = element.attributes
        children: t.List = element.children

        # replace underscores with dashes in tag name
        tag = tag.replace("_", "-")
        # parse attributes using optimized compilation
        attrs_str = _compile_attributes_fast(attrs, id(element) if attrs else None)
        if tag in SELF_CLOSING_TAGS:
            # self-closing tags have no children
            return f"<{tag}{attrs_str}/>"
        else:
            # process non-self-closing tags
            if children is None:
                innerHTML = ""
            elif isinstance(children, (str, _Number, bool)):
                innerHTML = str(children)
            elif isinstance(children, Element):  # ht class instance
                try:
                    innerHTML = ht.render_element(children)
                except Exception:
                    log.error("Error rendering element: %r" % children, exc_info=True)
                    innerHTML = ""
            elif hasattr(children, "get_element"):
                # Any class instance with a get_element method
                innerHTML = children.get_element()  # type: ignore
            elif _is_function(children):
                # evaluate function and render the result
                try:
                    result = children()  # type: ignore
                    innerHTML = str(result)
                except Exception:
                    log.error("Error evaluating function: %r" % children, exc_info=True)
                    innerHTML = ""
            elif isinstance(children, (list, tuple)):
                child_buffer = StringIO()
                for child in children:
                    child_buffer.write(ht.render_element(child))
                innerHTML = child_buffer.getvalue()
            else:
                innerHTML = ""
            return f"<{tag}{attrs_str}>{innerHTML}</{tag}>"

    @classmethod
    def render_document(
        cls,
        body: Element,
        head: t.Optional[t.List[Element]] = None,
        title: t.Optional[str] = None,
        body_kwargs: t.Optional[dict] = None,
        head_kwargs: t.Optional[dict] = None,
        html_kwargs: t.Optional[dict] = None,
    ) -> str:
        """
        Render a full HTML document.

        Args:
            body (Element): Document body.
            head (list[Element]): A list of elements to include in the head tag.
            title (str): Document title.
            body_kwargs (dict): Body tag attributes.
            head_kwargs (dict): Head tag attributes.
            html_kwargs (dict): HTML tag attributes.

        Returns:
            The HTML document as a string.

        Examples:

            Render an HTML document.

            ```python
            ht.render_document(ht.div("Hello world"))
            # <!DOCTYPE html><html><head>...</head><body><div>Hello world</div></body></html>
            ```
        """
        if not isinstance(body, (Element, str)):
            if not hasattr(body, "get_element"):
                raise TypeError(
                    "body must be an instance of `Element` or str or have a `get_element` method that returns an `Element` element"
                )

        head = head or []
        body_kwargs = body_kwargs or {}
        head_kwargs = head_kwargs or {}
        html_kwargs = html_kwargs or {}

        if not isinstance(head, list):
            raise TypeError("head must be a list of `Element` elements")

        _head = [
            ht.meta(charset="utf-8"),
            ht.meta(name="viewport", content="width=device-width, initial-scale=1"),
            ht.meta(http_equiv="X-UA-Compatible", content="IE=edge"),
        ]
        _head.extend(head)
        if title is not None:
            _head.append(ht.title(title))
        html = [
            "<!DOCTYPE html>",
            ht.render_element(
                ht.html(
                    ht.head(_head, **head_kwargs),
                    ht.body(body, **body_kwargs),
                    **html_kwargs,
                )
            ),
        ]
        return "".join(html)


def _get_selector_type(selector: str) -> str:
    """
    Determine the type of CSS selector.

    Returns one of: 'at-rule', 'parent-ref', 'pseudo', 'attribute', 'combinator', 'regular'
    """
    if selector.startswith("@"):
        return "at-rule"
    elif selector.startswith("&"):
        return "parent-ref"
    elif selector.startswith(":"):
        return "pseudo"
    elif selector.startswith("[") and selector.endswith("]"):
        return "attribute"
    elif selector.startswith((">", "+", "~")):
        return "combinator"
    else:
        return "regular"


def _combine_selectors(parent: str, child: str) -> str:
    """
    Combine parent and child selectors based on the child selector type.
    """
    selector_type = _get_selector_type(child)

    if selector_type == "at-rule":
        # At-rules don't combine with parent
        return child
    elif selector_type == "parent-ref":
        # Replace & with parent
        return parent + child[1:]
    elif selector_type == "pseudo":
        # Append directly to parent (no space)
        return parent + child
    elif selector_type == "attribute":
        # Append directly to parent (no space)
        return parent + child
    elif selector_type == "combinator":
        # Add space before combinator
        return f"{parent} {child}"
    else:
        # Regular selector - add space
        return f"{parent} {child}"


def dict2css(style: t.Mapping[str, t.Any], parent_selector: str = "") -> str:
    """
    Convert a dict to a CSS string with support for nested selectors.

    Args:
        style (Mapping[str, Any]): A dict where keys are CSS selectors and values can be:
            - str: Raw CSS properties
            - dict: CSS properties or nested selectors
        parent_selector (str): Parent selector for nested rules (internal use)

    Returns:
        str: The CSS string.

    Examples:

        Convert a dict to a CSS string:

        ```python
        dict2css({"body": {"background-color": "red", "color": "white"}})
        # 'body{background-color:red;color:white;}'

        dict2css({"body": "background-color: red;"})
        # 'body{background-color: red;}'

        # Nested selectors with various types
        dict2css({
            ".card": {
                "padding": "10px",
                ".title": {                    # Regular nested
                    "font-size": "20px"
                },
                ":hover": {                    # Pseudo-class
                    "background": "#f0f0f0"
                },
                "::before": {                  # Pseudo-element
                    "content": "'*'"
                },
                "[data-active]": {             # Attribute
                    "border": "1px solid green"
                },
                "> .child": {                  # Child combinator
                    "margin": "5px"
                },
                "+ .sibling": {                # Adjacent sibling
                    "color": "blue"
                },
                "&.active": {                  # Parent reference
                    "font-weight": "bold"
                }
            }
        })
        ```
    """
    css_buffer = StringIO()

    for selector, properties in style.items():
        # Handle string values (raw CSS)
        if isinstance(properties, str):
            if parent_selector:
                # Inside a parent, treat as property
                css_buffer.write(f"{selector}:{properties};")
            else:
                # Top level, treat as selector with raw CSS
                css_buffer.write(f"{selector}{{{properties}}}")
            continue

        # Handle dict values
        if isinstance(properties, dict):
            # Check if this is a nested selector or properties
            has_nested_selectors = False
            css_properties = []
            nested_rules = {}

            for key, value in properties.items():
                if isinstance(value, dict):
                    # This is a nested selector
                    has_nested_selectors = True
                    nested_rules[key] = value
                else:
                    # This is a CSS property
                    css_properties.append((key, value))

            # Build the current selector
            if parent_selector:
                current_selector = _combine_selectors(parent_selector, selector)
            else:
                current_selector = selector

            # Output CSS properties for current selector
            if css_properties:
                prop_buffer = StringIO()
                for prop, value in css_properties:
                    if isinstance(value, str) and value.endswith("}"):
                        prop_buffer.write(f"{prop}:{value}")
                    else:
                        prop_buffer.write(f"{prop}:{value};")
                css_buffer.write(f"{current_selector}{{{prop_buffer.getvalue()}}}")

            # Process nested selectors
            if has_nested_selectors:
                if selector.startswith("@"):
                    # For at-rules, wrap the content
                    nested_css = dict2css(nested_rules, "")
                    css_buffer.write(f"{selector}{{{nested_css}}}")
                else:
                    # Regular nested selectors
                    css_buffer.write(dict2css(nested_rules, current_selector))

    return css_buffer.getvalue()


class Document(Element):
    """HTML document that can be used as an ASGI application.

    This class is a subclass of Element and can be used to create an HTML document. It can also be used to return an
    HTML response in an ASGI application.

    Args:
        page_title (str, optional): The title of the page. Defaults to None.
        headers (Mapping[str, Any], optional): Response headers. Defaults to None.
        status_code (int, optional): Response status code. Defaults to 200.
        *args: Children elements.
        **kwargs: Attributes.

    Attributes:
        page_title (str): The title of the page.
        headers (dict): Response headers.
        status_code (int): Response status code.
        title (Element): The title element.
        head (Element): The head element.
        body (Element): The body element.
        html (Element): The html element.
    """

    def __init__(
        self,
        *args,
        page_title: t.Optional[str] = None,
        headers: t.Optional[t.Mapping[str, t.Any]] = None,
        status_code: int = 200,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.page_title: t.Optional[str] = page_title
        self.headers: t.Optional[t.Mapping[str, t.Any]] = headers
        """Response headers."""
        self.status_code: int = status_code
        """Response status code."""
        self.title = ht.title()
        """Document title."""
        self.head: Element = ht.head(
            ht.meta(charset="utf-8"),
            ht.meta(name="viewport", content="width=device-width, initial-scale=1"),
            ht.meta(http_equiv="X-UA-Compatible", content="IE=edge"),
            self.title,
        )
        """The head element."""
        self.body = ht.body()
        """The body element."""
        self.html = ht.html(self.head, self.body)
        """The html element."""

    def get_element(self) -> Element:
        """
        Return the document as an Element, starting with the `<html>` tag.

        Returns:
            Element: The document as an Element.
        """
        self.title.children = [self.page_title]
        self.body.children = self.children
        self.body.attributes = self.attributes
        return self.html

    def to_string(self) -> str:
        """Return the HTML document as a string."""
        doc = super().to_string()
        return "<!DOCTYPE html>" + doc

    async def __call__(self, scope, receive, send):
        """
        ASGI application interface for Starlette and FastAPI.
        This method allows the Document class to be used as an ASGI application,
        enabling it to return an HTML response when called.

        Args:
            scope (dict): ASGI scope dictionary.
            receive (callable): ASGI receive callable.
            send (callable): ASGI send callable.

        Examples:

            Use the Document class as an ASGI application in a Starlette or FastAPI app.

            ```python
            from starlette.applications import Starlette
            from starlette.routing import Route
            from pypertext import Document
            async def homepage(request):
                doc = Document(page_title="My Page")
                doc.body += "Hello, World!"
                return doc
            app = Starlette(routes=[Route("/", homepage)])
            ```
        """
        assert scope["type"] == "http"

        response = HTMLResponse(self.to_string(), headers=self.headers, status_code=self.status_code)
        await response(scope, receive, send)