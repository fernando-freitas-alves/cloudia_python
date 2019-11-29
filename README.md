# cloudia_python
Teste para Desenvolvedores Python

# Fizz Buzz Twitter Bot
O projeto consiste em um bot para o Twitter que responda automaticamente mensagens direcionadas a ele com a lógica "Fizz Buzz".

## Requisitos:
```
Python 3
Flask 1.1.1
MySQL 8.0.18
mysql-connector-python 8.0.18
```

## Sobre as tecnologias usadas:
- [X] Flask como framework web da aplicação;
- [X] Requisições de API são tratadas utilizando arquitetura REST;
- [X] Banco de dados relacional MySQL.

## Funcionalidade:
- O bot recebe como entrada qualquer texto com até 280 caracteres e responde caso seja um número inteiro.
- A resposta é "Fizz" caso o número seja múltiplo de 3, "Buzz" caso o número seja múltiplo de 5 ou "FizzBuzz" caso seja múltiplo de 3 e de 5.
- O bot responde com a mesma entrada caso não se enquadre em nenhum caso descrito de "FizzBuzz".
- Ou responder com uma mensagem padrão caso a entrada não seja um número inteiro válido.
- O bot armazena as informações dos usuários que interagem com o bot;
- Assim como armazena também as mensagens trocadas com estes usuários.


## Como rodar:
```
python3 ./cloudia_python.py

Exemplos:
curl -iLH "Content-Type: application/json" -X POST -d '{"user": "user 1", "msg": ""}'    http://localhost:5000/
curl -iLH "Content-Type: application/json" -X POST -d '{"user": "user 2", "msg": "9"}'   http://localhost:5000/ # Fizz
curl -iLH "Content-Type: application/json" -X POST -d '{"user": "user 1", "msg": "10"}'  http://localhost:5000/ # Buzz
curl -iLH "Content-Type: application/json" -X POST -d '{"user": "1",      "msg": "15"}'  http://localhost:5000/ # FizzBuzz
curl -iLH "Content-Type: application/json" -X POST -d '{"user": "1",      "msg": "16"}'  http://localhost:5000/ # 16
curl -iLH "Content-Type: application/json" -X POST -d '{"user": "2",      "msg": "abc"}' http://localhost:5000/
curl -iLH "Content-Type: application/json" -X POST -d '{"user": "user 2", "msg": "3.5"}' http://localhost:5000/
curl -iLH "Content-Type: application/json" -X PUT  -d '{"user": "2",      "msg": "30"}'  http://localhost:5000/api/msgs/1
curl -iLH "Content-Type: application/json" -X POST -d '{"name": "user 3"}'               http://localhost:5000/api/users
curl -iLH "Content-Type: application/json" -X PUT  -d '{"name": "user 3 *"}'             http://localhost:5000/api/users/user%203
curl -iLX DELETE http://localhost:5000/api/msgs/2
curl -iLX DELETE http://localhost:5000/api/users/1

Acesse em um navegador:
- http://localhost:5000/api/msgs,  para verificar as mensagens gravadas
- http://localhost:5000/api/users, para verificar os usuários gravadas
- http://localhost:5000/api/msgs/1, para verificar a primeira mensagem gravada
- http://localhost:5000/api/users/2, para verificar o segundo usuário gravado
```

## A fazer:
- [ ] Testes unitários;
- [ ] Pytest como framework de teste unitário;
- [ ] Deploy da aplicação na AWS.
