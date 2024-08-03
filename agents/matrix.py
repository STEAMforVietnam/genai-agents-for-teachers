from crewai import Agent, Crew, Task, Process
from crewai.tasks.conditional_task import ConditionalTask
from agents.base import CustomCrew
from agents.models import MatrixJSON, EvaluationJSON
from agents.custom_tools import create_matrix_html_maker_tool
from agents.prompt_list import PromptList
from tools.exam import ExamTool
from pydantic_core import from_json

class MatrixCrew(CustomCrew):
    """
    This is a CustomCrew specific for creating an Matrix file from
    Textbooks and other reference materials, such as Ministry of Education's instruction
    """
    def __init__(self, 
                 creator_prompt=PromptList('./prompts/prompt_list_matrix_creator.txt'),
                 orchestrator_prompt=PromptList('./prompts/prompt_list_matrix_orchestrator.txt'),
                 checker_prompt=PromptList('./prompts/prompt_list_matrix_checker.txt'),
                 html_creator_prompt=PromptList('./prompts/prompt_list_matrix_html_creator.txt')):
        super(MatrixCrew, self).__init__(
          creator_prompt, orchestrator_prompt, 
          checker_prompt, html_creator_prompt)
        
    def is_done(result: EvaluationJSON) -> bool:
        return True if result.result == "DONE" else False
    
    def _get_tools(self):
        super()._get_tools()
        self.tools.append(create_matrix_html_maker_tool)

    def _get_crew(self):
        """
        Create a crew for building Exam file
        """
        self._get_tools()

        ### Add Orchestrator (Người Giám Sát)
        matrix_orchestrator_role = self.orchestrator_prompt.role
        matrix_orchestrator_goal = self.orchestrator_prompt.goal
        matrix_orchestrator_backstory = self.orchestrator_prompt.backstory

        matrix_orchestrator = Agent(
            role=matrix_orchestrator_role,
            goal=(matrix_orchestrator_goal),
            backstory=matrix_orchestrator_backstory,
            allow_delegation=True,
            llm=self.llm,
            verbose=True,
            max_iter=5
        )

        matrix_orchestrator_task_description = self.orchestrator_prompt.task_description
        matrix_orchestrator_task_expected_output = self.orchestrator_prompt.task_expected_output
        matrix_orchestrator_task = Task(
            description=(matrix_orchestrator_task_description),
            expected_output=matrix_orchestrator_task_expected_output,
            agent=matrix_orchestrator,
        )

        ### Add Matrix Creator Agent (Ngừoi Kiến Tạo), responsible for all "Tạo" task
        # TODO: change Agent args roal, goal, backstory to take in prompt.txt        
        matrix_creator = Agent(
            role=self.creator_prompt.role,
            goal=(self.creator_prompt.goal
            ),
            backstory=self.creator_prompt.backstory,
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            # tools=[ExamTool.get_appendix],
            max_iter=5
        )
        
        # TODO: change Task args description and expected_output to take in prompt.txt        
        matrix_creator_task = Task(
            description=(self.creator_prompt.task_description),
            expected_output=self.creator_prompt.task_expected_output,
            agent=matrix_creator,
            output_json=MatrixJSON,
            # output_file="./outputs/matrix-creator-output.md",
            tools=[ExamTool.get_appendix],
            context=[matrix_orchestrator_task]
        )

        ### Add Matrix Checker Agent (Nguời Kiểm Định), responsible for all "Kiểm Tra Task"        
        matrix_checker = Agent(
            role=self.checker_prompt.role,
            goal=self.checker_prompt.goal,
            backstory=self.checker_prompt.backstory,
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            max_iter=5
        )

        matrix_checker_task = Task(
            description=(self.checker_prompt.task_description),
            expected_output=(self.checker_prompt.task_expected_output),
            agent=matrix_checker,
            output_json=EvaluationJSON,
            output_file="./outputs/matrix-danh-gia.md",
            context=[matrix_creator_task],
        )

        ### ADD HTML Creator Agent (Thiết kế WEB)
        html_creator = Agent(
            role=self.html_creator_prompt.role,
            goal=self.html_creator_prompt.goal,
            backstory=self.html_creator_prompt.backstory,
            allow_delegation=False,
            llm=self.llm,
            verbose=True, 
            # tools=[create_matrix_html_maker_tool],
            max_iter=5
        )
        
        html_task = Task(
            description=(self.html_creator_prompt.task_description),
            # TODO: somehow the tool output is not passed back to Agent Output
            # SO expected_output is never met and the agent + the task fall into infinite loop
            expected_output=(self.html_creator_prompt.task_expected_output),
            # output_file="matrix.html"
            agent=html_creator,
            tools=[create_matrix_html_maker_tool]
            # context=[matrix_creator_task, matrix_checker_task],
            
        )

        ### Finally, compose Crew
        return Crew(
                agents=[matrix_orchestrator, matrix_creator, matrix_checker, html_creator],
                tasks=[matrix_orchestrator_task, matrix_creator_task, matrix_checker_task, html_task],
                memory=True,
                verbose=2,
                # manager_agent=matrix_orchestrator,
                # process=Process.hierarchical,
                planning=True
            )
    
    def run(self):
        eval_result = "NOT DONE"
        result = {
            "result":"NOT DONE",
            "evaluation":"Hãy tạo mới một $Ma_Trận_Đề_Bài",
            "data":[]
        }
        for i in range(0, 2):
            if eval_result == "NOT DONE":
                if isinstance(result, EvaluationJSON):
                    result = result.model_dump()
                print(result)
                result = super().run(inputs=result)

                eval_result = from_json(result.tasks_output[2].json_dict).get("result")
                print(eval_result)
                return result