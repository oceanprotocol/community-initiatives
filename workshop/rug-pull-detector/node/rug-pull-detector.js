const { Web3 } = require("web3");
const fs = require("fs");
const path = require("path");
const Bignumber = require("bignumber.js");

// ============= CONFIGURATION =============
const CONFIG = {
  RPC_URL: "https://base.drpc.org",
  CONTRACTS: {
    USDC: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    WETH: "0x4200000000000000000000000000000000000006",
    ZERO: "0x0000000000000000000000000000000000000000",
    UNISWAP_V2_FACTORY: "0x8909Dc15e40173Ff4699343b6eB8132c65e18eC6",
  },
  OUTPUT_DIR: "/data/outputs",
};

// ============= CONTRACT ABIs =============
const ABIs = {
  uniswapV2Factory: [
    {
      constant: true,
      inputs: [
        { name: "tokenA", type: "address" },
        { name: "tokenB", type: "address" },
      ],
      name: "getPair",
      outputs: [{ name: "", type: "address" }],
      payable: false,
      stateMutability: "view",
      type: "function",
    },
    {
      constant: true,
      inputs: [],
      name: "allPairsLength",
      outputs: [{ name: "", type: "uint256" }],
      payable: false,
      stateMutability: "view",
      type: "function",
    },
    {
      constant: true,
      inputs: [{ name: "uint", type: "uint256" }],
      name: "allPairs",
      outputs: [{ name: "pair", type: "address" }],
      payable: false,
      stateMutability: "view",
      type: "function",
    },
  ],
  pair: [
    {
      constant: true,
      inputs: [],
      name: "token0",
      outputs: [{ name: "", type: "address" }],
      stateMutability: "view",
      type: "function",
    },
    {
      constant: true,
      inputs: [],
      name: "token1",
      outputs: [{ name: "", type: "address" }],
      stateMutability: "view",
      type: "function",
    },
    {
      constant: true,
      inputs: [],
      name: "totalSupply",
      outputs: [{ name: "", type: "uint256" }],
      stateMutability: "view",
      type: "function",
    },
    {
      constant: true,
      inputs: [],
      name: "getReserves",
      outputs: [
        { name: "reserve0", type: "uint112" },
        { name: "reserve1", type: "uint112" },
        { name: "blockTimestampLast", type: "uint32" },
      ],
      stateMutability: "view",
      type: "function",
    },
    {
      constant: true,
      inputs: [],
      name: "decimals",
      outputs: [{ name: "", type: "uint8" }],
      stateMutability: "view",
      type: "function",
    },
  ],
  token: [
    {
      constant: true,
      inputs: [],
      name: "name",
      outputs: [{ name: "", type: "string" }],
      stateMutability: "view",
      type: "function",
    },
    {
      constant: true,
      inputs: [],
      name: "symbol",
      outputs: [{ name: "", type: "string" }],
      stateMutability: "view",
      type: "function",
    },
    {
      constant: true,
      inputs: [],
      name: "totalSupply",
      outputs: [{ name: "", type: "uint256" }],
      stateMutability: "view",
      type: "function",
    },
    {
      constant: true,
      inputs: [],
      name: "decimals",
      outputs: [{ name: "", type: "uint8" }],
      stateMutability: "view",
      type: "function",
    },
  ],
};

// ============= WEB3 SETUP =============
const web3 = new Web3(CONFIG.RPC_URL);
const factoryContract = new web3.eth.Contract(
  ABIs.uniswapV2Factory,
  CONFIG.CONTRACTS.UNISWAP_V2_FACTORY
);

// ============= UTILITY FUNCTIONS =============
class TokenUtils {
  static async getTokenDecimals(tokenAddress) {
    if (tokenAddress === CONFIG.CONTRACTS.USDC) return 6;
    if (tokenAddress === CONFIG.CONTRACTS.WETH) return 18;

    const tokenContract = new web3.eth.Contract(ABIs.token, tokenAddress);
    return await tokenContract.methods.decimals().call();
  }

  static async getTokenTotalSupply(tokenAddress) {
    const tokenContract = new web3.eth.Contract(ABIs.token, tokenAddress);
    return await tokenContract.methods.totalSupply().call();
  }

  static async checkMintingAbility(tokenContract) {
    try {
      await tokenContract.methods.mint().call();
      return { mintable: true, supplyStatus: "NOT FIXED" };
    } catch {
      return { mintable: false, supplyStatus: "FIXED" };
    }
  }
}

// ============= CORE FUNCTIONS =============
class TokenAnalyzer {
  static async findPairByToken(tokenAddress) {
    try {
      const pairAddressUsdc = await factoryContract.methods
        .getPair(
          web3.utils.toChecksumAddress(tokenAddress),
          web3.utils.toChecksumAddress(CONFIG.CONTRACTS.USDC)
        )
        .call();

      if (pairAddressUsdc !== CONFIG.CONTRACTS.ZERO) {
        return { pairAddress: pairAddressUsdc, quoteToken: "USDC" };
      }

      const pairAddressWeth = await factoryContract.methods
        .getPair(
          web3.utils.toChecksumAddress(tokenAddress),
          web3.utils.toChecksumAddress(CONFIG.CONTRACTS.WETH)
        )
        .call();

      if (pairAddressWeth !== CONFIG.CONTRACTS.ZERO) {
        return { pairAddress: pairAddressWeth, quoteToken: "WETH" };
      }

      return null;
    } catch (error) {
      console.error("Error finding pair:", error);
      return null;
    }
  }

