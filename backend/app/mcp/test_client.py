import asyncio

from mcp import Client

from app.mcp.server import mcp


async def main():
    async with Client(mcp) as client:
        tools = await client.list_tools()

        print("\nAvailable MCP tools:")

        for tool in tools.tools:
            print(f"- {tool.name}: {tool.description}")

        resources = await client.list_resources()

        print("\nAvailable resources:")

        for resource in resources.resources:
            print(f"- {resource.uri}")

        prompts = await client.list_prompts()

        print("\nAvailable prompts:")

        for prompt in prompts.prompts:
            print(f"- {prompt.name}")


if __name__ == "__main__":
    asyncio.run(main())