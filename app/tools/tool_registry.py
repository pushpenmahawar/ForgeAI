from app.tools.code_tools import CodeTools


class ToolRegistry:

    def __init__(self):
        self.code_tools = CodeTools()

    def get_tools(self):
        return [
            self.code_tools.search_code,
            self.code_tools.read_file,
            self.code_tools.find_class,
            self.code_tools.find_function,
            self.code_tools.list_files,
        ]

    def get_tool_map(self):
        return {
            "search_code": self.code_tools.search_code,
            "read_file": self.code_tools.read_file,
            "find_class": self.code_tools.find_class,
            "find_function": self.code_tools.find_function,
            "list_files": self.code_tools.list_files,
        }