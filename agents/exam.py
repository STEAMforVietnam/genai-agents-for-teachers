import json
from crewai import Agent, Task, Crew, Process
from agents.base import CustomCrew
from tools.exam import ExamTool
from agents.custom_tools import create_exam_html_maker_tool
from crewai_tools.tools.json_search_tool.json_search_tool import JSONSearchTool
from crewai_tools.tools.file_read_tool.file_read_tool import FileReadTool
from .models import ExamJSON
from agents.prompt_list import PromptList


class ExamCrew(CustomCrew):
    def __init__(self, 
                 creator_prompt=PromptList('./prompts/prompt_list_test_creator.txt'),
                 orchestrator_prompt=PromptList('./prompts/prompt_list_test_orchestrator.txt'),
                 checker_prompt=PromptList('./prompts/prompt_list_test_checker.txt'),
                 html_creator_prompt=PromptList('./prompts/prompt_list_test_html_creator.txt')):
        super(ExamCrew, self).__init__(
            creator_prompt, orchestrator_prompt,
            checker_prompt, html_creator_prompt)
        self.project = "TẠO_ĐỀ_BÀI_THI"

    def _get_tools(self):
        super()._get_tools()
        ### ADD JSONParserTool
        self.tools.append(JSONSearchTool('./outputs/matrix.json')) 

        ### ADD HTMLMakerTool
        self.tools.append(create_exam_html_maker_tool)


    def _get_crew(self):
        orchestrator = self._create_orchestrator_agent()
        exam_generator = self._create_exam_generator_agent()
        checker = self._create_checker_agent()
        exam_html_creator = self._create_exam_html_creator_agent()

        self.orchestrator_task = self._create_orchestrator_task(orchestrator)
        self.exam_generator_task = self._create_exam_generator_task(exam_generator)
        self.checker_task = self._create_checker_task(checker)
        exam_html_creator_task = self._create_exam_html_creator_task(exam_html_creator)

        return Crew(
            agents=[orchestrator, exam_generator, checker, exam_html_creator],
            tasks=[self.orchestrator_task, self.exam_generator_task, self.checker_task, exam_html_creator_task],
            memory=True,
            verbose=2,
            planning=True
        )

    def _create_orchestrator_agent(self):
        test_orchestrator_role = self.orchestrator_prompt.role
        test_orchestrator_goal = self.orchestrator_prompt.goal
        test_orchestrator_backstory = self.orchestrator_prompt.backstory
        return Agent(
            role=test_orchestrator_role,
            goal=test_orchestrator_goal,
            backstory=test_orchestrator_backstory,
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=5
        )

    def _create_exam_generator_agent(self):
        test_creator_role = self.creator_prompt.role
        test_creator_goal = self.creator_prompt.goal
        test_creator_backstory = self.creator_prompt.backstory
        return Agent(
            role=test_creator_role,
            goal=test_creator_goal,
            backstory=test_creator_backstory,
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=10
        )

    def _create_checker_agent(self):
        test_checker_role = self.checker_prompt.role
        test_checker_goal = self.checker_prompt.goal
        test_checker_backstory = self.checker_prompt.backstory
        return Agent(
            role=test_checker_role,
            goal=test_checker_goal,
            backstory=test_checker_backstory,
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            max_iter=5
        )

    def _create_exam_html_creator_agent(self):
        test_html_creator_role = self.html_creator_prompt.role
        test_html_creator_goal = self.html_creator_prompt.goal
        test_html_creator_backstory = self.html_creator_prompt.backstory
        return Agent(
            role=test_html_creator_role,
            goal=test_html_creator_goal,
            backstory=test_html_creator_backstory,
            verbose=True,
            allow_delegation=False,
            tools=[create_exam_html_maker_tool],
            llm=self.llm,
            max_iter=2
        )

    def _create_orchestrator_task(self, agent):
        test_orchestrator_task_description = self.orchestrator_prompt.task_description
        test_orchestrator_task_expected_output = self.orchestrator_prompt.task_expected_output
        return Task(
            description=(test_orchestrator_task_description),
            expected_output=test_orchestrator_task_expected_output,
            agent=agent,
            output_file="dulieu-de-thi.md",
            tools=[FileReadTool('./outputs/matrix.json')]
        )

    def _create_exam_generator_task(self, agent):
        test_creator_task_description = self.creator_prompt.task_description
        test_creator_task_expected_output = self.creator_prompt.task_expected_output
        return Task(
            description=(test_creator_task_description),
            expected_output=test_creator_task_expected_output,
            output_file="./outputs/de-thi.md, dap-an.md",
            # output_json=ExamJSON,
            agent=agent,
            tools=[ExamTool.get_chapter],
            context=[self.orchestrator_task]
        )

    def _create_checker_task(self, agent):
        test_checker_task_description = self.checker_prompt.task_description
        test_checker_task_expected_output = self.checker_prompt.task_expected_output
        return Task(
            description=(test_checker_task_description),
            expected_output=test_checker_task_expected_output,
            output_file="./outputs/danh-gia.md",
            agent=agent,
            context=[self.orchestrator_task]
        )

    def _create_exam_html_creator_task(self, agent):
        test_html_creator_task_description = self.html_creator_prompt.task_description
        test_html_creator_task_expected_output = self.html_creator_prompt.task_expected_output
        return Task(
            description=(test_html_creator_task_description),
            expected_output=test_html_creator_task_expected_output,
            #output_file="de-thi.md, dap-an.md",
            agent=agent,
            # context=[self.exam_generator_task, self.checker_task]
        )

    def run(self, inputs=None):
        
        with open("./outputs/matrix.json", "r", encoding="utf-8") as file:
            matrix = json.load(file)
        inputs = {"ma_tran_de_bai": matrix}
        return super().run()
        
