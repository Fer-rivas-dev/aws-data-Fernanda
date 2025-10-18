# aws-data-Fernanda
# Setup Completo EC2 Ubuntu 24.04

Este README guía la instalación de **Python 3.12**, **entorno virtual**, **Docker**, **Docker Compose**, y **Jupyter Notebook** en una instancia de Ubuntu 24.04 en AWS EC2.

---

## 📦 Dependencias

Las herramientas que se instalarán:

- **Python 3.12**: lenguaje de programación.
- **Entorno virtual (venv)**: aislar proyectos Python.
- **pip**: gestor de paquetes de Python.
- **Docker**: contenedores ligeros.
- **Docker Compose**: orquestación de contenedores.
- **Jupyter Notebook / JupyterLab**: notebooks interactivos de Python.

---

## ⚙️ Cómo las instalamos

A continuación se muestra un **script completo comentado**, que puedes copiar en `setup_ec2.sh` y ejecutar en tu EC2:

```bash
#!/bin/bash
# ==============================================================
# Setup completo para EC2 Ubuntu 24.04
# Instala: Python 3.12, entorno virtual, Docker, Docker Compose, Jupyter Notebook
# ==============================================================

# 1️⃣ Actualizar el sistema
echo "==> Actualizando el sistema..."
sudo apt update && sudo apt upgrade -y

# 2️⃣ Instalar Python 3.12 y herramientas necesarias
echo "==> Instalando Python 3.12 y herramientas..."
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip
python3.12 --version  # Verificar instalación

# 3️⃣ Crear un entorno virtual
echo "==> Creando entorno virtual 'myenv'..."
python3.12 -m venv ~/myenv

# Instrucción para activar el entorno virtual
echo "==> Para activar el entorno virtual, ejecuta:"
echo "source ~/myenv/bin/activate"

# 4️⃣ Instalar dependencias de Docker
echo "==> Instalando dependencias necesarias para Docker..."
sudo apt install -y ca-certificates curl gnupg lsb-release

# 5️⃣ Configurar el repositorio oficial de Docker
echo "==> Configurando repositorio de Docker..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 6️⃣ Instalar Docker y Docker Compose
echo "==> Instalando Docker y Docker Compose..."
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 7️⃣ Verificar instalación de Docker
echo "==> Verificando Docker..."
sudo docker run hello-world
docker --version
docker compose version

# 8️⃣ Permitir usar Docker sin sudo (opcional)
echo "==> Para usar Docker sin sudo, ejecuta:"
echo "sudo usermod -aG docker \$USER"
echo "Luego cierra sesión y vuelve a entrar para aplicar los cambios."

# 9️⃣ Activar entorno virtual
echo "==> Activando entorno virtual..."
source ~/myenv/bin/activate

# 10️⃣ Instalar Jupyter Notebook y JupyterLab dentro del entorno virtual
echo "==> Instalando Jupyter Notebook y JupyterLab..."
pip install --upgrade pip
pip install notebook jupyterlab

# 11️⃣ Instrucciones para ejecutar Jupyter Notebook
echo "==> Para ejecutar Jupyter Notebook en EC2:"
echo "jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser"
echo "Luego abre tu navegador en la IP pública de tu EC2 usando el token mostrado en la terminal."

# 12️⃣ Mensaje final
echo "✅ Setup completado. Recuerda activar tu entorno virtual antes de trabajar con Python y Jupyter."

