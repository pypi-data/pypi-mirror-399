<h1>🔐 How to enable HTTPS in fastapi-all-helper 🌐</h1>

<p><b>Выберите язык / Choose language ⬇️</b></p>

<details open>
<summary>🇷🇺 Русский</summary>

<h2>Как подключить https к fastapi-all-helper</h2>

<p>
    <b>Всем привет 👋</b>, в данном положении мы поговорим о нововведении нашей библиотеки
    а именно поддержки <b>https протокола</b> 🔒
</p>

<p>
    В данной статьи мы поговорим как же запустить ваше приложение
    на <b>https протоколе</b> с помощью <b>fastapi-all-helper</b> 🚀
</p>

<p><b>Итак, начнем ⬇️</b></p>

<hr>

<p>
    Для начала нам нужно создать <b>SSL сертификат и SSL ключ для доступа к https</b> 🔑
</p>

<p>
    Зачем это нужно?
    <b>Они нужны чтобы обеспечивать безопасную передачу данных между клиентом и сервере,
    а также для подлинности сайта</b>,
    что на протоколе http не делается этого ❌
</p>

<p>
    Итак в корне нашего проекта давайте создадим папку <b>certs</b> 📁
    в ней пока что будет пусто и не нужно создавать совместные файлы
    достаточно будет лишь вписать одну команду и все ✅
</p>

<p>
    Затем мы переходим в терминал 💻, через терминал мы заходим в нашу папку
    <b>certs</b> и пишем туда эту команду:
</p>

```bash
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem \
  -out cert.pem \
  -days 365 \
  -nodes \
  -subj "/CN=localhost"
```

<p>
    Данная команда автоматически создаст вам файлы
    <b>key.pem</b> и <b>cert.pem</b> 📄
</p>

<img src="./photo/ssl_dir.jpg" alt="Фото демонстрации">

<hr>

<p>
    Затем, вас обязательно нужно зайти в <b>.gitignore</b> file
    и <b>скрыть данные файлы</b> 🙈 либо так:
</p>

<pre><code>*.pem
certs/</code></pre>

<img src="./photo/github_sll.jpg" alt="Фото демонстрации">

<hr>

<p>
    Дальше у вас уже есть ключ и сертификат,
    <b>теперь вы можете переходить на то чтобы запустить ваш проект
    на https протоколе</b> 🚀
</p>

```python

import asyncio

from fastapi import FastAPI
from fastapi_helper import Client

app = FastAPI()
client = Client(app=app, host="127.0.0.1", port=9090, https=True)
"""
По умолчанию https будет стоять False и запуская ваш проект
он запуститься на http протоколе, будьте внимательны
"""
# запуск
async def main() -> None:
    await client.start_app(
        certfile="certs/cert.pem",
        keyfile="certs/key.pem"
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
```


<img src="./photo/run_with_ssl.jpg" alt="Фото демонстрации">

<hr>

<p>
    Итак давайте разберемся что мы сделали в аргумент метода
    <b>start_app()</b> —
    мы передали два значения <b>certfile</b> и <b>keyfile</b>
</p>

<h3>✅ Итоги</h3>

<p>
    <b>
        мы разобрались как запустить наше приложенение
        всего лишь в два клика на протоколе https
        всем спасибо за внимание 🙌
    </b>
</p>

</details>

<hr>

<details>
<summary>🇬🇧 English</summary>

<h2>How to enable HTTPS in fastapi-all-helper</h2>

<p>
    <b>Hello everyone 👋</b>, in this guide we will talk about a new feature of our library —
    <b>HTTPS protocol support</b> 🔒
</p>

<p>
    In this article, we will show how to run your application
    on the <b>HTTPS protocol</b> using <b>fastapi-all-helper</b> 🚀
</p>

<p><b>Let’s get started ⬇️</b></p>

<hr>

<p>
    First, we need to create an <b>SSL certificate and SSL key for HTTPS access</b> 🔑
</p>

<p>
    Why is this necessary?
    <b>They are required to ensure secure data transmission between the client and the server,
    as well as site authenticity</b>,
    which is not provided by the HTTP protocol ❌
</p>

<p>
    In the root of your project, create a <b>certs</b> folder 📁
    it can be empty for now — you only need to run one command ✅
</p>

<p>
    Open the terminal 💻, navigate to the <b>certs</b> folder
    and run the following command:
</p>

```bash
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem \
  -out cert.pem \
  -days 365 \
  -nodes \
  -subj "/CN=localhost"
```

<p>
    This command will automatically generate
    <b>key.pem</b> and <b>cert.pem</b> files 📄
</p>

<img src="./photo/ssl_dir.jpg" alt="Demo image">

<hr>

<p>
    Next, make sure to add these files to <b>.gitignore</b> 🙈
</p>

<pre><code>*.pem
certs/</code></pre>

<img src="./photo/github_sll.jpg" alt="Demo image">

<hr>

<p>
    Now you have the key and certificate,
    <b>you can run your project using the HTTPS protocol</b> 🚀
</p>

```python
import asyncio

from fastapi import FastAPI
from fastapi_helper import Client

app = FastAPI()
client = Client(app=app, host="127.0.0.1", port=9090, https=True)

async def main() -> None:
    await client.start_app(
        certfile="certs/cert.pem",
        keyfile="certs/key.pem"
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
```

<img src="./photo/run_with_ssl.jpg" alt="Demo image">

<hr>

<p>
    In the <b>start_app()</b> method,
    we passed two arguments: <b>certfile</b> and <b>keyfile</b>
</p>

<h3>✅ Summary</h3>

<p>
    <b>
        Now you know how to run your application
        on HTTPS in just two clicks.
        Thanks for reading 🙌
    </b>
</p>

</details>
