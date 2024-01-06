const Web3 = require("web3");

const web3 = new Web3("http://localhost:8545");

const contractAddress = "TODO";

const contractABI = [
  {
    constant: true,
    inputs: [],
    name: "getInfo",
    outputs: [
      {
        name: "info",
        type: "string",
      },
    ],
    payable: false,
    stateMutability: "view",
    type: "function",
  },
];

const contract = new web3.eth.Contract(contractABI, contractAddress);
async function getClientFromContract() {
  try {
    const result = await contrant.methods.getClients.call();
    console.log("Wynik funkcji z kontraktu: ", result);
  } catch (error) {
    console.error("Błąd podczas odpytywania kontraktu: ", error);
  }
}

getClientFromContract();
