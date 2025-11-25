#!/usr/bin/env node
import axios from "axios";

const BASE_URL = "http://127.0.0.1:8000";

console.error("MCP Shared Memory Server starting...");

// Send JSON-RPC message
function send(msg) {
  process.stdout.write(JSON.stringify(msg) + "\n");
}

// Handle stdin
let buffer = "";
process.stdin.on("data", (chunk) => {
  buffer += chunk.toString();
  let lines = buffer.split("\n");
  buffer = lines.pop() || "";

  for (const line of lines) {
    if (line.trim()) {
      handleMessage(line.trim());
    }
  }
});

async function handleMessage(line) {
  console.error("RECEIVED:", line);

  let msg;
  try {
    msg = JSON.parse(line);
  } catch (e) {
    console.error("Invalid JSON:", e.message);
    return;
  }

  // INITIALIZE
  if (msg.method === "initialize") {
    send({
      jsonrpc: "2.0",
      id: msg.id,
      result: {
        protocolVersion: "2024-11-05",
        serverInfo: {
          name: "sharedMemory",
          version: "1.0.0"
        },
        capabilities: {
          tools: {}
        }
      }
    });
    
    // Send initialized notification
    send({
      jsonrpc: "2.0",
      method: "notifications/initialized"
    });
    return;
  }

  // TOOLS LIST
  if (msg.method === "tools/list") {
    send({
      jsonrpc: "2.0",
      id: msg.id,
      result: {
        tools: [
          {
            name: "AddMemory",
            description: "Store memory in backend",
            inputSchema: {
              type: "object",
              required: ["project", "content"],
              properties: {
                project: { type: "string" },
                content: { type: "string" },
                tags: { type: "array", items: { type: "string" } }
              }
            }
          },
          {
            name: "SearchMemory",
            description: "Search stored memory",
            inputSchema: {
              type: "object",
              required: ["query"],
              properties: {
                query: { type: "string" },
                limit: { type: "number" }
              }
            }
          },
          {
            name: "UpdateMemory",
            description: "Update existing memory by ID",
            inputSchema: {
              type: "object",
              required: ["id"],
              properties: {
                id: { type: "string" },
                content: { type: "string" },
                tags: { type: "array", items: { type: "string" } }
              }
            }
          },
          {
            name: "DeleteMemory",
            description: "Delete memory by ID",
            inputSchema: {
              type: "object",
              required: ["id"],
              properties: {
                id: { type: "string" }
              }
            }
          },
          {
            name: "ListMemories",
            description: "List memories by project",
            inputSchema: {
              type: "object",
              properties: {
                project: { type: "string" },
                limit: { type: "number" }
              }
            }
          }
        ]
      }
    });
    return;
  }

  // TOOL EXECUTION
  if (msg.method === "tools/call") {
    const { name, arguments: input } = msg.params;

    try {
      let output = null;

      // CREATE
      if (name === "AddMemory") {
        const res = await axios.post(`${BASE_URL}/memory/add`, input);
        output = res.data;
      }

      // READ/SEARCH
      else if (name === "SearchMemory") {
        const res = await axios.get(`${BASE_URL}/memory/search`, { 
          params: { query: input.query, limit: input.limit || 10 }
        });
        output = res.data;
      }

      // LIST
      else if (name === "ListMemories") {
        const res = await axios.get(`${BASE_URL}/memory/list`, { 
          params: { project: input.project, limit: input.limit || 50 }
        });
        output = res.data;
      }

      // UPDATE
      else if (name === "UpdateMemory") {
        const { id, ...updateData } = input;
        const res = await axios.put(`${BASE_URL}/memory/update/${id}`, updateData);
        output = res.data;
      }

      // DELETE
      else if (name === "DeleteMemory") {
        const res = await axios.delete(`${BASE_URL}/memory/delete/${input.id}`);
        output = res.data;
      }

      else {
        throw new Error(`Unknown tool: ${name}`);
      }

      send({
        jsonrpc: "2.0",
        id: msg.id,
        result: {
          content: [
            {
              type: "text",
              text: JSON.stringify(output, null, 2)
            }
          ]
        }
      });
    } catch (err) {
      console.error("ERROR:", err.message);

      send({
        jsonrpc: "2.0",
        id: msg.id,
        error: {
          code: -32603,
          message: err.response?.data?.detail || err.message
        }
      });
    }
    return;
  }

  console.error("Unknown method:", msg.method);
}

console.error("Server ready. Storage:", BASE_URL);