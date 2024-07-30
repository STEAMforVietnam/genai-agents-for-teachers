import configparser
import json
import pathlib
import shutil
import sys


class PromptList:
    def __init__(self, argfile):
        self.argfile = argfile
        parser = ArgParser(self.argfile, section_name="prompt")

        self.orchestrator_role = parser.get_arg("orchestrator_role", "str", "")
        self.orchestrator_goal = parser.get_arg("orchestrator_goal", "str", "")
        self.orchestrator_backstory = parser.get_arg("orchestrator_backstory", "str", "")

        self.orchestrator_task_description = parser.get_arg("orchestrator_task_description", "str", "")
        self.orchestrator_task_expected_output = parser.get_arg("orchestrator_task_expected_output", "str", "")

        self.matrix_creator_role = parser.get_arg("matrix_creator_role", "str", "")
        self.matrix_creator_goal = parser.get_arg("matrix_creator_goal", "str", "")
        self.matrix_creator_backstory = parser.get_arg("matrix_creator_backstory", "str", "")

        self.matrix_creator_task_description = parser.get_arg("matrix_creator_task_description", "str", "")
        self.matrix_creator_task_expected_output = parser.get_arg("matrix_creator_task_expected_output", "str", "")

        self.matrix_checker_role = parser.get_arg("matrix_checker_role", "str", "")
        self.matrix_checker_goal = parser.get_arg("matrix_checker_goal", "str", "")
        self.matrix_checker_backstory = parser.get_arg("matrix_checker_backstory", "str", "")

        self.matrix_checker_task_description = parser.get_arg("matrix_checker_task_description", "str", "")
        self.matrix_checker_task_expected_output = parser.get_arg("matrix_checker_task_expected_output", "str", "")

        self.test_creator_role = parser.get_arg("test_creator_role", "str", "")
        self.test_creator_goal = parser.get_arg("test_creator_goal", "str", "")
        self.test_creator_backstory = parser.get_arg("test_creator_backstory", "str", "")

        self.test_assignment_task_description = parser.get_arg("test_assignment_task_description", "str", "")
        self.test_assignment_task_expected_output = parser.get_arg("test_assignment_task_expected_output", "str", "")

        self.topic = parser.get_arg("topic", "str", "")
        self.rnge = parser.get_arg("rnge", "str", "")
        self.sub_topics = parser.get_arg("sub_topics", "str", "")
        self.students = parser.get_arg("students", "str", "")
        

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


