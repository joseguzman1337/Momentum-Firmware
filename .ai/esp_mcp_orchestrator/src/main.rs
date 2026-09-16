use anyhow::{anyhow, bail, Context, Result};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::process::{Child, ChildStdin, Command, Stdio};
use std::sync::mpsc::{self, Receiver, RecvTimeoutError};
use std::thread::{self, sleep};
use std::time::Duration;

const DEFAULT_TIMEOUT_SECS: u64 = 900;
const MAX_TIMEOUT_SECS: u64 = 3600;
const DEFAULT_FLASH_ATTEMPTS: u32 = 3;
const MAX_FLASH_ATTEMPTS: u32 = 5;
const MAX_RETRY_DELAY_SECS: f32 = 30.0;
const FLASH_CONFIRMATION: &str = "FLASH_VERIFIED_ESP_IMAGE";

#[derive(Debug)]
struct CommandFailure(String);

impl std::fmt::Display for CommandFailure {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        formatter.write_str(&self.0)
    }
}

impl std::error::Error for CommandFailure {}

#[derive(Serialize)]
struct RpcRequest<'a> {
    jsonrpc: &'static str,
    id: u64,
    method: &'a str,
    #[serde(skip_serializing_if = "Option::is_none")]
    params: Option<Value>,
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
        result: Value,
    },
    Error {
        jsonrpc: String,
        id: u64,
        error: RpcError,
    },
}

struct ChildGuard(Child);

impl Drop for ChildGuard {
    fn drop(&mut self) {
        let _ = self.0.kill();
        let _ = self.0.wait();
    }
}

struct RpcClient {
    stdin: ChildStdin,
    responses: Receiver<std::result::Result<String, String>>,
    next_id: u64,
    timeout: Duration,
}

impl RpcClient {
    fn request(&mut self, method: &str, params: Option<Value>) -> Result<Value> {
        let id = self.next_id;
        self.next_id += 1;
        let request = RpcRequest {
            jsonrpc: "2.0",
            id,
            method,
            params,
        };
        let line = serde_json::to_string(&request)? + "\n";
        self.stdin
            .write_all(line.as_bytes())
            .context("failed to write MCP request")?;
        self.stdin.flush().context("failed to flush MCP request")?;
        let line = match self.responses.recv_timeout(self.timeout) {
            Ok(Ok(line)) => line,
            Ok(Err(error)) => bail!("esp_mcp output reader failed: {error}"),
            Err(RecvTimeoutError::Timeout) => bail!(
                "esp_mcp timed out after {} seconds while handling {method}",
                self.timeout.as_secs()
            ),
            Err(RecvTimeoutError::Disconnected) => bail!("esp_mcp exited while handling {method}"),
        };
        if line.trim().is_empty() {
            bail!("empty response from esp_mcp during {method}");
        }
        match serde_json::from_str::<RpcResponse>(&line)
            .with_context(|| format!("invalid JSON-RPC response during {method}"))?
        {
            RpcResponse::Result {
                jsonrpc,
                id: response_id,
                result,
            } => {
                if jsonrpc != "2.0" {
                    bail!("unsupported JSON-RPC version {jsonrpc}");
                }
                if response_id != id {
                    bail!("mismatched response id: got {response_id}, expected {id}");
                }
                Ok(result)
            }
            RpcResponse::Error {
                jsonrpc,
                id: response_id,
                error,
            } => {
                if jsonrpc != "2.0" {
                    bail!("unsupported JSON-RPC version {jsonrpc}");
                }
                if response_id != id {
                    bail!("mismatched error id: got {response_id}, expected {id}");
                }
                bail!("esp_mcp error {}: {}", error.code, error.message)
            }
        }
    }

    fn notify_initialized(&mut self) -> Result<()> {
        let line = serde_json::to_string(
            &json!({"jsonrpc": "2.0", "method": "notifications/initialized"}),
        )? + "\n";
        self.stdin.write_all(line.as_bytes())?;
        self.stdin.flush()?;
        Ok(())
    }

    fn call_tool(&mut self, name: &str, arguments: Value) -> Result<Value> {
        let result = self.request(
            "tools/call",
            Some(json!({"name": name, "arguments": arguments})),
        )?;
        validate_tool_result(name, result)
    }
}

