# Yobit's fee parser

## Installation

1. Install docker. E.g. for ubuntu: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04
2. Clone this repo(may require to install git before):
        git clone https://github.com/ggrafu/yobit_fees.git
3. Build docker image: 
        docker build -t yobit_bot .
4. Create directory to store CSV file (or use existing), e.g:
        mkdir /var/log/yobit
5. Run the container:
        docker run -d -v <the directory you've created>:/usr/src/app/export -e TELEGRAM_TOKEN=<token> --name yobit_bot yobit_bot
  
 ## Usage
 
 1. Start to chat with your bot
 2. Say '/subscribe' to get the updates of fees
 3. Say '/unsubscribe' to stop getting updates
