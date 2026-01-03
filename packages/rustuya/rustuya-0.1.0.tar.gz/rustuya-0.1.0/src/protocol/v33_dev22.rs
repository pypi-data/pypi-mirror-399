use crate::crypto::TuyaCipher;
use crate::error::Result;
use crate::protocol::{CommandType, TuyaProtocol, Version};
use serde_json::Value;

pub struct ProtocolV33Dev22;

impl TuyaProtocol for ProtocolV33Dev22 {
    fn version(&self) -> Version {
        Version::V3_3
    }

    fn get_effective_command(&self, command: CommandType) -> u32 {
        match command {
            CommandType::DpQuery => CommandType::ControlNew as u32,
            cmd => cmd as u32,
        }
    }

    fn generate_payload(
        &self,
        device_id: &str,
        command: CommandType,
        data: Option<Value>,
        cid: Option<&str>,
        t: u64,
    ) -> Result<(u32, Value)> {
        let cmd_to_send = self.get_effective_command(command);
        let mut payload = serde_json::Map::new();
        payload.insert("gwId".into(), device_id.into());
        payload.insert("devId".into(), cid.unwrap_or(device_id).into());
        payload.insert("uid".into(), device_id.into());
        payload.insert("t".into(), t.to_string().into());

        let final_data = if cmd_to_send == CommandType::ControlNew as u32 && data.is_none() {
            Some(serde_json::json!({"1": null}))
        } else {
            data
        };

        if let Some(d) = final_data {
            payload.insert("dps".into(), d);
        }
        Ok((cmd_to_send, Value::Object(payload)))
    }

    fn pack_payload(&self, payload: &[u8], _cmd: u32, cipher: &TuyaCipher) -> Result<Vec<u8>> {
        cipher.encrypt(payload, false, None, None, true)
    }

    fn decrypt_payload(&self, payload: Vec<u8>, cipher: &TuyaCipher) -> Result<Vec<u8>> {
        cipher.decrypt(&payload, false, None, None, None)
    }

    fn has_version_header(&self, payload: &[u8]) -> bool {
        !payload.len().is_multiple_of(16)
    }
}
