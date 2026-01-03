# Rubico

Professional Rubika Bot Framework 🚀

---

## نصب

```bash
pip install rubico
from rubico import Bot
from rubico.keyboard import Keyboard
from rubico.force_join import ForceJoin

bot = Bot("TOKEN")
bot.use(ForceJoin(bot, "@my_channel", "⚠️ لطفا عضو کانال شوید"))

@bot.command("start")
def start(ctx):
    kb = Keyboard()
    kb.add("📌 راهنما").add("📞 تماس", row=True)
    ctx.reply("سلام 😎، یکی رو انتخاب کن", keyboard=kb)

@bot.on_message(contains="سلام")
def hello(msg):
    bot.send_message(msg.chat_id, "سلام! خوش اومدی 😎")

bot.run()