  static async calculateMarketCap(pairContract) {
    try {
      const [reserves, token0, token1] = await Promise.all([
        pairContract.methods.getReserves().call(),
        pairContract.methods.token0().call(),
        pairContract.methods.token1().call(),
      ]);

      const tokenTotalSupply = await TokenUtils.getTokenTotalSupply(token0);

      const reserve0Normalized = new Bignumber(reserves[0]).div(
        new Bignumber(10).pow(await TokenUtils.getTokenDecimals(token0))
      );
      const reserve1Normalized = new Bignumber(reserves[1]).div(
        new Bignumber(10).pow(await TokenUtils.getTokenDecimals(token1))
      );
      const pricePerToken = reserve1Normalized.div(reserve0Normalized);
      const totalSupplyNormalized = new Bignumber(tokenTotalSupply).div(
        new Bignumber(10).pow(await TokenUtils.getTokenDecimals(token0))
      );
      const marketCap = totalSupplyNormalized.multipliedBy(pricePerToken);

      return {
        reserves,
        token0,
        token1,
        pricePerToken: pricePerToken.toString(),
        totalSupplyNormalized: totalSupplyNormalized.toString(),
        marketCap: marketCap.toString(),
      };
    } catch (error) {
      console.log(`Error calculating market cap: ${error.message}`);
      return null;
    }
  }
}

// ============= REPORT GENERATION =============
class ReportGenerator {
  static async generateReport(inputTokenAddress) {
    const output = [];

    // Header
    output.push("=".repeat(80));
    output.push("🔍 TOKEN ANALYSIS REPORT");
    output.push("=".repeat(80));
    output.push(`Generated on: ${new Date().toLocaleString()}`);
    output.push("-".repeat(80));

    const pairInfo = await TokenAnalyzer.findPairByToken(inputTokenAddress);
    if (!pairInfo) {
      output.push(
        "Pair could not be found! Quit execution of the algorithm..."
      );
      return;
    }

    const pairAddress = pairInfo.pairAddress;
    const pairContract = new web3.eth.Contract(ABIs.pair, pairAddress);
    const token0 = await pairContract.methods.token0().call();
    const token1 = await pairContract.methods.token1().call();
    const inputToken =
      token0 !== CONFIG.CONTRACTS.USDC && token0 !== CONFIG.CONTRACTS.WETH
        ? token0
        : token1;
    const pairToken =
      token0 === CONFIG.CONTRACTS.USDC || token0 === CONFIG.CONTRACTS.WETH
        ? token0
        : token1;

    const tokenContract = new web3.eth.Contract(ABIs.token, inputToken);
    const pairTokenContract = new web3.eth.Contract(ABIs.token, pairToken);

    // Token Information
    output.push("\n📊 TOKEN INFORMATION");
    output.push("-".repeat(40));
    output.push(`Token Address: ${inputToken}`);
    const tokenName = await tokenContract.methods.name().call();
    const tokenSymbol = await tokenContract.methods.symbol().call();
    output.push(`Token Name: ${tokenName}`);
    output.push(`Token Symbol: ${tokenSymbol}`);

    // Pair Token Information
    output.push("\n🔄 PAIR TOKEN INFORMATION");
    output.push("-".repeat(40));
    output.push(`Pair Token Address: ${pairToken}`);
    const pairTokenName = await pairTokenContract.methods.name().call();
    const pairTokenSymbol = await pairTokenContract.methods.symbol().call();
    output.push(`Pair Token Name: ${pairTokenName}`);
    output.push(`Pair Token Symbol: ${pairTokenSymbol}`);

    // Liquidity Information
    output.push("\n💧 LIQUIDITY INFORMATION");
    output.push("-".repeat(40));
    output.push(`Liquidity Pair Address: ${pairAddress}`);
    const totalLpTokens = await pairContract.methods.totalSupply().call();
    output.push(`Total Supply of LP Tokens: ${totalLpTokens}`);

    // Market Analysis
    output.push("\n💰 MARKET ANALYSIS");
    output.push("-".repeat(40));
    const marketCapData = await TokenAnalyzer.calculateMarketCap(pairContract);
    if (marketCapData) {
      output.push(`Reserve ${tokenSymbol}: ${marketCapData.reserves[0]}`);
      output.push(`Reserve ${pairTokenSymbol}: ${marketCapData.reserves[1]}`);
      output.push(
        `Price per ${tokenSymbol}: ${marketCapData.pricePerToken} ${pairTokenSymbol}`
      );
      output.push(`Total Supply : ${marketCapData.totalSupplyNormalized}`);
      output.push(`Market Cap: ${marketCapData.marketCap} ${pairTokenSymbol}`);
    }

    // Supply Analysis
    output.push("\n🪄 SUPPLY ANALYSIS");
    output.push("-".repeat(40));

    const mintingStatus = await TokenUtils.checkMintingAbility(tokenContract);
    output.push(
      `Mint Status: ${mintingStatus.mintable ? "MINTABLE" : "NOT MINTABLE"}`
    );
    output.push(`Total Supply Status: ${mintingStatus.supplyStatus}`);

    output.push("\n" + "=".repeat(80));
    output.push("End of Report");
    output.push("=".repeat(80));

    // Save to file
    const outputText = output.join("\n");
    if (!fs.existsSync(CONFIG.OUTPUT_DIR)) {
      fs.mkdirSync(CONFIG.OUTPUT_DIR, { recursive: true });
    }

    const txtFilename = path.join(CONFIG.OUTPUT_DIR, "report.txt");
    fs.writeFileSync(txtFilename, outputText);

    // Display the report in terminal
    console.log(outputText);
    console.log(`✅ Output saved to ${txtFilename}\n`);
  }
}

// ============= MAIN EXECUTION =============
const inputTokenAddress = "0x768BE13e1680b5ebE0024C42c896E3dB59ec0149";
ReportGenerator.generateReport(inputTokenAddress).catch(console.error);
