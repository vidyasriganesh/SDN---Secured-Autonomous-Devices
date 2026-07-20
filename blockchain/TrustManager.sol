// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TrustManager {

    address public admin;
    mapping(string => bool) private allowedDevices;

    event DeviceVerified(string mac, bool allowed, uint256 timestamp);

    constructor() {
        admin = msg.sender;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not authorised");
        _;
    }

    function addDevice(string memory mac) public onlyAdmin {
        allowedDevices[mac] = true;
    }

    function removeDevice(string memory mac) public onlyAdmin {
        allowedDevices[mac] = false;
    }

    function verifyDevice(string memory mac) public returns (bool) {
        bool result = allowedDevices[mac];
        emit DeviceVerified(mac, result, block.timestamp);
        return result;
    }

    function isDeviceAllowed(string memory mac) public view returns (bool) {
    return allowedDevices[mac];
    }
}

contract SDNVerifier {
    address public admin;
    address public authorisedSDN;

    event SignatureVerified(address signer, bool valid, uint256 timestamp);

    constructor(address _sdnAddress) {
        admin = msg.sender;
        authorisedSDN = _sdnAddress;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not authorised");
        _;
    }

    function updateSDN(address _newSDN) public onlyAdmin {
        authorisedSDN = _newSDN;
    }

    function verifySignature(bytes32 messageHash, bytes memory signature) public returns (bool) {
        address signer = recoverSigner(messageHash, signature);
        bool valid = (signer == authorisedSDN);
        emit SignatureVerified(signer, valid, block.timestamp);
        return valid;
    }

    function recoverSigner(bytes32 messageHash, bytes memory signature) internal pure returns (address) {
    bytes32 ethSignedHash = keccak256(
        abi.encodePacked("\x19Ethereum Signed Message:\n32", messageHash)
    );

    (bytes32 r, bytes32 s, uint8 v) = splitSignature(signature);
    return ecrecover(ethSignedHash, v, r, s);
}

    function splitSignature(bytes memory sig) internal pure returns (bytes32 r, bytes32 s, uint8 v) {
        require(sig.length == 65, "Invalid signature length");
        assembly {
            r := mload(add(sig, 32))
            s := mload(add(sig, 64))
            v := byte(0, mload(add(sig, 96)))
        }
    }
}