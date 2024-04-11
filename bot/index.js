const fastify = require("fastify")({ logger: true });

const {
  Client,
  Events,
  GatewayIntentBits,
  Partials,
  ChannelType,
} = require("discord.js");

const { getResponse } = require("./utils");

require("dotenv").config();
console.log(process.env);

// Create a new client instance
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.DirectMessages,
    GatewayIntentBits.MessageContent,
  ],
  partials: [Partials.Channel, Partials.Message],
});

// When the client is ready, run this code (only once).
client.once(Events.ClientReady, (readyClient) => {
  console.log(`Ready! Logged in as ${readyClient.user.tag}`);

  // Log incoming messages
  client.on("messageCreate", async (message) => {
    console.log(`[Incoming Message] ${message.content}`);
    if (message.author.bot) return;

    // Check if the message is in a DM channel
    if (message.channel.type === ChannelType.DM) {
      console.log(`[Incoming DM] ${message.content}`);

      message.channel.sendTyping();

      // Fetch the last 10 messages from the DM channel
      let messages = [];

      try {
        const messageHistory = await message.channel.messages.fetch({
          limit: 6,
        });
        console.log("Previous 10 messages in the DM:");
        messageHistory.forEach((msg) => {
          console.log(`[${msg.createdAt}] ${msg.author.tag}: ${msg.content}`);
          messages = [
            {
              role: msg.author.bot ? "assistant" : "user",
              content: msg.content,
            },
            ...messages,
          ];
        });

        console.log(messages);
      } catch (error) {
        console.error("Failed to fetch messages:", error);
      }

      const response = await getResponse(messages).catch((error) => {
        console.log(error);
        return null;
      });

      if (response !== null) {
        message.author.send(response);
      }
    }
  });

  // Declare a route
  fastify.get("/", function handler(request, reply) {
    reply.send({ status: true });
  });

  fastify.get("/id/:userId", async (request, reply) => {
    const { userId } = request.params;
    client.users.send(userId, "status: true");
    reply.send({ status: true });
  });

  fastify.post("/id/:userId", async (request, reply) => {
    const { userId } = request.params;
    console.log(request.body);
    client.users.send(userId, request.body.content);
    reply.send({ status: true });
  });

  fastify.get("/id/:userId/delete", async (request, reply) => {
    const { userId } = request.params;

    try {
      // Fetch the user by ID
      const user = await client.users.fetch(userId);
      if (!user) {
        reply.code(404).send({ message: "User not found" });
        return;
      }

      // Fetch the DM channel with this user
      const dmChannel = await user.createDM();
      if (!dmChannel) {
        reply.code(404).send({ message: "DM channel not found" });
        return;
      }

      // Function to delete all messages sent by the bot in the DM
      const deleteBotMessages = async () => {
        let shouldContinue = true;
        while (shouldContinue) {
          // Fetch messages in batches of 100 (maximum allowed)
          const messages = await dmChannel.messages.fetch({ limit: 100 });
          const botMessages = messages.filter(
            (m) => m.author.id === client.user.id
          );

          // Delete all messages sent by the bot
          for (const msg of botMessages.values()) {
            await msg.delete();
          }

          // If fewer than 100 messages were fetched, we've reached the end
          if (messages.size < 100) {
            shouldContinue = false;
          }
        }
      };

      // Execute the deletion
      await deleteBotMessages();
      reply.send({ message: "All bot messages deleted successfully." });
    } catch (error) {
      console.error("Failed to delete messages:", error);
      reply.code(500).send({ message: "Failed to delete messages" });
    }
  });

  // Run the server!
  fastify.listen({ port: 3737 }, (err) => {
    if (err) {
      fastify.log.error(err);
      process.exit(1);
    }
  });
});

// Log in to Discord with your client's token
client.login(process.env.DISCORD_TOKEN);
