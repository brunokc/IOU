from functools import wraps
from sqlalchemy import event, inspect
from sqlalchemy.orm import DeclarativeBase

# from sqlalchemy.orm import Session

def _get_type(name: str):
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def _full_name(type):
    return f"{type.__module__}.{type.__name__}" if type else "None"


# def _get_bl_wrapper_for_model(model_class):
#     if model_class.__module__.endswith("server.store.models") and issubclass(model_class, DeclarativeBase):
#         wrapper_type_name = f"server.businesslogic.{model_class.__name__.lower()}.{model_class.__name__}"
#         cls = _get_type(wrapper_type_name)

#     # print(f"item type: {_full_name(item_type)}; wrapper: {_full_name(cls)}")
#     return cls


def _get_bl_wrapper(model):
    # print(f"_get_bl_wrapper: model={model!r}")
    cls = None
    model_type = type(model)
    if model_type.__module__.endswith("server.store.models") and issubclass(model_type, DeclarativeBase):
        wrapper_type_name = f"server.businesslogic.{model_type.__name__.lower()}.{model_type.__name__}"
        cls = _get_type(wrapper_type_name)

    # print(f"_get_bl_wrapper: model type: {_full_name(model_type)}; wrapper: {_full_name(cls)}")
    return cls


def _get_model_from_bl_wrapper(bl_class):
    model_class = getattr(bl_class, "__model_class__", None)
    if not model_class:
        raise RuntimeError(f"could not detect model class name for wrapper class {bl_class.__qualname__}. "
                           f"Did you forget to add the __model_class__ class property to the wrapper?")

    return model_class

def _get_class_from_method(method):
    cls_name = method.__module__ + "." + method.__qualname__.split(".")[0]
    return _get_type(cls_name)


# def validator(func):
#     breakpoint()
#     model_cls = _get_class_from_method(func)
#     cls = _get_model_from_bl_wrapper(model_cls)

#     @event.listens_for(model_cls, "before_insert")
#     def validate_for_insert(mapper, connection, target):
#         state = inspect(target)
#         if state.modified:
#             func(cls(target))

#     @event.listens_for(model_cls, "before_update")
#     def validate_for_update(mapper, connection, target):
#         state = inspect(target)
#         if state.modified:
#             func(cls(target))

#     return func


# def transactional(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         session = kwargs.get("session") or Session()
#         is_top_level_call = "session" not in kwargs
#         try:
#             result = func(*args, session=session, **kwargs)
#             if is_top_level_call:
#                 session.commit()
#             return result
#         except Exception as e:
#             if is_top_level_call:
#                 session.rollback()
#             raise e
#         finally:
#             if is_top_level_call:
#                 session.close()
#     return wrapper


def transactional(session):
    def decorator_transactional(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with session.begin():
                result = func(*args, **kwargs)
                return result
        return wrapper
    return decorator_transactional


# from store import models
# import businesslogic

# MODEL_BL_TYPE_MAP = {
#     models.User: businesslogic.User,
#     models.Group: businesslogic.Group
# }

class AttributeDelegator:
    '''Delegates property access to the object passed in during construction

       Methods __eq__ and __repr__ were also implemented to facilitate the base
       class participating in comparisons and container presence checks.
    '''

    def __init__(self, delegated):
        # First access needs to be done via super().__setattr__() since it won't exist (and pass the
        # check in __setattr__) until after this.
        # self._delegated = delegated
        super().__setattr__("_delegated", delegated)

    def __eq__(self, other: "AttributeDelegator"):
        return self._delegated == other._delegated

    def __getattr__(self, name):
        # print(f"AttributeDelegator: getattr: name={name}")
        item = getattr(self._delegated, name)
        if isinstance(item, list):
            return ListDelegator(item)

        cls = _get_bl_wrapper(item)
        if cls:
            return cls(item)
        else:
            return item

    def __setattr__(self, name, value):
        cls = type(self)
        # Check if the attribute is a property
        if isinstance(getattr(cls, name, None), property):
            raise RuntimeError("Should I be here?")
            prop = getattr(cls, name)
            if prop.fset:
                print(f"AttributeDelegator: setting property '{name}'")
                return prop.fset(self, value)

        if name in self.__dict__:
            # Setting property on super() to avoid recursion
            # print(f"AttributeDelegator: local attrib set for '{name}'")
            return setattr(super(), name, value)

        return setattr(self._delegated, name, value)

    def __repr__(self):
        return "BL::" + repr(self._delegated)


class ListDelegator(AttributeDelegator):
    def __init__(self, delegated):
        super().__init__(delegated)

    def __len__(self):
        return len(self._delegated)

    def __getitem__(self, key):
        # print(f"ListDelegator: getitem: key={key}")
        item = self._delegated[key]
        cls = _get_bl_wrapper(item)
        if cls:
            return cls(item)
        else:
            return item

    def append(self, item):
        # Unwrap before appending, if necessary
        if isinstance(item, AttributeDelegator):
            item = item._delegated

        return self._delegated.append(item)


def get_model_changes(model):
    """
    Return a dictionary containing changes made to the model since it was
    fetched from the database.

    The dictionary is of the form {'property_name': (old_value, new_value)}

    Example:
      user = get_user_by_id(420)
      >>> '<User id=420 email="business_email@gmail.com">'
      get_model_changes(user)
      >>> {}
      user.email = 'new_email@who-dis.biz'
      get_model_changes(user)
      >>> {'email': ['business_email@gmail.com', 'new_email@who-dis.biz']}
    """
    state = inspect(model)
    changes = {}
    for attr in state.attrs:
      hist = state.get_history(attr.key, True)

      if not hist.has_changes():
        continue

      old_value = hist.deleted[0] if hist.deleted else None
      new_value = hist.added[0] if hist.added else None
      changes[attr.key] = (old_value, new_value)

    return changes
