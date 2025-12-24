#!/bin/bash

echo "########################################"
echo "#    GemShot Ultimate - Mac/Linux Setup #"
echo "########################################"
echo ""

# 1. Check Python
if ! command -v python3 &> /dev/null
then
    echo "[!] Python3 no detectado."
    if command -v brew &> /dev/null
    then
        echo "[+] Detectado Homebrew. Instalando Python..."
        brew install python
    else
        echo "[X] Error: Por favor instala Python3 o Homebrew primero."
        exit 1
    fi
fi

echo "[+] Python3 detectado: $(python3 --version)"

# 2. Virtual Env (Optional but recommended on Mac)
if [ ! -d ".venv" ]; then
    echo "[+] Creando entorno virtual..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# 3. Install Requirements
echo "[+] Instalando dependencias..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# 4. Create Launcher
cat <<EOF > run_mac.command
#!/bin/bash
cd "\$(dirname "\$0")"
source .venv/bin/activate
python3 main.py
EOF
chmod +x run_mac.command

echo ""
echo "########################################"
echo "#      INSTALACION COMPLETADA          #"
echo "########################################"
echo "Para arrancar: Haz doble clic en 'run_mac.command'"
echo ""
