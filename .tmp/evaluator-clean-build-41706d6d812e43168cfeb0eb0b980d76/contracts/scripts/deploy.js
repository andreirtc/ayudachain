const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const network = hre.network.name;
  const chainId = (await hre.ethers.provider.getNetwork()).chainId;

  console.log(`=================================================`);
  console.log(`Deploying AyudaChainRegistry...`);
  console.log(`Network: ${network} (Chain ID: ${chainId})`);
  console.log(`Deployer Address: ${deployer.address}`);

  const AyudaChainRegistry = await hre.ethers.getContractFactory("AyudaChainRegistry");
  const registry = await AyudaChainRegistry.deploy();
  await registry.waitForDeployment();

  const contractAddress = await registry.getAddress();
  console.log(`AyudaChainRegistry deployed at: ${contractAddress}`);
  console.log(`=================================================`);

  // Export metadata (ABI, Address, Network)
  const artifactPath = path.join(__dirname, "../artifacts/contracts/AyudaChainRegistry.sol/AyudaChainRegistry.json");
  const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));

  const deploymentData = {
    network: network,
    chainId: Number(chainId),
    contractAddress: contractAddress,
    deployer: deployer.address,
    deployedAt: new Date().toISOString(),
    abi: artifact.abi
  };

  const sharedDir = path.join(__dirname, "../../shared/contracts");
  const backendDir = path.join(__dirname, "../../backend/app/blockchain");

  fs.mkdirSync(sharedDir, { recursive: true });
  fs.mkdirSync(backendDir, { recursive: true });

  fs.writeFileSync(path.join(sharedDir, "AyudaChainRegistry.json"), JSON.stringify(deploymentData, null, 2));
  fs.writeFileSync(path.join(backendDir, "AyudaChainRegistry.json"), JSON.stringify(deploymentData, null, 2));

  console.log(`Exported deployment metadata to /shared and /backend`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
