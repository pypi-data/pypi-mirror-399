# ACP Setup

Decoder can be used in text editors and IDEs that support [Agent Client Protocol](https://agentclientprotocol.com/overview/clients). Decoder includes the `decoder-acp` tool.
Once you have set up `decoder` with the API keys, you are ready to use `decoder-acp` in your editor. Below are the setup instructions for some editors that support ACP.

## Zed

For usage in Zed, we recommend using the [Decoder Zed's extension](https://zed.dev/extensions/decoder). Alternatively, you can set up a local install as follows:

1. Go to `~/.config/zed/settings.json` and, under the `agent_servers` JSON object, add the following key-value pair to invoke the `decoder-acp` command. Here is the snippet:

```json
{
   "agent_servers": {
      "Decoder": {
         "type": "custom",
         "command": "decoder-acp",
         "args": [],
         "env": {}
      }
   }
}
```

2. In the `New Thread` pane on the right, select the `decoder` agent and start the conversation.

## JetBrains IDEs

1. Add the following snippet to your JetBrains IDE acp.json ([documentation](https://www.jetbrains.com/help/ai-assistant/acp.html)):

```json
{
  "agent_servers": {
    "Decoder": {
      "command": "decoder-acp",
    }
  }
}
```

2. In the AI Chat agent selector, select the new Decoder agent and start the conversation.

## Neovim (using avante.nvim)

Add Decoder in the acp_providers section of your configuration

```lua
{
  acp_providers = {
    ["decoder"] = {
      command = "decoder-acp",
      env = {
         MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY"), -- necessary if you setup Decoder manually
      },
    }
  }
}
```
