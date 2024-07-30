from dotenv import load_dotenv
load_dotenv()
from agents.agents import MatrixCrew

matrix_crew = MatrixCrew()
result = matrix_crew.run()