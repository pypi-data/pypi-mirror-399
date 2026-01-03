from typing import Dict, Callable

class PluginSystem:
    """Plugin system for extensions"""
    
    def __init__(self):
        self.plugins: Dict[str, any] = {}
    
    def register_plugin(self, name:  str, plugin):
        self.plugins[name] = plugin
    
    def get_plugin(self, name: str):
        return self.plugins.get(name)