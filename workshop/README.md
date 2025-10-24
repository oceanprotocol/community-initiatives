# Ocean Protocol Hands-On Workshop

Welcome to the Ocean Protocol Workshop repository! This repository is designed to give you hands-on experience with Ocean Protocol's technology stack and help you build real-world applications.

## Prerequisites

### Required Equipment
- Laptop 
- VS Code installed on your laptop
- Ocean Protocol VS Code Extension installed from the [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=OceanProtocol.ocean-protocol-vscode-extension)

## Technical Requirements

Coding experience is mandatory. We will provide you with a basic template to get started. Template will be available in the workshop repository.



## [08.07 - 10.07] Workshop guidelines and steps

1. Clone this repository
```bash
git clone https://github.com/oceanprotocol/workshop
```
2. Open the repository in VS Code
3. Go to extensions tab and install the [Ocean Nodes VS Code Extension](https://marketplace.visualstudio.com/items?itemName=OceanProtocol.ocean-protocol-vscode-extension)
4. In order to create an asi1 api key
    1. Open [asi1](https://asi1.ai/) webpage and create an account.
    2. Go to developers tab
    3. Create an api key
    4. Save the api key somewhere safe
5. Open the **rug-pull-detector/python/rug-pull-detector.py** file and replace the api key with the one you created in the previous step
6. Now let's use the extension from VS Code to run the analyser.
    1. Click the ocean protocol icon in the extensions tab
    2. Select the algorithm file 
    `rug-pull-detector/python/rug-pull-detector.py`
    3. Select where you want the results to be saved 
    `any folder you want`
    4. Add the docker image name 
    `oceanprotocol/c2d_examples`
    5. Add the docker tag 
    `py-lite`
    6. Click the **Start Compute Job** button
7. Check the results


## Join Our Community

[Meet Ocean: Tokenized AI & Data](https://oceanprotocol.com/)
Stay connected with us through our community channels:
- Discord: [Join our Discord server](https://discord.gg/CQ2PQnKe)