fn main() -> Result<()> {
    let project_path =
        validated_project_path(&std::env::var("ESP_PROJECT_PATH").unwrap_or_else(|_| ".".into()))?;
    let port_override = std::env::var("ESP_PORT")
        .ok()
        .or_else(|| std::env::var("ESPPORT").ok())
        .map(|port| validate_port(&port).map(str::to_owned))
        .transpose()?;
    let port_filter = std::env::var("ESP_PORT_FILTER")
        .ok()
        .or_else(|| std::env::var("ESPPORTFILTER").ok())
        .map(|filter| validate_filter(&filter).map(str::to_owned))
        .transpose()?;
    let (filter_vid, filter_pid) = parse_filter(port_filter.as_deref());
    let timeout = Duration::from_secs(bounded_u64_env(
        "ESP_MCP_REQUEST_TIMEOUT",
        DEFAULT_TIMEOUT_SECS,
        1,
        MAX_TIMEOUT_SECS,
    )?);
    let repo_root = PathBuf::from(std::env::var("REPO_ROOT").unwrap_or_else(|_| ".".into()));
    let server_dir = repo_root.join(".ai/mcp/servers/esp_mcp");
    if !server_dir.join("main.py").is_file() {
        bail!("esp_mcp server is missing at {}", server_dir.display());
    }
    let python = std::env::var("ESP_MCP_PYTHON").unwrap_or_else(|_| "python3".into());
    let mut child = Command::new(&python)
        .arg("main.py")
        .current_dir(&server_dir)
        .env("ESP_MCP_FLASH_RETRIES", "1")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .with_context(|| {
            format!(
                "failed to start esp_mcp using {python:?} in {}",
                server_dir.display()
            )
        })?;
    let stdin = child.stdin.take().context("esp_mcp stdin unavailable")?;
    let stdout = child.stdout.take().context("esp_mcp stdout unavailable")?;
    let (sender, responses) = mpsc::channel();
    thread::spawn(move || {
        for line in BufReader::new(stdout).lines() {
            if sender
                .send(line.map_err(|error| error.to_string()))
                .is_err()
            {
                break;
            }
        }
    });
    let _guard = ChildGuard(child);
    let mut client = RpcClient {
        stdin,
        responses,
        next_id: 1,
        timeout,
    };
    client.request(
        "initialize",
        Some(json!({
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "esp_mcp_orchestrator", "version": env!("CARGO_PKG_VERSION")}
        })),
    )?;
    client.notify_initialized()?;

    println!("[esp_mcp_orchestrator] Building {}", project_path.display());
    print_command_result(
        "build",
        &client.call_tool("build_esp_project", json!({"project_path": project_path}))?,
    );
    let selected_port = match port_override {
        Some(port) => Some(port),
        None => {
            let args = if filter_vid.is_some() || filter_pid.is_some() {
                json!({"vid": filter_vid.map(|v| format!("0x{v:04x}")), "pid": filter_pid.map(|v| format!("0x{v:04x}"))})
            } else {
                json!({})
            };
            extract_first_port(&client.call_tool("list_esp_serial_ports", args)?)
                .map(|port| validate_port(&port).map(str::to_owned))
                .transpose()?
        }
    };
    let mut flash_args = json!({"project_path": project_path});
    if let Some(port) = selected_port {
        flash_args["port"] = json!(port);
    } else if let Some(filter) = port_filter {
        flash_args["port_filter"] = json!(filter);
    }
    let confirmation = require_flash_confirmation()?;
    flash_args["confirm"] = json!(confirmation);
    flash_args["dry_run"] = json!(false);
    let attempts = bounded_u32_env(
        "ESP_MCP_FLASH_RETRIES",
        DEFAULT_FLASH_ATTEMPTS,
        1,
        MAX_FLASH_ATTEMPTS,
    )?;
    let delay = bounded_f32_env("ESP_MCP_FLASH_RETRY_DELAY", 1.0, 0.0, MAX_RETRY_DELAY_SECS)?;
    let result = retry(
        attempts,
        Duration::from_secs_f32(delay),
        |error| error.downcast_ref::<CommandFailure>().is_some(),
        || client.call_tool("flash_esp_project", flash_args.clone()),
    )?;
    print_command_result("flash", &result);
    Ok(())
}

fn require_flash_confirmation() -> Result<&'static str> {
    match std::env::var("ESP_MCP_FLASH_CONFIRM") {
        Ok(value) if value == FLASH_CONFIRMATION => Ok(FLASH_CONFIRMATION),
        _ => bail!(
            "ESP flash refused: set ESP_MCP_FLASH_CONFIRM={FLASH_CONFIRMATION} after verifying the image and target"
        ),
    }
}

