# 🎲 Chaos Gacha App

This repository contains a Streamlit application that simulates a gacha system with different rarity levels, estimated luck, and a transcendent point system that affects bonus pulls.

---

## 📁 Project Structure

```
Chaos_Gacha/
├── Gacha_app.py               # Main Streamlit application
├── gacha_engine.py            # Gacha logic and draw processing
├── tracker.py                 # History and Transcendent Points management
├── logic/
│   ├── __init__.py
│   ├── gacha_engine.py        # (optional duplication for structure)
│   ├── tracker.py             # (optional duplication for structure)
├── gachafiles/                # Active editable gacha data files
│   ├── ability.txt
│   ├── item.txt
│   ├── familiar.txt
│   ├── trait.txt
│   └── skill.txt
├── Original_gachafiles/       # Original unmodified data files
├── gachafiles_versions/       # Timestamped backup versions of edited files
├── gacha_log/                 # Logs for repeats and transcendent points
│   ├── points.json
│   └── repeats.json
```

---

## 🧪 Usage

1. Make sure you have Python 3.8 or higher.
2. Install Streamlit:

```bash
pip install streamlit
pip install pyinstaller (Only for packaging .exe)
```

3. Run the application:

```bash
streamlit run Gacha_app.py
```

---

## 📦 Packaging as `.exe`

Use PyInstaller to convert the app into a standalone executable:

```bash
pyinstaller --onefile ^
  --add-data "gachafiles;gachafiles" ^
  --add-data "Original_gachafiles;Original_gachafiles" ^
  --add-data "gachafiles_versions;gachafiles_versions" ^
  --add-data "gacha_log;gacha_log" ^
  Gacha_app.py
----------(OPTIONAL/EASIER)----------
pyinstaller chaos_gacha.spec
```

> ⚠️ The `.txt` files in the `gachafiles/` folder and logs must remain next to the `.exe` when distributing the app.

---

## 🌐 Online Version

You can try the web version of this app hosted on Streamlit Cloud:  
🔗 https://gachaapppy-n4vmqf3krbmgzmbndci2yw.streamlit.app/

---

## 🙏 Credits

This project was inspired by the original work of **BronzDeck**.  
If you like this project, please consider supporting the original author:

- [Patreon](https://www.patreon.com/BronzDeck)  
- [GitHub](https://github.com/Bronzdeck/ChaosGacha)
