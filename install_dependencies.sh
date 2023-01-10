if ! command -v docker compose version &> /dev/null
then
    sudo apt-get install apt-transport-https ca-certificates curl gnupg release software-properties-common
#    sudo mkdir -p /etc/apt/keyrings
#    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
#    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-pluginsudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-pluginlinux/ubuntu   $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo apt-key fingerprint 0EBFCD88
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update

    ### Install docker and docker compose on Ubuntu
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
    exit
    if ! command -v docker compose --version &> /dev/null
    then
      echo "Could not install docker-compose"
    fi
fi