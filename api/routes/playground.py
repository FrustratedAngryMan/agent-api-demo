from agno.playground import Playground

from agents.agno_assist import get_agno_assist
from agents.finance_agent import get_finance_agent
from agents.web_agent import get_web_agent
from agents.ttd_coding_helper import TTDCoderAgent

######################################################
## Routes for the Playground Interface
######################################################

# Get Agents to serve in the playground
web_agent = get_web_agent(debug_mode=True)
agno_assist = get_agno_assist(debug_mode=True)
finance_agent = get_finance_agent(debug_mode=True)


ttd_workflow = TTDCoderAgent()
test_generator = ttd_workflow.test_generator
junit_generator = ttd_workflow.junit_generator



# Create a playground instance
playground = Playground(
    agents=[web_agent,
            agno_assist,
            finance_agent,
            test_generator,
            junit_generator],
    teams=[ttd_workflow.team1, ttd_workflow.team2],
    workflows=[ttd_workflow]
    )

# Get the router for the playground
playground_router = playground.get_async_router()
