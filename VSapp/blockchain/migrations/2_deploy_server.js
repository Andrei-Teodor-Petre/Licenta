const Server = artifacts.require("../contracts/Server.sol");

module.exports = function(deployer) {
  deployer.deploy(Server);
};
