-- Estrutura do banco do PetShop.
-- O app.py executa este arquivo sozinho ao iniciar (CREATE ... IF NOT EXISTS
-- nao apaga nada que ja exista). Voce tambem pode rodar no MySQL Workbench.

CREATE DATABASE IF NOT EXISTS petshop CHARACTER SET utf8mb4;

USE petshop;

CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    especie VARCHAR(50),
    raca VARCHAR(50),
    cliente_id INT NOT NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pet_id INT NOT NULL,
    servico VARCHAR(50) NOT NULL,
    data_hora DATETIME NOT NULL,
    valor DECIMAL(8,2) NOT NULL,
    observacao VARCHAR(255),
    status VARCHAR(20) NOT NULL DEFAULT 'Agendado',
    FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
);
