class Lessons:
    """Educational lessons"""
    
    def __init__(self):
        self.lessons = {}
    
    def get_lesson(self, level: str, topic: str):
        return f"Lesson:  {level} - {topic}"