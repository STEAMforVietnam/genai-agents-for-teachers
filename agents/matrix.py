from crewai import Agent, Crew, Task
from agents.base import CustomCrew
from agents.models import MatrixJSON
from agents.custom_tools import create_matrix_html_maker_tool

class MatrixCrew(CustomCrew):
    """
    This is a CustomCrew specific for creating an Matrix file from
    Textbooks and other reference materials, such as Ministry of Education's instruction
    """
    def __init__(self, creator_prompt,
                 orchestrator_prompt=None,
                 checker_prompt=None,
                 html_creator_prompt=None):
        super(MatrixCrew, self).__init__(
          creator_prompt, orchestrator_prompt, 
          checker_prompt, html_creator_prompt)
        
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
            allow_delegation=False,
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
        matrix_creator_role = self.creator_prompt.role
        matrix_creator_goal = self.creator_prompt.goal
        matrix_creator_backstory = self.creator_prompt.backstory
        
        matrix_creator = Agent(
            role=matrix_creator_role,
            goal=(matrix_creator_goal
            ),
            backstory=matrix_creator_backstory,
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            tools=self.tools,
            max_iter=1
        )
        
        # TODO: change Task args description and expected_output to take in prompt.txt
        matrix_creator_task_description = self.creator_prompt.task_description
        matrix_creator_task_expected_output = self.creator_prompt.task_expected_output
        
        matrix_creator_task = Task(
            description=(matrix_creator_task_description),
            expected_output=matrix_creator_task_expected_output,
            agent=matrix_creator,
            output_json=MatrixJSON
            # context=[orchestrator_task]
        )

        ### Add Matrix Checker Agent (Nguời Kiểm Định), responsible for all "Kiểm Tra Task"
        matrix_checker_role = self.checker_prompt.role
        matrix_checker_goal = self.checker_prompt.goal
        matrix_checker_backstory = self.checker_prompt.backstory
        
        matrix_checker = Agent(
            role=matrix_checker_role,
            goal=matrix_checker_goal,
            backstory=matrix_checker_backstory,
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            # tools=self.tools,
            max_iter=2
        )

        matrix_checker_task_description = self.checker_prompt.task_description
        matrix_checker_task_expected_output = self.checker_prompt.task_expected_output
        matrix_checker_task = Task(
            description=(matrix_checker_task_description),
            expected_output=(matrix_checker_task_expected_output),
            agent=matrix_checker,
            # output_json=MatrixJSON,
            # output_file="matrix.json",
            context=[matrix_creator_task],
        )

        ### ADD HTML Creator Agent (Thiết kế WEB)
        matrix_html_creator_role = self.html_creator_prompt.role
        matrix_html_creator_goal = self.html_creator_prompt.goal
        matrix_html_creator_backstory = self.html_creator_prompt.backstory
        html_creator = Agent(
            role=matrix_html_creator_role,
            goal=matrix_html_creator_goal,
            backstory=matrix_html_creator_backstory,
            allow_delegation=False,
            llm=self.llm, 
            verbose=True, 
            tools=[create_matrix_html_maker_tool],
            max_iter=1
        )
        
        matrix_html_creator_task_description = self.html_creator_prompt.task_description
        matrix_html_creator_task_expected_output = self.html_creator_prompt.task_expected_output
        html_task = Task(
            description=(matrix_html_creator_task_description),
            # TODO: somehow the tool output is not passed back to Agent Output
            # SO expected_output is never met and the agent + the task fall into infinite loop
            expected_output=(matrix_html_creator_task_expected_output),
            # output_file="matrix.html"
            agent=html_creator,
            # context=[matrix_creator_task, matrix_checker_task],
            
        )

        ### Finally, compose Crew
        return Crew(
                agents=[matrix_orchestrator, matrix_creator, matrix_checker, html_creator],
                tasks=[matrix_orchestrator_task, matrix_creator_task, matrix_checker_task, html_task],
                # manager_agent=orchestrator,
                # memory=True,
                # process=Process.hierarchical,
                verbose=2
            )