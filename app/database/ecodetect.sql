-- phpMyAdmin SQL Dump
-- version 5.2.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Tempo de geração: 13/11/2025 às 00:46
-- Versão do servidor: 8.0.36
-- Versão do PHP: 7.4.33

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `ecodetect`
--

-- --------------------------------------------------------

--
-- Estrutura para tabela `lixo`
--

CREATE TABLE `lixo` (
  `id` int NOT NULL,
  `data` timestamp NULL DEFAULT NULL,
  `imagem` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `latitude` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `longitude` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `rua` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `numero` int DEFAULT NULL,
  `cidade` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `estado` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `pais` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `cep` varchar(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `user_id` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Despejando dados para a tabela `lixo`
--

INSERT INTO `lixo` (`id`, `data`, `imagem`, `latitude`, `longitude`, `rua`, `numero`, `cidade`, `estado`, `pais`, `cep`, `user_id`) VALUES
(1, NULL, '/detect/detected_lixo_3_20251112_120635.jpg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 3),
(2, '2025-10-18 17:52:57', '/detect/detected_lixo_3_20251112_120651.jpg', '-23.590392972222222', '-46.634783999999996', 'Avenida Professor Noé Azevedo', NULL, 'São Paulo', 'SP', 'Brasil', '04119-000', 3);

-- --------------------------------------------------------

--
-- Estrutura para tabela `users`
--

CREATE TABLE `users` (
  `id` int NOT NULL,
  `username` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `image_url` varchar(255) DEFAULT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;

--
-- Despejando dados para a tabela `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `image_url`, `password`) VALUES
(1, 'teste', 'teste@gmail.com', NULL, '$2b$12$FJIk8bvi1LsvoHP2QD8xruaMRRANrbREC7tJ0BnMEVmK3w9zmjQq.'),
(2, 'GamesjogosJ', 'joguindoray@gmail.com', '/uploads/user_2_20251008_024459.png', '$2b$12$enFCJoTe3ctfwT2R6A/nJOgBIC5/WckmEM/zbPoB2QULY6bLSX/Qm'),
(3, 'Hitalo Chaves dos santos', 'hitalo@gmail.com', '/uploads/user_3_20251112_114043.png', '$2b$12$/RNpLKY050z.ClF2uZmAQ.z0AwE4uz54eEjVnI3LZaJpciYCRWZ5e'),
(6, 'Kaladin', 'kaladin@gmail.com', NULL, '$2b$12$E4715SKQI6hRFLuJvMQTe.Unom3xwPGcv9POjmqYaRLcSX.l7v9gu'),
(7, 'Guilherme', 'guilherme@gmail.com', '/uploads/user_7_20251008_024223.gif', '$2b$12$7HQL2H5LTeS4OWaFvCQzEOR//76ILPw7bKX2/LQehgEgJOEDIVROe'),
(8, 'Shruikan', 'shruikan@gmail.com', NULL, '$bcrypt-sha256$v=2,t=2b,r=12$ZHBCkO14Xq4lgGhcD3KPsu$HCK4UJfzsmcchqcoo/L2eSjaXQXbUBq'),
(9, 'Shruikan', 'Shruika22n@gmail.com', NULL, '$2b$12$VKs5th2YPmSVur3tOYNh2OlhnC8M0fgYRLHbgDdDHjle/8a5YQBzW'),
(10, 'Shruikan', 'Shruika@gmail.com', NULL, '$2b$12$pRg.0OFk2FonFguY8D0zo.GVJDHDHW8EFketieKbTxazGXd50VPYG'),
(11, 'Shruikan', 'Shruikddda@gmail.com', NULL, '$2b$12$9yoKstAb00tu6Qkp8LxZTuPn5JspOi3R2tS0wTbC5RZ4WWDIMVmjy'),
(12, 'Shruikan', 'Shruikssddda@gmail.com', NULL, '$2b$12$F7PwtTWzci5A5.Av6FSxCexJWSBBGSDSr4HQELOqESOq10PHuomNG'),
(13, 'Eragon', 'eragon@gmail.com', NULL, '$2b$12$gg5dATQCAFsDw1bWV3s9dea9dyTZnFC7T1ksNRqJgB5ZEAp73ITRS'),
(14, 'Shruikan', 'Shrudddikssddda@gmail.com', NULL, '$2b$12$LZXGuyXbF479b2Bs9DZ1u.uXGToO5i3mNPw8BUdgj1E1kYOh/Xclq'),
(15, 'Shruikan', 'asa@gmail.com', NULL, '$2b$12$lq2/TVo9okcF6Xcg.JmeZ.x/ytsyE7.yYutN/ETMzeotYdpNN/oWG'),
(16, 'Shruikan', 'dddd@gmail.com', NULL, '$2b$12$hHsxnwv2U6y4ZfeAHSqNIuSCLlwhGCvn3bZ6MlMQp4aE8Huo2kbqK'),
(17, 'Bruno Da Silva Pimentel', 'brunopimentel@gmail.com', NULL, '$2b$12$U4GHo9JcsbS75VLi1zvZEe0RYa9iwWjWA9p.lITQeCw1/bTT0Orpu');

--
-- Índices para tabelas despejadas
--

--
-- Índices de tabela `lixo`
--
ALTER TABLE `lixo`
  ADD PRIMARY KEY (`id`);

--
-- Índices de tabela `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT para tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `lixo`
--
ALTER TABLE `lixo`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de tabela `users`
--
ALTER TABLE `users`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