fn validate_tool_result(name: &str, result: Value) -> Result<Value> {
    if result.get("isError").and_then(Value::as_bool) == Some(true) {
        bail!(
            "{name} reported an MCP tool error: {}",
            content_text(&result)
        );
    }
    let payload = if let Some(structured) = result.get("structuredContent") {
        structured.get("result").unwrap_or(structured).clone()
    } else if result.get("content").is_some() {
        let text = content_text(&result);
        serde_json::from_str(&text).unwrap_or(Value::String(text))
    } else {
        result
    };
    if let Some(values) = payload.as_array() {
        let stderr = values.get(1).and_then(Value::as_str).unwrap_or("");
        if stderr.contains("ESP command failed with exit code") {
            return Err(CommandFailure(format!("{name} command failed: {stderr}")).into());
        }
    }
    Ok(payload)
}

fn content_text(value: &Value) -> String {
    value
        .get("content")
        .and_then(Value::as_array)
        .map(|items| {
            items
                .iter()
                .filter_map(|item| item.get("text").and_then(Value::as_str))
                .collect::<Vec<_>>()
                .join("\n")
        })
        .unwrap_or_else(|| value.to_string())
}

fn extract_first_port(value: &Value) -> Option<String> {
    value
        .as_array()?
        .first()?
        .as_str()?
        .lines()
        .find_map(|line| line.split_whitespace().next())
        .filter(|port| !port.is_empty())
        .map(str::to_owned)
}

fn print_command_result(label: &str, value: &Value) {
    if let Some(values) = value.as_array() {
        println!(
            "--- esp_mcp {label} stdout ---\n{}\n------------------------------",
            values.first().and_then(Value::as_str).unwrap_or("")
        );
        let stderr = values.get(1).and_then(Value::as_str).unwrap_or("");
        if !stderr.trim().is_empty() {
            eprintln!("--- esp_mcp {label} stderr ---\n{stderr}\n------------------------------");
        }
    } else {
        println!("{label} result: {value}");
    }
}

fn validated_project_path(raw: &str) -> Result<PathBuf> {
    if raw.trim().is_empty() || raw.as_bytes().contains(&0) {
        bail!("ESP_PROJECT_PATH is invalid");
    }
    let path = Path::new(raw)
        .canonicalize()
        .with_context(|| format!("ESP project does not exist: {raw}"))?;
    if !path.is_dir() {
        bail!("ESP project is not a directory: {}", path.display());
    }
    Ok(path)
}

fn validate_port(raw: &str) -> Result<&str> {
    if raw.is_empty() || raw.len() > 255 || raw.chars().any(|c| c.is_control() || c.is_whitespace())
    {
        bail!("invalid ESP serial port");
    }
    Ok(raw)
}

fn validate_filter(raw: &str) -> Result<&str> {
    if raw.is_empty()
        || raw.len() > 128
        || !raw
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || "=,; xX_-".contains(c))
    {
        bail!("invalid ESP port filter");
    }
    let (vid, pid) = parse_filter(Some(raw));
    if vid.is_none() && pid.is_none() {
        bail!("port filter must contain a valid vid= or pid=");
    }
    Ok(raw)
}

fn parse_filter(raw: Option<&str>) -> (Option<u16>, Option<u16>) {
    let mut vid = None;
    let mut pid = None;
    for part in raw.unwrap_or("").split([',', ';', ' ']) {
        if let Some(value) = part.strip_prefix("vid=") {
            vid = parse_usb_id(value);
        }
        if let Some(value) = part.strip_prefix("pid=") {
            pid = parse_usb_id(value);
        }
    }
    (vid, pid)
}

fn parse_usb_id(raw: &str) -> Option<u16> {
    let value = raw.trim();
    value
        .strip_prefix("0x")
        .or_else(|| value.strip_prefix("0X"))
        .map(|hex| u16::from_str_radix(hex, 16).ok())
        .unwrap_or_else(|| value.parse().ok())
}

fn bounded_u32_env(name: &str, default: u32, min: u32, max: u32) -> Result<u32> {
    let value = std::env::var(name)
        .ok()
        .map(|raw| {
            raw.parse::<u32>()
                .with_context(|| format!("invalid {name}"))
        })
        .transpose()?
        .unwrap_or(default);
    if !(min..=max).contains(&value) {
        bail!("{name} must be between {min} and {max}");
    }
    Ok(value)
}

fn bounded_u64_env(name: &str, default: u64, min: u64, max: u64) -> Result<u64> {
    let value = std::env::var(name)
        .ok()
        .map(|raw| {
            raw.parse::<u64>()
                .with_context(|| format!("invalid {name}"))
        })
        .transpose()?
        .unwrap_or(default);
    if !(min..=max).contains(&value) {
        bail!("{name} must be between {min} and {max}");
    }
    Ok(value)
}

