// 必要なパッケージ: mineflayer, node-fetch
import mineflayer from 'mineflayer';
import fetch from 'node-fetch';

const bot = mineflayer.createBot({
  host: '192.168.10.101', // IPアドレス, localならlocalhostで良いはず
  port: 25565,       // Minecraftサーバーのポート
  username: 'ai_steve' // Botのユーザー名
});

// Flask APIサーバーのエンドポイント
const API_URL = 'http://localhost:5000/chat';

bot.on('chat', async (username, message) => {
  // 自分自身の発言は無視
  if (username === bot.username) return;

  // チャット内容をFlask APIにPOST
  try {
    const res = await fetch(API_URL, {
      method: 'POST',
      body: JSON.stringify({ user: username, message }),
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    if (data.reply) {
      // AIの返答をゲーム内チャットで発言
      bot.chat(data.reply);
    } else if (data.error) {
      bot.chat('AI error: ' + data.error);
    }
  } catch (err) {
    bot.chat('API connection error');
    console.error(err);
  }
});

bot.on('login', () => {
  console.log('ai_steve bot logged in');
  bot.chat('こんにちは！私はAI Steveです。チャットで話しかけてください。');
});

bot.on('error', err => {
  console.error('Bot error:', err);
});

bot.on('end', () => {
  console.log('Bot disconnected');
});
