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

    // 1. Start esp_mcp server (python3 main.py in .ai/mcp/servers/esp_mcp)
    let repo_root = std::env::var("REPO_ROOT").unwrap_or_else(|_| ".".to_string());
    let mut child = Command::new("python3")
        .arg("main.py")
        .current_dir(format!("{}/.ai/mcp/servers/esp_mcp", repo_root))
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .context("failed to start esp_mcp server")?;

    let mut stdin = child.stdin.take().context("no stdin on esp_mcp process")?;
    let stdout = child.stdout.take().context("no stdout on esp_mcp process")?;
    let mut reader = BufReader::new(stdout);

    let mut next_id = 1u64;

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
