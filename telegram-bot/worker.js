export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    if (url.pathname === "/") {
      return new Response(JSON.stringify({status: "Bot is running"}), {
        headers: {"Content-Type": "application/json"}
      });
    }
    
    if (url.pathname === "/send-message") {
      const body = await request.json();
      const TOKEN = env.TELEGRAM_BOT_TOKEN;
      const CHAT_ID = env.YOUR_TELEGRAM_CHAT_ID;
      
      const genderText = {"male": "Pan", "female": "Pani", "unknown": ""};
      const gender = body.name === "Ghost" ? "unknown" : "male"; // hardcoded for demo
      
      const text = gender === "unknown" 
        ? `✨ Ghost Dev: <b>${body.name}</b>\n\n📝 ${body.message}`
        : `👨 Ghost Dev połączył się z Pana <b>${body.name}</b>\n\n📝 ${body.message}`;
      
      await fetch(`https://api.telegram.org/bottestelegramchatbotbot/sendMessage`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          chat_id: CHAT_ID,
          text: text,
          parse_mode: "HTML"
        })
      });
      
      return new Response(JSON.stringify({status: "sent"}), {
        headers: {"Content-Type": "application/json"}
      });
    }
    
    return new Response("Not found", {status: 404});
  }
};