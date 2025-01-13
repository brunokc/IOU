from functools import wraps
# from sqlalchemy.orm import Session

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


class AttributeDelegator:
    def __init__(self, delegated):
        self._delegated = delegated

    def __eq__(self, other: "AttributeDelegator"):
        return self._delegated == other._delegated

    def __getattr__(self, name):
        return getattr(self._delegated, name)

    # def __setattr__(self, name, value):
    #     if hasattr(self, name):
    #         setattr(self, name, value)
    #     else:
    #         setattr(self._delegated, name, value)

    def __repr__(self):
        return "BL::" + repr(self._delegated)
