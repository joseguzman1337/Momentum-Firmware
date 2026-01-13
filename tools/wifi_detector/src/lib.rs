use std::fmt;
use std::fs;
use std::io;
use std::path::{Path, PathBuf};
use std::time::Duration;

use rusb::{Device, DeviceDescriptor, GlobalContext};
use serialport::{SerialPortInfo, SerialPortType};
use thiserror::Error;

const VID_ESPRESSIF: u16 = 0x303A;
const PID_ESP32S2_ROM_BOOTLOADER: u16 = 0x0002;
const VID_CMSIS_DAP: u16 = 0x1D50;
const PID_CMSIS_DAP: u16 = 0x6018;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum WifiDevboardState {
    Bootloader {
        vid: u16,
        pid: u16,
        bus: u8,
        address: u8,
    },
    CmsisDap {
        vid: u16,
        pid: u16,
        bus: u8,
        address: u8,
    },
    Esp32S2Firmware {
        vid: u16,
        pid: u16,
        bus: u8,
        address: u8,
        product: String,
        manufacturer: String,
    },
    SerialOnly {
        port_name: String,
        sysfs_path: PathBuf,
        vid: Option<u16>,
        pid: Option<u16>,
        product: Option<String>,
        manufacturer: Option<String>,
    },
    GhostUsb {
        sysfs_path: PathBuf,
    },
    NotDetected,
}

impl fmt::Display for WifiDevboardState {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            WifiDevboardState::Bootloader { vid, pid, bus, address } => {
                write!(
                    f,
                    "Bootloader: VID={:#06x}, PID={:#06x}, bus={}, addr={}",
                    vid, pid, bus, address
                )
            }
            WifiDevboardState::CmsisDap { vid, pid, bus, address } => {
                write!(
                    f,
                    "CMSIS-DAP: VID={:#06x}, PID={:#06x}, bus={}, addr={}",
                    vid, pid, bus, address
                )
            }
            WifiDevboardState::Esp32S2Firmware {
                vid,
                pid,
                bus,
                address,
                product,
                manufacturer,
            } => {
                write!(
                    f,
                    "ESP32-S2 firmware: VID={:#06x}, PID={:#06x}, bus={}, addr={}, mfg='{}', product='{}'",
                    vid, pid, bus, address, manufacturer, product
                )
            }
            WifiDevboardState::SerialOnly {
                port_name,
                sysfs_path,
                vid,
                pid,
                product,
                manufacturer,
            } => {
                write!(
                    f,
                    "Serial-only ESP32-S2: port={}, sysfs={}, VID={:?}, PID={:?}, mfg={:?}, product={:?}",
                    port_name,
                    sysfs_path.display(),
                    vid,
                    pid,
                    manufacturer,
                    product
                )
            }
            WifiDevboardState::GhostUsb { sysfs_path } => {
                write!(
                    f,
                    "Ghost USB device (partial enumeration or error) at {}",
                    sysfs_path.display()
                )
            }
            WifiDevboardState::NotDetected => write!(f, "WiFi Devboard not detected"),
        }
    }
}

