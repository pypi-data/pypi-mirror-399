from typing import Dict, Callable, Any, List
import importlib. util
import sys
from pathlib import Path

class PluginSystem:
    
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.hooks: Dict[str, List[Callable]] = {}
    
    def register_plugin(self, name: str, plugin_class: type):
        self.plugins[name] = plugin_class()
    
    def load_plugin_from_file(self, filepath: str, plugin_name: str) -> bool:
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, filepath)
            module = importlib.util.module_from_spec(spec)
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)
            
            if hasattr(module, 'Plugin'):
                self.register_plugin(plugin_name, module.Plugin)
                return True
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}:  {e}")
            return False
        
        return False
    
    def register_hook(self, hook_name: str, callback: Callable):
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self. hooks[hook_name].append(callback)
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        results = []
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e: 
                    print(f"Hook {hook_name} error: {e}")
        return results
    
    def get_plugin(self, name: str) -> Any:
        return self.plugins.get(name, None)
    
    def list_plugins(self) -> List[str]:
        return list(self.plugins.keys())
    
    def unload_plugin(self, name:  str) -> bool:
        if name in self.plugins:
            del self.plugins[name]
            return True
        return False