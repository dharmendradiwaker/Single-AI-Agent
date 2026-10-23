from agent import agent
from config import config


#Agent calling
def main():
    while True:
        q = input("\n\nAsk question:- ")
        if q in ("exit","stop", "q"):
            break
        query_resp = agent.stream({"messages":[{"role":"user", "content":q}]},config, stream_mode="messages")

        for chunk, meta in query_resp:
            if meta.get("langgraph_node") != "model":
                continue  # skip tool outputs; only show the model's tokens

            thinking = chunk.additional_kwargs.get("reasoning_content")
            if thinking:
                print(thinking, end="", flush=True)

            if chunk.content:
                print(chunk.content, end="", flush=True)

            for tc in chunk.tool_call_chunks:
                if tc.get("name"):
                    print(f"\n🔧 calling {tc['name']}", flush=True)



if __name__ == "__main__":
    main()