fn bounded_f32_env(name: &str, default: f32, min: f32, max: f32) -> Result<f32> {
    let value = std::env::var(name)
        .ok()
        .map(|raw| {
            raw.parse::<f32>()
                .with_context(|| format!("invalid {name}"))
        })
        .transpose()?
        .unwrap_or(default);
    if !value.is_finite() || value < min || value > max {
        bail!("{name} must be between {min} and {max}");
    }
    Ok(value)
}

fn retry<T>(
    attempts: u32,
    delay: Duration,
    retryable: impl Fn(&anyhow::Error) -> bool,
    mut operation: impl FnMut() -> Result<T>,
) -> Result<T> {
    let mut last_error = None;
    for attempt in 1..=attempts {
        match operation() {
            Ok(value) => return Ok(value),
            Err(error) => {
                eprintln!("[esp_mcp_orchestrator] attempt {attempt}/{attempts} failed: {error:#}");
                if !retryable(&error) {
                    return Err(error);
                }
                last_error = Some(error);
                if attempt < attempts && !delay.is_zero() {
                    sleep(delay);
                }
            }
        }
    }
    Err(last_error.unwrap_or_else(|| anyhow!("operation had no attempts")))
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::Cell;

    #[test]
    fn rejects_mcp_tool_error() {
        let err = validate_tool_result(
            "flash",
            json!({"isError": true, "content": [{"type":"text", "text":"boom"}]}),
        )
        .unwrap_err();
        assert!(err.to_string().contains("boom"));
    }

    #[test]
    fn rejects_command_failure_inside_success_response() {
        let err = validate_tool_result("build", json!({"content": [{"type":"text", "text":"[\"out\",\"ESP command failed with exit code 2.\\nnope\"]"}]})).unwrap_err();
        assert!(err.to_string().contains("exit code 2"));
    }

    #[test]
    fn accepts_success_tuple_and_structured_content() {
        assert_eq!(
            validate_tool_result(
                "build",
                json!({"structuredContent":{"result":["ok", "warning"]}})
            )
            .unwrap(),
            json!(["ok", "warning"])
        );
    }

    #[test]
    fn retry_is_strictly_bounded() {
        let calls = Cell::new(0);
        let result: Result<()> = retry(
            3,
            Duration::ZERO,
            |_| true,
            || {
                calls.set(calls.get() + 1);
                bail!("failed")
            },
        );
        assert!(result.is_err());
        assert_eq!(calls.get(), 3);
    }

    #[test]
    fn retry_stops_immediately_for_protocol_or_timeout_errors() {
        let calls = Cell::new(0);
        let result: Result<()> = retry(
            3,
            Duration::ZERO,
            |error| error.downcast_ref::<CommandFailure>().is_some(),
            || {
                calls.set(calls.get() + 1);
                bail!("request timed out")
            },
        );
        assert!(result.is_err());
        assert_eq!(calls.get(), 1);
    }

    #[test]
    fn validates_ports_and_filters() {
        assert!(validate_port("/dev/cu.usbmodem01").is_ok());
        assert!(validate_port("/dev/cu/x\n--evil").is_err());
        assert_eq!(
            parse_filter(Some("vid=0x303a,pid=2")),
            (Some(0x303a), Some(2))
        );
        assert!(validate_filter("vid=0x303a,pid=2").is_ok());
        assert!(validate_filter("anything; rm -rf").is_err());
    }

    #[test]
    fn environment_bounds_reject_excessive_attempts() {
        std::env::set_var("TEST_ATTEMPTS", "100");
        assert!(bounded_u32_env("TEST_ATTEMPTS", 3, 1, 5).is_err());
        std::env::remove_var("TEST_ATTEMPTS");
    }

    #[test]
    fn flash_requires_exact_environment_confirmation() {
        std::env::remove_var("ESP_MCP_FLASH_CONFIRM");
        assert!(require_flash_confirmation().is_err());
        std::env::set_var("ESP_MCP_FLASH_CONFIRM", "wrong");
        assert!(require_flash_confirmation().is_err());
        std::env::set_var("ESP_MCP_FLASH_CONFIRM", FLASH_CONFIRMATION);
        assert_eq!(require_flash_confirmation().unwrap(), FLASH_CONFIRMATION);
        std::env::remove_var("ESP_MCP_FLASH_CONFIRM");
    }
}
