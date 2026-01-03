use crate::crypto::TuyaCipher;
use crate::error::Result;
use crate::protocol::{CommandType, NO_PROTOCOL_HEADER_CMDS, TuyaProtocol, Version};
use serde_json::Value;

pub struct ProtocolV33;

impl ProtocolV33 {
    fn add_protocol_header(&self, payload: &[u8]) -> Vec<u8> {
        let mut header = Version::V3_3.as_bytes().to_vec();
        header.extend_from_slice(&[0u8; 12]);
        header.extend_from_slice(payload);
        header
    }
}

impl TuyaProtocol for ProtocolV33 {
    fn version(&self) -> Version {
        Version::V3_3
    }

    fn get_effective_command(&self, command: CommandType) -> u32 {
        command as u32
    }

    fn generate_payload(
        &self,
        device_id: &str,
        _command: CommandType,
        data: Option<Value>,
        cid: Option<&str>,
        t: u64,
    ) -> Result<(u32, Value)> {
        let mut payload = serde_json::Map::new();
        payload.insert("gwId".into(), device_id.into());
        payload.insert("devId".into(), cid.unwrap_or(device_id).into());
        payload.insert("uid".into(), device_id.into());
        payload.insert("t".into(), t.to_string().into());
        if let Some(d) = data {
            payload.insert("dps".into(), d);
        }
        Ok((self.get_effective_command(_command), Value::Object(payload)))
    }

    fn pack_payload(&self, payload: &[u8], cmd: u32, cipher: &TuyaCipher) -> Result<Vec<u8>> {
        let mut packed = cipher.encrypt(payload, false, None, None, true)?;
        if !NO_PROTOCOL_HEADER_CMDS.contains(&cmd) {
            packed = self.add_protocol_header(&packed);
        }
        Ok(packed)
    }

    fn decrypt_payload(&self, mut payload: Vec<u8>, cipher: &TuyaCipher) -> Result<Vec<u8>> {
        if payload.len() >= 15 && &payload[..3] == Version::V3_3.as_bytes() {
            payload.drain(..15);
        }
        if !payload.is_empty() {
            if let Ok(decrypted) = cipher.decrypt(&payload, false, None, None, None) {
                let mut d = decrypted;
                if d.len() >= 15 && &d[..3] == Version::V3_3.as_bytes() {
                    d.drain(..15);
                }
                return Ok(d);
            }
        }
        Ok(payload)
    }

    fn has_version_header(&self, payload: &[u8]) -> bool {
        payload.len() >= 15 && &payload[..3] == Version::V3_3.as_bytes()
    }
}
