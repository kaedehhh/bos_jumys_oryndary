# CareerHub — веб-сайт із SQLite

CareerHub — веб-нұсқа бос жұмыс орындарын іздеу және өтінім беру жүйесі. Flask, HTML/CSS және SQLite қолданады.

## Жергілікті іске қосу (Windows / PyCharm)

1. Python 3.10+ орнатыңыз.
2. PyCharm Terminal ашып, жоба бумасына өтіңіз.
3. Тәуелділіктерді орнатыңыз:
   ```powershell
   pip install -r requirements.txt
   ```
4. Қосымшаны іске қосыңыз:
   ```powershell
   python app.py
   ```
5. Браузерден `http://127.0.0.1:5000` ашыңыз.

## Render-ге жариялау

- GitHub репозиторийіне осы буманың ішіндегі файлдарды жүктеңіз (папканың ішіндегі файлдарды, ZIP-ті емес).
- Render → New → Web Service → GitHub репозиторийін таңдаңыз.
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Free instance сайтты көрсетуге жарайды, бірақ Render Free файлдық жүйесі уақытша: сервер ұйқыға кеткенде, қайта іске қосылғанда немесе redeploy болғанда SQLite-ке жазылған жаңа өтінімдер жоғалуы мүмкін. Тұрақты SQLite деректері үшін ақылы Render Web Service + Persistent Disk қажет. Render құжаттамасын қараңыз.

## Деректер базасы

`vacancies.db` — бастапқы курстық жұмыстағы SQLite базасының көшірмесі. Қосымша бар кестелерді ғана пайдаланады:
`Users`, `Companies`, `Vacancies`, `Skills`, `User_Skills`, `Vacancy_Skills`, `Applications`.

Кодта `CREATE TABLE` және `DROP TABLE` сұраныстары жоқ. Жаңа өтінім жіберілгенде қажет болса `Users` кестесіне пайдаланушы, ал `Applications` кестесіне өтінім қосылады.

`DB_PATH` орта айнымалысы арқылы деректер базасының орнын өзгертуге болады.
