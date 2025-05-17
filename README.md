# 🎲 Chaos Gacha App

This repository contains a Streamlit application that simulates a gacha system with different rarity levels.

---

## 📁 Structure

```
Chaos_Gacha/
├── Gacha_app.py
├── gachafiles/
│   ├── ability.txt
│   ├── item.txt
│   ├── familiar.txt
│   ├── trait.txt
│   └── skill.txt
```

---

##  Usage

1. Make sure you have Python 3.8 or higher.
2. Install Streamlit:

```bash
pip install streamlit
```

3. Run the application:

```bash
streamlit run Gacha_app.py
```

---

## 📦 Packaging as .exe

Use PyInstaller to convert the app into an executable:

```bash
pyinstaller --onefile ^
  --add-data "gachafiles;gachafiles" ^
  --add-data "original_gacha;original_gacha" ^
  --add-data "gacha_versions;gacha_versions" ^
  Gacha_app.py
```

> ⚠️ The `.txt` files in the `gachafiles/` folder are essential and must remain next to the `.exe` when distributing the app.

---

##  Online Version

You can try the web version of this app hosted on Streamlit Cloud:  
🔗 https://gachaapppy-9q6feaejxgdf4bbxwkkywx.streamlit.app/

---

## Credits

This project was inspired by the original work of **BronzDeck**.  
If you like this project, please consider supporting the original author:

-  [Patreon](https://www.patreon.com/BronzDeck)  
-  [GitHub](https://github.com/Bronzdeck/ChaosGacha)
