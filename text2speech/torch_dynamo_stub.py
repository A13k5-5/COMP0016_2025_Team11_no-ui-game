"""
Stub for torch._dynamo to handle lazy imports
This provides dummy implementations that satisfy transformers without actually loading torch._dynamo
Since we don't use JIT/torch.compile, these functions can be no-ops
"""
import sys
from types import ModuleType


def dummy_decorator(*args, **kwargs):
    """Dummy decorator that returns the function unchanged"""
    # Handle different usage patterns:
    # 1. @disable - no args, first call returns wrapper
    # 2. @disable(recursive=False) - args/kwargs, returns wrapper
    # 3. disable(fn) - fn passed directly, return it
    # 4. disable(fn, recursive=False, reason="...") - fn + kwargs, return fn
    
    def wrapper(*wargs, **wkwargs):
        # If wrapper is called with args, first arg might be the function
        if len(wargs) >= 1 and callable(wargs[0]):
            return wargs[0]
        return wrapper
    
    # If first arg is callable and looks like a function to decorate
    if len(args) >= 1 and callable(args[0]):
        return args[0]
    
    # Otherwise, return wrapper for later decoration
    return wrapper


def dummy_function(*args, **kwargs):
    """Dummy function that does nothing"""
    pass


class DummyClass:
    """Dummy class that can be instantiated but does nothing"""
    def __init__(self, *args, **kwargs):
        pass
    
    def __call__(self, *args, **kwargs):
        return None
    
    def __getattr__(self, name):
        # Return dummy implementations for any attribute access
        return DummyClass()


# Create a module with dummy implementations
dynamo_module = ModuleType('torch._dynamo')
dynamo_module.__path__ = []  # Make it a package so submodules can be imported
dynamo_module.__package__ = 'torch._dynamo'
dynamo_module.disable = dummy_decorator
dynamo_module.allow_in_graph = dummy_decorator  
dynamo_module.assume_constant_result = dummy_decorator
dynamo_module.disallow_in_graph = dummy_decorator
dynamo_module.forbid_in_graph = dummy_decorator
dynamo_module.mark_static_address = dummy_decorator
dynamo_module.optimize = dummy_decorator
dynamo_module.run = dummy_function
dynamo_module.reset = dummy_function
dynamo_module.comptime = dummy_function

# Add any class references
dynamo_module.OptimizeContext = DummyClass
dynamo_module.CompileContext = DummyClass

# Make __getattr__ return dummy implementations for anything we missed
def module_getattr(name):
    # For introspection attributes, return appropriate values
    if name in ('__file__', '__path__', '__spec__', '__loader__', '__package__'):
        return None
    if name.startswith('_'):
        raise AttributeError(f"module 'torch._dynamo' has no attribute '{name}'")
    # For any other attribute, return a dummy class or function
    return DummyClass()

dynamo_module.__getattr__ = module_getattr

# Install in sys.modules
sys.modules['torch._dynamo'] = dynamo_module


# Create meta path finder for submodules  
class DynamoSubmoduleFinder:
    """Handles torch._dynamo.* submodule imports"""
    
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith('torch._dynamo.'):
            from importlib.machinery import ModuleSpec
            return ModuleSpec(fullname, self)
        return None
    
    def create_module(self, spec):
        # Create a dummy module
        module = ModuleType(spec.name)
        
        # Create a custom __getattr__ for this submodule
        def submodule_getattr(name):
            # For introspection attributes, return appropriate values
            if name in ('__file__', '__path__', '__spec__', '__loader__', '__package__'):
                return None
            if name.startswith('_'):
                raise AttributeError(f"module '{spec.name}' has no attribute '{name}'")
            # For any other attribute, return a dummy class
            return DummyClass()
        
        module.__getattr__ = submodule_getattr
        # Add common exports
        module.TransformGetItemToIndex = DummyClass
        return module
    
    def exec_module(self, module):
        # Module is already set up in create_module
        pass


# Install meta path finder
sys.meta_path.insert(0, DynamoSubmoduleFinder())
