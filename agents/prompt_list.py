import configparser
import json
import pathlib
import shutil
import sys


class PromptList:
    def __init__(self, argfile):
        self.argfile = argfile
        
        parser = ArgParser(self.argfile, section_name="agent")
        self.role = parser.get_arg("role", "str", "")
        self.goal = parser.get_arg("goal", "str", "")
        self.backstory = parser.get_arg("backstory", "str", "")

        parser_task = ArgParser(self.argfile, section_name="task")
        self.task_description = parser_task.get_arg("description", "str", "")
        self.task_expected_output = parser_task.get_arg("expected_output", "str", "")
        

class ArgParser:
    def __init__(self, argfile, section_name="prompt"):
        self.section_name = section_name
        self.argfile = argfile
        self.argparser = configparser.RawConfigParser()
        self.argparser.read(self.argfile)

    def get_arg(self, arg_name=None, arg_type='str', default=None):
        set_type = None

        try:
            arg = self.argparser.get(self.section_name, arg_name)
        except:
            arg = default
            set_type = False

        if set_type:
            if arg_type == 'str':
                arg = str(arg)
            if arg_type == 'int':
                arg = int(arg)