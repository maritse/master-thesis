// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract TrainOrch {
    address public owner;
    // modifier to control only owner access
    modifier onlyOwner() {
        require(msg.sender == owner, "Tylko owner");
        _;
    }
    // constructor
    constructor() {
        owner = msg.sender;
    }
    // function to transfer ownership to another account
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "zero addr");
        owner = newOwner;
    }
    // --- Events ---
    event PublicKeyHashSubmitted(address indexed user, bytes32 hash);
    event RewardWithdrawn(address indexed trainer, uint256 amount);
    event RewardDistributed(uint256 sessionId, address indexed trainer, uint256 amount);
    event SessionCreated(uint256 sessionId, uint256 maxParticipants);
    event SessionFunded(uint256 sessionId, address indexed funder, uint256 amount);
    event TrainerRegistered(uint256 sessionId, address indexed trainer);
    event TrainingReady(uint256 sessionId, address[] trainers, uint256 rewardPool);
    event TrainingStarted(uint256 sessionId);
    event TrainingCompleted(uint256 sessionId, address[] trainers, uint256 totalReward);
    
    // mapping: address -> hash publicznego klucza
    mapping(address => bytes32) public keyHashes;

    /// Client is sending the hash of its public key
    function submitKeyHash(bytes32 keyHash) external {
        keyHashes[msg.sender] = keyHash;
        emit PublicKeyHashSubmitted(msg.sender, keyHash);
    }
    /// Pobranie hasha zarejestrowanego dla użytkownika
    function getKeyHash(address user) external onlyOwner view returns (bytes32) {
        return keyHashes[user];
    }
    // struktura prowadzenia całej sesji trenowania przez klientów
    struct TrainingSession {
        address funder;            // account funding rewards
        address[] trainers;        // clients registered
        bool completed;            // session completed
        bool started;              // if session started
        uint256 maxParticipants;   // session limit
        bool readyToStart;         // true if session reached maxParticipants
        uint256 rewardPool;        // funds allocated for rewards
    }

    mapping(uint256 => TrainingSession) public sessions; // sessionId -> session
    uint256 public currentSession;

    // Nagrody dla klientów po procesie uczenia
    mapping(address => uint256) public balances; // ETH to withdraw per trainer

    // Utworzenie nowej sesji przez server
    function createNewSession(uint256 maxParticipants) external onlyOwner payable {
        require(
            currentSession == 0 || sessions[currentSession].completed,
            "Current session not finished"
        );
  
        currentSession++;
        TrainingSession storage session = sessions[currentSession];
        session.maxParticipants = maxParticipants;
        session.completed = false;
        session.started = false;
        session.readyToStart = false;

        emit SessionCreated(currentSession, maxParticipants);
    }
    // start sesji trenowania
    function startSession() external onlyOwner {
        TrainingSession storage session = sessions[currentSession];
        require(!session.completed, "Session already completed");
        require(session.rewardPool > 0, "No funds provided");
        require(session.trainers.length == session.maxParticipants, "Not enough trainers");

        session.readyToStart = true;
        session.started = true;

        emit TrainingReady(currentSession, session.trainers, session.rewardPool);
        emit TrainingStarted(currentSession);
    }

    // rejestrowanie przez klienta swojej gotowości do uczenia
    // sprawdzenia czy są wolne miejsca
    function registerForTraining() external {
        TrainingSession storage session = sessions[currentSession];
        require(!session.completed, "Session already completed");
        require(!session.started, "Training already started");
        require(msg.sender != session.funder, "Funder cannot register as trainer");

        // sprawdzenie czy nie jest juz zarejestrowany
        for (uint i = 0; i < session.trainers.length; i++) {
            require(session.trainers[i] != msg.sender, "Already registered");
        }
        session.trainers.push(msg.sender);
        emit TrainerRegistered(currentSession, msg.sender);
    }

    // dodanie środków do puli uczenia przez właściciela modelu
    function fundSessionRewards() external payable {
        require(msg.value > 0, "Must send ETH to fund session");
        TrainingSession storage session = sessions[currentSession];
        require(!session.completed, "Session already completed");
        
        session.rewardPool += msg.value;
        session.funder = msg.sender;
        emit SessionFunded(currentSession, msg.sender, msg.value);
    }
    // wylistowanie wszystkich trenujących danej sesji poprzez Session ID
    function getTrainers(uint256 sessionId) external onlyOwner view returns (address[] memory) {
        return sessions[sessionId].trainers;
    }

    // zakończenie etapu trenowania
    // dodanie podziału wyników trenowania przez server
    function completeTrainingSession() external onlyOwner {
        TrainingSession storage session = sessions[currentSession];
        require(session.readyToStart, "Session not ready to start");
        require(!session.completed, "Session already completed");
        require(session.rewardPool > 0, "No funds for rewards");

        uint256 rewardPerTrainer = session.rewardPool / session.trainers.length;

        // Assign rewards to trainers - TODO
        for (uint i = 0; i < session.trainers.length; i++) {
            balances[session.trainers[i]] += rewardPerTrainer;
        }

        emit TrainingCompleted(currentSession, session.trainers, session.rewardPool);

        session.completed = true;
    }

    // dystrybucja srodkow z wygranej do klientow uczenia
    function distributeRewards(address[] calldata trainers, uint256[] calldata amounts) external onlyOwner {
        require(trainers.length == amounts.length, "Arrays must match");

        for (uint i = 0; i < trainers.length; i++) {
            uint256 amount = amounts[i];
            if (amount > 0) {
                require(address(this).balance >= amount, "insufficient contract balance");
                (bool success, ) = payable(trainers[i]).call{value: amount}("");
                require(success, "Transfer failed");
                emit RewardDistributed(currentSession, trainers[i], amount);
            }
        }
        // trainers list cleared for next session, rewardPool remains for server distribution
        TrainingSession storage session = sessions[currentSession];
        delete session.trainers;
    }
    receive() external payable {}
}