# HTB - Lucky Dice Writeup

- **Category:** Misc  
- **Difficulty:** Very Easy  

---

# Introduction

Lucky Dice is a simple automation challenge.

The server shows multiple players rolling dice, and our job is to quickly tell which player has the highest total score.

The problem is:

- There are 100 rounds
- We only have 0.3 seconds to answer each round

So solving it manually is impossible.  
We need to create a Python bot to solve it automatically.

---

# Understanding the Challenge

When we connect to the server, the game starts.

Example output:

```text
Player 1: 4 5
Player 2: 2 2
Player 3: 6 5
```

Each number is a dice roll.

We must:

1. Add the dice values for every player
2. Find the player with the highest score
3. Send that player number back to the server

---

# Important Rules

## Number of Players

The challenge randomly chooses between 8 and 13 players.

```python
player_nr = random.randint(8, 13)
```

---

## Number of Dice

Each round increases the number of dice.

```python
dice_nr = rnd * 2 + 2
```

Examples:

| Round | Dice Count |
|---|---|
| 1 | 2 dice |
| 2 | 4 dice |
| 3 | 6 dice |
| 10 | 20 dice |
| 100 | 200 dice |

---

# Timeout Protection

The challenge checks how fast we answer.

```python
timeout = 0.3

start = time.time()
answer = input("> ")

if time.time() - start > timeout:
    print("Too slow!")
```

If we answer slower than 0.3 seconds, the game ends.

This is why we must automate it.

---

# Tie Rule

If two players have the same score:

> The LAST player wins.

Example:

```text
Player 3 -> 20
Player 7 -> 20
```

Winner:

```text
Player 7
```

---

# Solution Idea

Our script will:

1. Connect to the server
2. Read the game output
3. Find all player scores
4. Add the dice values
5. Find the highest score
6. Send the winner
7. Repeat 100 times

---

# Parsing the Player Data

Example line:

```text
Player 3: 6 5
```

We use regex:

```python
re.match(r"Player\s+(\d+):\s+([\d\s]+)", line)
```

This extracts:

| Part | Value |
|---|---|
| `group(1)` | Player number |
| `group(2)` | Dice values |

Example:

```python
group(1) -> "3"
group(2) -> "6 5"
```

---

# Converting Dice Into Numbers

This line:

```python
dice = list(map(int, m.group(2).split()))
```

Step-by-step:

## Step 1

```python
m.group(2)
```

Returns:

```python
"6 5"
```

---

## Step 2

```python
.split()
```

Splits by spaces:

```python
["6", "5"]
```

---

## Step 3

```python
map(int, ...)
```

Converts strings into integers:

```python
[6, 5]
```

---

## Step 4

```python
sum(dice)
```

Adds them:

```python
11
```

---
- **Provided 2 solution script using Pwn and Socket**
  
- Solving script using Pwm
  
```python
from pwn import *
import re 

HOST = "IP" #plave here IP
PORT = 123 #PLACE HERE PORT

def solve():
    io = remote(HOST,PORT)
    io.recvuntil(b"> ")
    io.sendline(b"1")

    for round in range(100):
        output = io.recvuntil(b"> ").decode()            
        print(output)

        players = []
        for line in output.split("\n"):
            m = re.match(r"Player\s+(\d+):\s+([\d\s]+)", line.strip())
            if m:
                player_num = int(m.group(1))
                dice = list(map(int,m.group(2).split()))
                players.append((player_num,sum(dice)))
        if not players:
            print("[!] Parsing error")
            return

        #Find the winner player 
        max_score = max(score for _, score in players)
        winner = None
        for player_num , score in players:
            if score == max_score:
                winner = player_num
        print(f"Round {round+1} → Player {winner}")

        io.sendline(str(winner).encode())
    #recieve flag:

    print(io.recvall().decode())

if __name__ == "__main__":
    solve()    

```
- solving script using socket

```python

    import socket
import sys
import re

HOST = "154.57.164.79"
PORT = 32195

def solve_challange():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((HOST,PORT))
    s.settimeout(10)    

    def recieve_until():
        data = b""
        while True:
            try:
                data_chunck = s.recv(4096)
                if not data_chunck:
                    break
                else:
                    data += data_chunck
                    if data.endswith(b"> "):
                        break
            except socket.timeout:
                break
        return data.decode("utf-8",errors="replace")

    #starting game 
    intro = recieve_until()
    print(intro)

    s.sendall(b"1\n")
    for round in range(100):
        output = recieve_until()
        print(output)

        lines = output.split("\n")
        players_order_score = []

        for line in lines:
            m = re.match(r"Player\s+(\d+):\s+([\d\s]+)",line.strip())
            if m:
                player_number = int(m.group(1))
                dice = list(map(int,m.group(2).strip().split()))
                players_order_score.append((player_number, sum(dice)))
        if not players_order_score:
            print("[!] Could not parse the player score!")
            print(repr(output))
            return 

        #Finding the winner player
        max_score = max(score for _, score in players_order_score)
        winner_player = None
        for player_number,score in players_order_score:
            if score == max_score:
                winner_player = player_number
        print(f" ----> Round {round+1}: winnner = player {winner_player} (score={max_score})")
        s.sendall(f"{winner_player}\n".encode())

    #recieve flag
    flag = b""
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            flag += chunk
    except:
        pass

    print("------flag----------")
    print(flag.decode("utf-8",errors="replace"))

    s.close()


if __name__ == "__main__":
    solve_challange()
    

```


# Flag
```text
HTB{r0LL1ng-1n-*******************}
```
