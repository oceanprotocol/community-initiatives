# 🧪 Uniswap V2 Liquidity Pool Analyzer

This tool is designed to analyze the token pairs characteristics using **Uniswap V2** smart contracts
on **Base chain**.

It inspects various characteristics of the tokens involved in each pair and prints key risk and health
indicators. The results are saved into a text report (`report.txt`) titled "TOKEN ANALYSIS REPORT".

## 🔍 What the Script Does

1. Connects to the Base chain via an RPC endpoint.
2. Interacts with the Uniswap V2 Factory contract.
3. Based on the input token address, it finds the corresponding pair backed up by WETH or USDC.
4. Uses ASI1 to analyze the results and provides an analysis report.

## 📊 Parameters Analyzed Per Token or Pair


| Parameter                   | Description                                               |
| --------------------------- | :--------------------------------------------------------:|
| `Token Name / Symbol`       | Identity of the token in the pair                         |
| `Total Supply of LP Tokens` | How many LP tokens exist for the pair                     |
| `Market Cap`                | Estimated based on liquidity pool reserves                |
| `Price per Token`           | Price of the token in the pair                            |
| `LP reserves`               | How much of each token is in the liquidity pool           |
| `Minting Ability`           | Can new tokens be minted? `MINTABLE` or `NOT MINTABLE`    |
| `Total Supply Status`       | If minting is disabled, it's `FIXED` otherwise `NOT FIXED`|
| `24H Volume Token0`         | 24-hour volume of the first token in the pair             |
| `24H Volume Token1`         | 24-hour volume of the second token in the pair            |
| `Ownership`                 | Check if the ownership is renounced                       |
| `Self-Destruct Risk`        | Check if the self-destruct opcode is found                |
| `Liquidity`                 | Check if the liquidity is fully unlocked                  |

## 📁 Input

- Input token address
- Uniswap V2 Factory contract address **(no need to update this if using uniswap v2 on Base)**
- Base chain RPC endpoint **(no need to update for running on base)**

**Note:**
- You can use [The graph](https://thegraph.com/explorer/subgraphs/D31gzGUtVNhHNdnxeELUBdch5rzDRm5cddvae9GzhCLu?view=Query) to fetch new token addresses
```
{
  tokens(first: 25) {
    id
    symbol
    name
    decimals
  }
}
``` 

## 📁 Output
- Console output with all parameters per pair
- ASI1 analysis report
- A text report saved as `report.txt` in the `data/outputs` directory

## How to run your algorithm on Ocean Node

```bash
1. Open Ocean Protocol vscode-extension
2. Select Algorithm file
3. Select Results folder
4. Press Start Compute Job
```

## 🔐 Disclaimer
This tool is for research and educational purposes. It is not a financial advice tool.
