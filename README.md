# NOVA X1 — Simulador de Drone

Simulador visual disponível em HTML/CSS/JavaScript e Kivy para Android.

## Web

Abra `index.html` ou execute:

```bash
python3 -m http.server 4173
```

No modo **Inspeção**, clique nos marcadores verdes ou na lista lateral para visualizar cada componente. Arraste o drone para alterar yaw e inclinação, ou use WASD/setas e Espaço.

## Android

O arquivo `main.py` contém o aplicativo Kivy. O APK é compilado automaticamente pelo GitHub Actions em `.github/workflows/android-apk.yml`.

Após o commit, abra a aba **Actions** no GitHub, execute **Build Android APK** e baixe o artefato `novax1-debug-apk`.
