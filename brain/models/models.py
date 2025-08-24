# brain/models/models.py

from .runs import BrainRun, BrainRunEvent

__all__ = ["BrainRun", "BrainRunEvent"]
# what does the line above do? this line defines the public API of the models module, specifying which classes should be accessible when the module is imported.
# It helps in organizing and controlling the exposure of model classes to other parts of the application.
# __all__ is a special variable in Python that defines the public interface of a module. When you use from module import *, only the names listed in __all__ will be imported.