import asyncio

from agno.models.google import Gemini
from agno.team import Team
from dotenv import load_dotenv
from agno.agent import Agent, RunResponse
from agno.knowledge.text import TextKnowledgeBase
from agno.models.groq import Groq
from agno.models.ollama import Ollama
from agno.workflow import Workflow
from agents.output_models import TestCases, FileUpdateList

from agents.knowledge_base_loader import KnowledgeBaseLoader
from agents.combined_knowledge_base_loader import CombinedKnowledgeBaseLoader

load_dotenv()


class TTDCoderAgent(Workflow):
    description: str = "TTD Coding Helper Workflow"

    # Initialize knowledge base
    # knowledge_base: TextKnowledgeBase = KnowledgeBaseLoader.code_knowledge_base
    knowledge_base: TextKnowledgeBase = CombinedKnowledgeBaseLoader.combined_knowledge_base
    # Below line is not required, as the agent creation takes care of data load automatically
    # knowledge_base.load()

    # Define agents as class attributes

    # Agent that generates code based on given test cases
    code_snippet_generator_based_on_testcase: Agent = Agent(
        name="Code Snippet Generator for given scenario or test cases",
        # model=Ollama(id="llama3-groq-tool-use"),
        # model=Groq(id="llama-3.3-70b-versatile"),
        # model=Groq(id="deepseek-r1-distill-llama-70b"),
        model=Gemini("gemini-2.0-flash"),
        knowledge=knowledge_base,
        search_knowledge=True,
        description="Generates code for given scenario",
        instructions=[
            "You are an expert java developer",
            "When asked, use the available knowledge base (the codebase) to generate the code snippet for the given scenario",
            "Always give output as code snippets, strictly no explanations required"
        ],
        debug_mode=True,
    )

    # Agent that generates test cases for given scenarios
    test_generator: Agent = Agent(
        agent_id="test_generator",
        name="Test Case Generator",
        # model=Ollama(id="llama3-groq-tool-use"),
        # model=Groq(id="llama-3.3-70b-versatile"),
        model=Gemini("gemini-2.0-flash"),
        description="Generates test cases for given scenarios",
        instructions=[
            "You are an expert manual Tester. Your task is to provide test cases for given scenarios for Test Driven Development.",
            "When asked, use common sense to create test scenarios.",
        ],
        response_model=TestCases,
        debug_mode=True,
    )

    # Agent that generates test cases for given scenarios
    junit_generator: Agent = Agent(
        agent_id="junit_generator",
        name="JUnit Test Generator",
        # model=Ollama(id="llama3-groq-tool-use"),
        # model=Groq(id="llama-3.3-70b-versatile"),
        model=Gemini("gemini-2.0-flash"),
        description="Updates JUnit test cases for given scenarios",
        knowledge=knowledge_base,
        add_references=True,
        instructions=[
            "You are an expert Java Developer following Test driven development.",
            "Your task is to create/update JUnit test cases for given scenarios for Test Driven Development.",
            "ALWAYS look into to the knowledge base before creating JUnits and Integration Tests",
            "For Product related JUnits, update ProductControllerIntegrationTest.java"
            # "Create a test suite with test stubs that map to these requirements."
        ],
        debug_mode=True,
        response_model=FileUpdateList
    )

    code_analyst_agent: Agent = Agent(
        agent_id="code_analyst_agent",
        name="Code Base Analyst",
        # model=Ollama(id="llama3-groq-tool-use"), Not working
        # model = Groq(id="llama-3.3-70b-versatile"), Working
        # model = Groq(id="qwen/qwen3-32b"),
        # qwen3 is decent offline model with tool use. can be used for simple analysis.
        # model = Ollama(id="qwen3:8b"),
        model=Gemini("gemini-2.0-flash"),
        knowledge=knowledge_base,
        search_knowledge=True,
        add_references=True,
        markdown=True,  # Format responses in Markdown
        instructions=[
            "You are an expert code analyst. Your task is to provide insights about the given codebase.",
            "When asked, use the available knowledge base (the codebase) to answer questions.",
            "Focus on code structure, functionality, potential improvements, and common patterns.",
            "Always cite the file paths from where you retrieved information."
        ]
    )

    fileFinderAgent: Agent = Agent(
        agent_id="fileFinderAgent",
        name="File Finder Agent - Local",
        # model=Groq(id="deepseek-r1-distill-llama-70b"),
        # model=Ollama(id="qwen3:8b"),
        # model=Groq(id="qwen/qwen3-32b"),
        # model=Groq(id="llama-3.3-70b-versatile"), Did not work for this role/instructions
        model=Gemini("gemini-2.0-flash"),
        knowledge=knowledge_base,
        search_knowledge=True,
        # add_references=True,
        instructions=[
            "You are an expert code analyst. Your task is to identify the most relevant files in the provided codebase that would need modification or review for a given software development requirement.",
            "When asked for a requirement, perform a knowledge base search.",
            "Your response should be a comma-separated list of absolute file paths only. Do NOT include any other text, explanations, or code snippets.",
            "Mark the files with UPDATE or CREATE as applicable",
            "If you cannot find any relevant files, respond with 'No relevant files found'.",
            "When a new attribute is added to Products or Categories. CSVUtils.java and the products.csv or categories.csv has to be updated accordingly"
        ],
        markdown=True,
        debug_mode=True,
    )

    # Agent that generates code based on given scenario
    code_generator_based_on_testcase: Agent = Agent(
        agent_id="code_generator_based_on_testcase",
        name="Code Generator for given scenario",
        # model=Ollama(id="llama3-groq-tool-use"),
        # model=Groq(id="llama-3.3-70b-versatile"),
        # model=Groq(id="deepseek-r1-distill-llama-70b"),
        model=Gemini("gemini-2.0-flash"),
        knowledge=knowledge_base,
        # search_knowledge=True,
        add_references=True,
        description="Generates code for given scenario",
        instructions=[
            "You are an expert java developer",
            "Your task is to perform code updates on the knowledge base for the given requirement",
            "Consider the list of files provided by File finder agent while updating the existing knowledge base",
            "Update the existing code in the knowledge base",
            "Update all the relevant files in the knowledge base for the requirement including controller, pojos, service, repository and csv files as necessary.",
        ],
        debug_mode=True,
        stream=False,
    )

    team1 = Team(
        team_id="code-generator-team-1",
        name="Code Generator - Team 1",
        mode="coordinate",
        # model=Groq(id="deepseek-r1-distill-llama-70b"),
        model=Gemini("gemini-2.0-flash"),
        members=[fileFinderAgent, code_generator_based_on_testcase],
        description="You are team lead and your task is co-ordinate between the File Finder Agent and Code Generator Agent",
        instructions=[
            "You are team lead and your task is co-ordinate between the File Finder Agent and Code Generator Agent",
            "Interact with each team member only once",
            "FIRST ask the File Finder Agent to give the list of files to be updated for a requirement.",
            "SECOND ask Code Generator Agent to update the given list of files as applicable for the given requirement.",
            "FINALLY return the response from Code Generator Agent as a PATCH",
        ],
        add_datetime_to_instructions=True,
        add_member_tools_to_system_message=False,
        # This can be tried to make the agent more consistently get the transfer tool call correct
        enable_agentic_context=True,  # Allow the agent to maintain a shared context and send that to members.
        share_member_interactions=True,  # Share all member responses with subsequent member requests.
        show_members_responses=True,
        markdown=True,
    )

    team2 = Team(
        team_id="junit-generator-team-2",
        name="JUnit Generator - Team 2",
        mode="coordinate",
        model=Gemini("gemini-2.0-flash"),
        members=[test_generator, junit_generator],
        description="You are team lead and your task is co-ordinate between the Test Generator Agent, JUnit Generator Agent, and File Writer Agent",
        instructions=[
            "You are team lead and your task is co-ordinate between the Test Generator Agent, JUnit Generator Agent, and File Writer Agent",
            "Interact with each team member only once",
            "FIRST ask the Test Generator Agent to give the list of Test cases for the given requirement",
            "SECOND ask the JUnit Generator Agent to create JUnits for the given test cases",
            # "THIRD ask the File Writer Agent to write the generated JUnit code to the appropriate file",
            "FINALLY return the FileUpdateList as response from JUnit Generator Agent",
        ],
        add_member_tools_to_system_message=False,
        enable_agentic_context=True,
        share_member_interactions=True,
        show_members_responses=True,
    )

    #def run(self, question: str) -> RunResponse:
        # response_1 = self.test_generator.run(question)
        # response_1 = self.code_generator_based_on_testcase.run(question)
        # response_1 = self.team1.run(question)

        #self.team2.aprint_response(question)
        #return


if __name__ == "__main__":
    from rich.prompt import Prompt

    # Get question from user
    val = Prompt.ask(
        "[bold]Enter your test scenario[/bold]\n✨",
        default="""
            As a Product Manager/Inventory Manager
            I want to update the price and stock quantity of an existing product via the Product API
            So that I can quickly and accurately reflect changes in inventory and pricing on the e-commerce platform and other integrated systems.

            Acceptance Criteria:
            API Endpoint:

            The API should expose a PUT or PATCH endpoint for updating a product, e.g., /api/products/{productId}.
            The endpoint must require authentication (e.g., using an API key or OAuth token).
        """
    )

    # Initialize workflow
    #workflow = TTDCoderAgent()

    # Run workflow and get results
    #response = workflow.run(question=val)

    resp_1 = TTDCoderAgent.team2.run(val)
    print('========= Started \n\n', resp_1)

    print('---- Ended ---')
