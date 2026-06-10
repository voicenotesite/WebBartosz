import { WorkerEntrypoint } from "@cloudflare/workers-types";

export interface Env {
  TELEGRAM_BOT_TOKEN: string;
  YOUR_TELEGRAM_CHAT_ID: string;
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    
    if (url.pathname === "/") {
      return new Response(JSON.stringify({ status: "Bot is running" }), {
        headers: { "Content-Type": "application/json" },
      });
    }
    
    if (url.pathname === "/send-message") {
      const body = await req.json() as { name: string; message: string };
      const { name, message } = body;
      
      const genderText = ["Pani", "Pan", ""];
      const isFemale = ["maria", "anna", "kasia", "magdalena"].includes(name.toLowerCase().substring(0, 5));
      const greeting = isFemale 
        ? `👩 Ghost Dev połączyła się z ${genderText[0]} ${name}`
        : `👨 Ghost Dev połączył się z ${genderText[1]} ${name}`;
      
      const text = `${greeting}\n\n📝 ${message}`;
      
      const telegramResp = await fetch(
        `https://api.telegram.org/bottest${env.TELEGRAM_BOT_TOKEN}/sendMessage`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            chat_id: env.YOUR_TELEGRAM_CHAT_ID,
            text,
            parse_mode: "HTML",
          }),
        }
      );
      
      return new Response(JSON.stringify(await telegramResp.json()), {
        headers: { "Content-Type": "application/json" },
      });
    }
    
    return new Response("Not found", { status: 404 });
  }
};