#[derive(Debug, Error)]
pub enum DetectionError {
    #[error("USB enumeration error: {0}")]
    Usb(#[from] rusb::Error),
    #[error("Serial enumeration error: {0}")]
    Serial(#[from] serialport::Error),
    #[error("IO error: {0}")]
    Io(#[from] io::Error),
}

pub fn detect_wifi_devboard() -> Result<WifiDevboardState, DetectionError> {
    let usb_matches = detect_via_usb()?;
    if let Some(best) = pick_best_usb_match(&usb_matches) {
        return Ok(best);
    }

    let serial_matches = detect_via_serial()?;
    if let Some(best) = pick_best_serial_match(&serial_matches) {
        return Ok(best);
    }

    if let Some(ghost) = detect_ghost_usb()? {
        return Ok(ghost);
    }

    Ok(WifiDevboardState::NotDetected)
}

fn pick_best_usb_match(states: &[WifiDevboardState]) -> Option<WifiDevboardState> {
    for s in states {
        if matches!(s, WifiDevboardState::Bootloader { .. }) {
            return Some(s.clone());
        }
    }
    for s in states {
        if matches!(s, WifiDevboardState::CmsisDap { .. }) {
            return Some(s.clone());
        }
    }
    for s in states {
        if matches!(s, WifiDevboardState::Esp32S2Firmware { .. }) {
            return Some(s.clone());
        }
    }
    None
}

fn pick_best_serial_match(states: &[WifiDevboardState]) -> Option<WifiDevboardState> {
    states.iter().cloned().next()
}

fn detect_via_usb() -> Result<Vec<WifiDevboardState>, DetectionError> {
    let mut matches = Vec::new();
    let devices = rusb::devices()?;
    for device in devices.iter() {
        if let Some(state) = classify_usb_device(&device)? {
            matches.push(state);
        }
    }
    Ok(matches)
}

fn classify_usb_device(device: &Device<GlobalContext>) -> Result<Option<WifiDevboardState>, DetectionError> {
    let desc = device.device_descriptor()?;
    let vid = desc.vendor_id();
    let pid = desc.product_id();
    let bus = device.bus_number();
    let address = device.address();

    let (manufacturer, product) = read_usb_strings(device, &desc);

    if vid == VID_ESPRESSIF && pid == PID_ESP32S2_ROM_BOOTLOADER {
        return Ok(Some(WifiDevboardState::Bootloader {
            vid,
            pid,
            bus,
            address,
        }));
    }

    let product_lower = product.to_lowercase();
    if (vid == VID_CMSIS_DAP && pid == PID_CMSIS_DAP)
        || product_lower.contains("cmsis-dap")
        || product_lower.contains("daplink")
    {
        return Ok(Some(WifiDevboardState::CmsisDap {
            vid,
            pid,
            bus,
            address,
        }));
    }

    if is_likely_esp32s2_firmware(device, &desc, vid, &product) {
        return Ok(Some(WifiDevboardState::Esp32S2Firmware {
            vid,
            pid,
            bus,
            address,
            product,
            manufacturer,
        }));
    }

    Ok(None)
}

fn read_usb_strings(
    device: &Device<GlobalContext>,
    desc: &DeviceDescriptor,
) -> (String, String) {
    let mut product = String::new();
    let mut manufacturer = String::new();

    if let Ok(handle) = device.open() {
        if let Ok(langs) = handle.read_languages(Duration::from_secs(1)) {
            if let Some(&lang0) = langs.get(0) {
                if let Ok(p) = handle.read_product_string(lang0, desc, Duration::from_secs(1)) {
                    product = p;
                }
                if let Ok(m) = handle.read_manufacturer_string(lang0, desc, Duration::from_secs(1)) {
                    manufacturer = m;
                }
            }
        }
    }

    (manufacturer, product)
}

fn is_likely_esp32s2_firmware(
    device: &Device<GlobalContext>,
    _desc: &DeviceDescriptor,
    vid: u16,
    product: &str,
) -> bool {
    let product_lower = product.to_lowercase();
    let looks_like_esp32s2_string =
        product_lower.contains("esp32") || product_lower.contains("s2");

    let mut has_vendor_specific_interface = false;
    let mut interface_count = 0u8;

    if let Ok(config) = device.config_descriptor(0) {
        for interface in config.interfaces() {
            for iface_desc in interface.descriptors() {
                interface_count = interface_count.saturating_add(1);
                if iface_desc.class_code() == 0xFF {
                    has_vendor_specific_interface = true;
                }
            }
        }
    }

    let vendor_match = vid == VID_ESPRESSIF;
    let string_or_vendor_match = vendor_match || looks_like_esp32s2_string;

    string_or_vendor_match && has_vendor_specific_interface && interface_count <= 4
}

fn detect_via_serial() -> Result<Vec<WifiDevboardState>, DetectionError> {
    let mut matches = Vec::new();
    let ports = serialport::available_ports()?;
    for port in ports {
        if let Some(serial_info) = is_candidate_serial_port(&port) {
            let (vid, pid, product, manufacturer) = usb_info_from_sysfs(&serial_info.sysfs_path);

            let product_lower = product
                .as_deref()
                .unwrap_or("")
                .to_lowercase();

            let looks_like_esp32 = product_lower.contains("esp32") || product_lower.contains("s2");
            let looks_like_cmsis = product_lower.contains("cmsis-dap");

            let vid_match = matches_esp_vid(vid);
            let any_match = vid_match || looks_like_esp32 || looks_like_cmsis;

            if any_match {
                matches.push(WifiDevboardState::SerialOnly {
                    port_name: serial_info.port_name,
                    sysfs_path: serial_info.sysfs_path,
                    vid,
                    pid,
                    product,
                    manufacturer,
                });
            }
        }
    }
    Ok(matches)
}

fn matches_esp_vid(vid: Option<u16>) -> bool {
    matches!(vid, Some(v) if v == VID_ESPRESSIF)
}

struct SerialPortSysInfo {
    port_name: String,
    sysfs_path: PathBuf,
}

fn is_candidate_serial_port(port: &SerialPortInfo) -> Option<SerialPortSysInfo> {
    match &port.port_type {
        SerialPortType::UsbPort(_usb) => {
            let sysfs = serial_sysfs_path(&port.port_name)?;
            Some(SerialPortSysInfo {
                port_name: port.port_name.clone(),
                sysfs_path: sysfs,
            })
        }
        _ => None,
    }
}

fn serial_sysfs_path(port_name: &str) -> Option<PathBuf> {
    let class_entry = PathBuf::from("/sys/class/tty").join(port_name);
    let link = fs::read_link(&class_entry).unwrap_or_else(|_| PathBuf::from(""));
    if link.as_os_str().is_empty() {
        return Some(class_entry);
    }

    let base = class_entry.parent().unwrap_or(&class_entry).to_path_buf();
    let resolved = if link.is_absolute() {
        link
    } else {
        base.join(link)
    };
    Some(resolved)
}

fn usb_info_from_sysfs(start: &Path) -> (Option<u16>, Option<u16>, Option<String>, Option<String>) {
    let mut path = start.to_path_buf();
    for _ in 0..10 {
        let id_vendor = path.join("idVendor");
        let id_product = path.join("idProduct");
        let prod = path.join("product");
        let mfg = path.join("manufacturer");

        let vid = read_hex(&id_vendor);
        let pid = read_hex(&id_product);
        let product = read_string(&prod);
        let manufacturer = read_string(&mfg);

        if vid.is_some() || pid.is_some() || product.is_some() || manufacturer.is_some() {
            return (vid, pid, product, manufacturer);
        }

        if !path.pop() {
            break;
        }
    }
    (None, None, None, None)
}

fn read_hex(path: &Path) -> Option<u16> {
    let data = fs::read_to_string(path).ok()?;
    let s = data.trim();
    if s.is_empty() {
        return None;
    }
    u16::from_str_radix(s, 16).ok()
}

fn read_string(path: &Path) -> Option<String> {
    let data = fs::read_to_string(path).ok()?;
    let s = data.trim();
    if s.is_empty() {
        None
    } else {
        Some(s.to_string())
    }
}

fn detect_ghost_usb() -> Result<Option<WifiDevboardState>, DetectionError> {
    let usb_bus = PathBuf::from("/sys/bus/usb/devices");

    if !usb_bus.exists() {
        return Ok(None);
    }

    for entry in fs::read_dir(&usb_bus)? {
        let entry = entry?;
        let path = entry.path();
        if !path.is_dir() {
            continue;
        }

        let id_vendor = path.join("idVendor");
        let id_product = path.join("idProduct");
        let descriptors = path.join("descriptors");
        let config = path.join("bConfigurationValue");

        let has_vendor = id_vendor.exists();
        let has_product = id_product.exists();
        let has_desc = descriptors.exists();
        let has_config = config.exists();

        if (has_desc || has_config) && (!has_vendor || !has_product) {
            return Ok(Some(WifiDevboardState::GhostUsb { sysfs_path: path }));
        }
    }

    Ok(None)
}
