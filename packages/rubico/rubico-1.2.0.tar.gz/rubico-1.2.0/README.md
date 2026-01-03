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
# Rubico 🧩

Professional Rubika Bot Framework - Version 1.1.0 🚀

Rubico یک فریم‌ورک کامل برای ساخت ربات‌های روبیکا است که امن، پایدار و قابل توسعه است.  
با Rubico می‌توانید ربات‌های حرفه‌ای بسازید بدون اینکه نگران Storage، مدیریت مراحل، یا Force Join باشید.

---

## 🔥 ویژگی‌های جدید v1.1.0
- ✅ Storage امن با JSON (دیگه از eval خبری نیست!)
- ✅ Force Join واقعی (چک عضویت کاربر در کانال)
- ✅ Step Handler برای ربات‌های مرحله‌ای
- ✅ Message Object حرفه‌ای (`ctx.message.text`, `ctx.message.user`)
- ✅ Logger و Error Handling پیشرفته
- ✅ آماده برای Plugin System و توسعه آسان

---

## 📦 نصب

```bash
pip install rubico --upgrade
from rubico import Bot, Keyboard, ForceJoin

bot = Bot("TOKEN")

# Middleware Force Join
bot.use(ForceJoin(bot, "@my_channel", "⚠️ لطفا عضو کانال شوید"))

# Command Start
@bot.command("start")
def start(ctx):
    kb = Keyboard()
    kb.add("📌 راهنما").add("📞 تماس", row=True)
    ctx.reply("سلام 😎، یکی رو انتخاب کن", keyboard=kb)

# Message Handler ساده
@bot.on_message()
def hello(msg):
    if "سلام" in msg.get("text", ""):
        ctx = bot.Context(bot, msg, bot.storage)
        ctx.reply("سلام! خوش اومدی 😎")

bot.run()
