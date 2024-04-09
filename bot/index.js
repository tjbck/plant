// Require the necessary discord.js classes
// Require the framework and instantiate it
const fastify = require("fastify")({ logger: true });

const { Client, Events, GatewayIntentBits, Partials } = require("discord.js");
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
// The distinction between `client: Client<boolean>` and `readyClient: Client<true>` is important for TypeScript developers.
// It makes some properties non-nullable.
client.once(Events.ClientReady, (readyClient) => {
  console.log(`Ready! Logged in as ${readyClient.user.tag}`);

  // Log incoming messages
  client.on("messageCreate", (message) => {
    console.log(`[Incoming Message] ${JSON.stringify(message)}`);

    // Check if the message is in a DM channel
    if (message.channel.type === "DM") {
      console.log(`[Incoming DM] ${JSON.stringify(message)}`);
    }
  });

  // Declare a route
  fastify.get("/", function handler(request, reply) {
    reply.send({ status: true });
  });

  // Run the server!
  fastify.listen({ port: 3000 }, (err) => {
    if (err) {
      fastify.log.error(err);
      process.exit(1);
    }
  });
});

// Log in to Discord with your client's token
client.login(process.env.DISCORD_TOKEN);
