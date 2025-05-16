# Chaos Gacha App

Este repositorio contiene una aplicación Streamlit para simular un sistema de gacha con distintos niveles de rareza.

## Estructura

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

## Uso

1. Asegúrate de tener Python 3.8 o superior.
2. Instala Streamlit:

```bash
pip install streamlit
```

3. Ejecuta la aplicación:

```bash
streamlit run Gacha_app.py
```

## Empaquetar como .exe

Usa PyInstaller para convertir la app en un ejecutable:

```bash
pyinstaller --onefile --add-data "gachafiles;gachafiles" Gacha_app.py
```

## Notas

- Los archivos `.txt` dentro de `gachafiles/` son esenciales y deben mantenerse junto al `.exe` si se distribuye como ejecutable.

---

### Credits
This project was inspired by the original work of **BronzDeck**.  
If you like this project, please consider supporting the original author on Patreon or visit his repository:

- Patreon: [https://www.patreon.com/BronzDeck](https://www.patreon.com/BronzDeck)  
- Repository: [https://github.com/Bronzdeck/ChaosGacha](https://github.com/Bronzdeck/ChaosGacha)

