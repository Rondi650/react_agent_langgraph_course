from collections.abc import Sequence
from typing import Annotated, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import END, START, StateGraph, add_messages, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import Messages
from langgraph.graph.state import RunnableConfig
from rich import print
from rich.markdown import Markdown
from dotenv import load_dotenv
load_dotenv()
import os

os.system('cls')

# llm = init_chat_model("google_genai:gemini-2.5-flash")
llm = init_chat_model("openai:gpt-5-nano")


# NÃO PRECISA FAZER ISSO
def reducer(a: Messages, b: Messages) -> Messages:
    print(f"Reducing messages... A{a}")
    print(Markdown("---"))
    print(f"Reducing messages... B{b}")
    print(Markdown("---"))
    return add_messages(a, b)
print(reducer)


# 1 - Defino o meu state
class AgentState(TypedDict):
    rondinelle: Annotated[Sequence[BaseMessage], reducer]

SYSTEM_MESSAGE = SystemMessage("Voce conversa em portugues do Brasil e se apresenta como Joaozinho.")

# 2 - Defino os meus nodes
def call_llm(state: AgentState) -> AgentState:
    print(f'Mensagens do Estado: {state}')
    print(Markdown("---"))
    
    llm_result = llm.invoke(state["rondinelle"])
    print(f'Resultado do LLM: {llm_result}')
    print(Markdown("---"))
    return {"rondinelle": [llm_result]}



# 3 - Crio o StateGraph
builder = StateGraph(
    AgentState, context_schema=None, input_schema=AgentState, output_schema=AgentState
)
print(builder)

# 4 - Adicionar nodes ao grafo
builder.add_node("call_llm", call_llm)

# 4.1 Aqui estao os edges
builder.add_edge(START, "call_llm")
builder.add_edge("call_llm", END)

# 5 - Compilar o grafo
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
print(graph)

if __name__ == "__main__":
    current_messages: Sequence[BaseMessage] = []
    human_message = HumanMessage("Meu nome e Rondinelle.")
    print(Markdown("## Iniciando conversa com Rondinelle"))
    print(human_message)
    print(Markdown("---"))
    config = RunnableConfig(configurable={"thread_id": 1})
    result = graph.invoke({"rondinelle": [human_message] + [SYSTEM_MESSAGE]} , config=config)
    print(result['rondinelle'][-1].content)
    print(Markdown("---"))
    
    human_message = HumanMessage("Qual meu nome?")
    print(Markdown("## Iniciando conversa com Rondinelle"))
    print(human_message)
    print(Markdown("---"))
    config = RunnableConfig(configurable={"thread_id": 1})
    result = graph.invoke({"rondinelle": [human_message]} , config=config)
    print(result['rondinelle'][-1].content)
    print(Markdown("---"))
    
    print(Markdown("## Estado Final"))
    print(result)

    # while True:
    #     user_input = input("Digite sua mensage: ")
    #     print(Markdown("---"))

    #     if user_input.lower() in ["q", "quit"]:
    #         print("Bye 👋")
    #         print(Markdown("---"))
    #         break

    #     human_message = HumanMessage(user_input)
    #     current_messages = [*current_messages, human_message]

    #     result = graph.invoke({"messages": current_messages})
    #     current_messages = result["messages"]

    #     print(Markdown(str(result["messages"][-1].content)))
    #     print(Markdown("---"))
