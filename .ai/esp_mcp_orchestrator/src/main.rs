use anyhow::{anyhow, Context, Result};
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::io::{BufRead, BufReader, Write};
use std::path::PathBuf;
use std::process::{Command, Stdio};

#[derive(Serialize)]
struct RpcRequest<'a> {
    jsonrpc: &'static str,
    id: u64,
    method: &'a str,
    #[serde(skip_serializing_if = "Option::is_none")]
    params: Option<serde_json::Value>,
}

#[derive(Deserialize, Debug)]
struct RpcError {
    code: i64,
    message: String,
}

#[derive(Deserialize, Debug)]
#[serde(untagged)]
enum RpcResponse {
    Result {
        jsonrpc: String,
        id: u64,
        result: serde_json::Value,
    },
    Error {
        jsonrpc: String,
        id: u64,
        error: RpcError,
    },
}

fn main() -> Result<()> {
    // PROJECT_PATH: default to current directory unless overridden.
    // We avoid canonicalize() here so that missing or lazily-created paths don't
    // cause an immediate hard failure; the esp_mcp server will validate the path.
    let project_path = std::env::var("ESP_PROJECT_PATH").unwrap_or_else(|_| ".".to_string());
    let project_path = PathBuf::from(project_path);

    // Optional serial port override (auto-detect if not set).
    let port_override = std::env::var("ESP_PORT").ok();

    // 1. Start esp_mcp server (python main.py in .ai/mcp/servers/esp_mcp)
    let repo_root = std::env::var("REPO_ROOT").unwrap_or_else(|_| ".".to_string());
    let server_dir = format!("{}/.ai/mcp/servers/esp_mcp", repo_root);

    // Prefer explicit interpreter passed from SCons/FBT; fall back to PATH search.
    let python_cmd = std::env::var("ESP_MCP_PYTHON").unwrap_or_else(|_| "python3".to_string());

    let mut child = Command::new(&python_cmd)
        .arg("main.py")
        .current_dir(&server_dir)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .with_context(|| format!(
            "failed to start esp_mcp server using '{}' in {}",
            python_cmd, server_dir
        ))?;

    let mut stdin = child.stdin.take().context("no stdin on esp_mcp process")?;
    let stdout = child.stdout.take().context("no stdout on esp_mcp process")?;
    let mut reader = BufReader::new(stdout);

    let mut next_id = 1u64;

    // Perform MCP initialize handshake before calling any tools.
    {
        let id = next_id;
        next_id += 1;

        let init_req = RpcRequest {
            jsonrpc: "2.0",
            id,
            method: "initialize",
            params: Some(json!({
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "sampling": {},
                    "logging": {},
                },
                "clientInfo": {
                    "name": "esp_mcp_orchestrator",
                    "version": "0.1.0",
                },
            })),
        };

        let line = serde_json::to_string(&init_req)? + "\n";
        stdin
            .write_all(line.as_bytes())
            .context("failed to write initialize request")?;
        stdin.flush().ok();

        let mut buf = String::new();
        reader
            .read_line(&mut buf)
            .context("failed to read initialize response line")?;

        if buf.trim().is_empty() {
            return Err(anyhow!("empty response from esp_mcp during initialize"));
        }

        let resp: RpcResponse = serde_json::from_str(&buf).context("failed to parse JSON-RPC initialize response")?;
        match resp {
            RpcResponse::Result { id: resp_id, .. } => {
                if resp_id != id {
                    return Err(anyhow!("mismatched id in initialize response: got {}, expected {}", resp_id, id));
                }
            }
            RpcResponse::Error { id: resp_id, error, .. } => {
                if resp_id != id {
                    return Err(anyhow!(
                        "mismatched id in initialize error response: got {}, expected {} ({:?})",
                        resp_id, id, error
                    ));
                }
                return Err(anyhow!("esp_mcp initialize error {}: {}", error.code, error.message));
            }
        }

        // Send notifications/initialized to complete MCP handshake.
        let initialized_notification = json!({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        });
        let line = serde_json::to_string(&initialized_notification)? + "\n";
        stdin
            .write_all(line.as_bytes())
            .context("failed to write notifications/initialized")?;
        stdin.flush().ok();
    }

    let mut call_tool = |name: &str, args: serde_json::Value| -> Result<serde_json::Value> {
        let id = next_id;
        next_id += 1;

        let req = RpcRequest {
            jsonrpc: "2.0",
            id,
            method: "tools/call",
            params: Some(json!({
                "name": name,
                "arguments": args,
            })),
        };

        let line = serde_json::to_string(&req)? + "\n";
        stdin
            .write_all(line.as_bytes())
            .context("failed to write request")?;
        stdin.flush().ok();

        let mut buf = String::new();
        reader
            .read_line(&mut buf)
            .context("failed to read response line")?;

        if buf.trim().is_empty() {
            return Err(anyhow!("empty response from esp_mcp"));
        }

        let resp: RpcResponse = serde_json::from_str(&buf).context("failed to parse JSON-RPC response")?;
        match resp {
            RpcResponse::Result { id: resp_id, result, .. } => {
                if resp_id != id {
                    return Err(anyhow!("mismatched id in response: got {}, expected {}", resp_id, id));
                }
                Ok(result)
            }
            RpcResponse::Error { id: resp_id, error, .. } => {
                if resp_id != id {
                    return Err(anyhow!(
                        "mismatched id in error response: got {}, expected {} ({:?})",
                        resp_id, id, error
                    ));
                }
                Err(anyhow!("esp_mcp error {}: {}", error.code, error.message))
            }
        }
    };

    println!(
        "[esp_mcp_orchestrator] Building ESP-IDF project at {}",
        project_path.display()
    );

    let build_args = json!({
        "project_path": project_path.to_string_lossy(),
    });

    let build_result = call_tool("build_esp_project", build_args)?;
    if let Some(arr) = build_result.as_array() {
        let stdout = arr.get(0).and_then(|v| v.as_str()).unwrap_or("");
        let stderr = arr.get(1).and_then(|v| v.as_str()).unwrap_or("");
        println!("--- esp_mcp build stdout ---\n{}\n------------------------------", stdout);
        if !stderr.trim().is_empty() {
            eprintln!("--- esp_mcp build stderr ---\n{}\n------------------------------", stderr);
        }
    } else {
        println!("build_esp_project result: {}", build_result);
    }

    println!("[esp_mcp_orchestrator] Flashing ESP32 via esp_mcp.flash_esp_project");

    let flash_args = if let Some(port) = port_override {
        json!({
            "project_path": project_path.to_string_lossy(),
            "port": port,
        })
    } else {
        json!({
            "project_path": project_path.to_string_lossy(),
        })
    };

    let flash_result = call_tool("flash_esp_project", flash_args)?;
    if let Some(arr) = flash_result.as_array() {
        let stdout = arr.get(0).and_then(|v| v.as_str()).unwrap_or("");
        let stderr = arr.get(1).and_then(|v| v.as_str()).unwrap_or("");
        println!("--- esp_mcp flash stdout ---\n{}\n------------------------------", stdout);
        if !stderr.trim().is_empty() {
            eprintln!("--- esp_mcp flash stderr ---\n{}\n------------------------------", stderr);
        }
    } else {
        println!("flash_esp_project result: {}", flash_result);
    }

    Ok(())
}
