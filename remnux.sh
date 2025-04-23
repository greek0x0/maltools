#!/bin/bash

if [ "$(id -u)" -eq 0 ]; then
    echo "[!] This script cannot be run as root. Please run as a regular user."
    exit 1
fi

check_alias_exists() {
    if grep -q "alias remnux=" ~/.zshrc; then
        return 0
    else
        return 1
    fi
}

check_docker_installed() {
    if command -v docker &> /dev/null; then
        return 0
    else
        return 1
    fi
}

check_malware_folder_exists() {
    if [ -d "$HOME/malware" ]; then
        return 0
    else
        return 1
    fi
}

check_setup_complete() {
    check_alias_exists && check_docker_installed && check_malware_folder_exists
}

install_docker() {
    echo "[*] Installing Docker and Docker Compose..."
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose
    sudo usermod -aG docker $USER
    sudo systemctl start docker
    sudo systemctl enable docker
}

setup_alias() {
    echo "[*] Setting up remnux alias in .zshrc..."
    echo 'alias remnux="docker run --rm -it -u remnux -v ~/malware:/home/remnux/files remnux/remnux-distro bash"' >> ~/.zshrc
}

create_malware_folder() {
    echo "[*] Creating malware directory..."
    mkdir -p ~/malware
}

run_remnux_container() {
    echo "[*] Running Remnux container..."
    sudo docker run --rm -it -u remnux -v ~/malware:/home/remnux/files remnux/remnux-distro bash
}

main() {
    if check_setup_complete; then
        echo "[*] Setup already complete. Running Remnux container..."
        run_remnux_container
    else
        echo "[*] Setup not complete. Proceeding with installation..."
        install_docker
        setup_alias
        create_malware_folder
        run_remnux_container
        echo "[*] The installation is complete. Please reboot your system for the Docker group changes to take effect."
    fi
}

main

